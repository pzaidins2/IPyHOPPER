#!/usr/bin/env python
"""
File Description: File used for definition of IPyHOP Class.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from __future__ import division, print_function

from copy import deepcopy
from itertools import count
from typing import Hashable, Iterator, List, Optional, Tuple, Union, cast

from networkx import DiGraph, descendants, dfs_preorder_nodes, is_tree

from ipyhop.actions import Actions
from ipyhop.chronicle import ChronicleInterface, ReferenceChronicle, RestorationTuple, ValueChronicle
from ipyhop.methods import Methods
from ipyhop.mulitgoal import MultiGoal
from ipyhop.state import State
from ipyhop.temporal import TemporalNetwork, TemporalRestorationTuple
from ipyhop.temporal_actions import TemporalActionCall, TemporalActionOutput, TemporalActions, TemporalGoal, \
    TemporalSingletonAction
from ipyhop.temporal_methods import TemporalMethodOutput, TemporalMethods

CI = ChronicleInterface()
# ******************************************    Class Declaration Start     ****************************************** #
class IPyHOP(object):
    """
    IPyHOP uses GTN methods to decompose tasks/goals into smaller and smaller subtasks/subgoals, until it finds
    tasks/goals that correspond directly to actions.

    *   planner = IPyHOP(methods, actions) tells IPyHOP to create a IPyHOP planner object.
        To plan using the planner, you should use planner.plan(state, task_list).
    """

    def __init__(self, methods: Methods, actions: Actions):
        """
        IPyHOP Constructor.

        :param methods: An instance of Methods class containing the collection of methods in the planning domain.
        :param actions: An instance of Actions class containing the collection of actions in the planning domain.
        """
        self.methods = methods
        self.actions = actions
        self.state = None
        self.task_list = []
        self.sol_plan = []
        self.sol_tree = DiGraph()
        self.blacklist = set()
        self.iterations = None

        self._verbose = 0

        # temporal planning additions
        # temporal planning can't use tree dfs ordering
        # if temporal, when node is visited add to the list
        # during back tracking, use the list to determine which node to go to
        # root has node id 0 and is first element of visitation list
        self.node_id_visit_order: List[ int ] = [ 0 ]

        """ 
        Planning cycle
        when selecting goals or time points do so using semisort on temporal network
        1) take input list of temporal goals, add new time points to unordered time points
        2) add t_s and t_e as the first and last time point in the plan
        3) current time, t_now, is set to t_s, let any time point t_now or later be pending time points
        4) if any singleton action exists at a pending time point, resolve it
        5) if any action starting at a pending time point exists, reduce to singleton actions
        6) if any goal has not been expanded, decompose prioritizing goals by 
        7) if any time point is unordered, add to ordering as == to t_now (said time point is now pending)
        8) if any time point is unordered, add to ordering as < to t_now, then set that time point to t_now
        9) if none of the above are possible, back track to previous node; if no previous node planning as failed
        10) if there are no open goals, actions, or singleton actions terminate with success
        
        """

    _t_type = List[Tuple[str]]
    _m_type = Optional[Methods]
    _op_type = Optional[Actions]
    _p_type = Union[List[Tuple[str]], bool]

    # ******************************        Class Method Declaration        ****************************************** #
    def plan(self, state: State, task_list: _t_type, methods: _m_type = None, actions: _op_type = None,
            verbose: Optional[ int ] = 0, value_chronicle: Optional[ ValueChronicle ] = None
    ) -> _p_type:
        """
        IPyHOP.plan(state_1, tasks) tells IPyHOP to find a plan for accomplishing the task_list (a list of tasks)
        *tasks*, starting from an initial state *state_1*, using whatever methods and actions IPyHOP was constructed
        with.

        Optionally, instances of Methods class and/or Actions class can be passed into methods and actions
        respectively to replace the methods and actions IPyHOP uses for solving the planning problem.

        Additionally, you can add an optional argument called 'verbose' that tells IPyHOP how much debugging printout
        it should provide:
            * if verbose = 0 (the default), IPyHOP returns the solution but prints nothing;
            * if verbose = 1, it prints the initial parameters and the answer;
            * if verbose = 2, it also prints a message on each iteration;
            * if verbose = 3, it also prints info about what it's computing.

        :param state: An instance of State class containing the collection of variable bindings representing
            the current/initial state in the planning problem.
        :param task_list: A list of tasks that need to be accomplished in the planning problem.
        :param methods: [Optional] An instance of Methods class containing the collection of methods in the
            planning domain.
        :param actions: [Optional] An instance of Actions class containing the collection of actions in the
            planning domain.
        :param verbose: [Optional] An integer specifying the level of verbosity for IPyHOP.
        :return: A list containing the solution plan.
        """

        # handle temporal flagging
        self.is_temporal = False
        how_many_temporal = sum(
                [
                    isinstance( actions, TemporalActions ), isinstance( methods, TemporalMethods ),
                    value_chronicle is not None,
                ],
        )
        self.value_chronicle = value_chronicle
        if how_many_temporal == 3:
            self.is_temporal = True

        # catch case of mixed temporal and atemporal
        elif how_many_temporal > 0 and how_many_temporal < 3:
            raise (TypeError(
                    "Temporal methods, temporal actions, and the value chronicle parameter cannot be used separately",
            ))
        self.state = state.copy()
        self.task_list = deepcopy(task_list)
        self.methods = self.methods if methods is None else methods
        self.actions = self.actions if actions is None else actions
        self._verbose = verbose

        if self._verbose > 0:
            run_info = '**IPyHOP, verbose = {verbosity}: **\n\tstate = {state}\n\ttasks/goals = {task_list}.'
            print(run_info.format(verbosity=self._verbose, state=self.state.__name__, task_list=task_list))

        self.sol_plan = []
        self.sol_tree = DiGraph()

        self.node_id_visit_order: List[ int ] = [ 0 ]
        _id = 0
        parent_node_id = _id
        self.sol_tree.add_node(_id, info=('root',), type='D', status='NA')
        _id = self._add_nodes_and_edges(_id, _id, self.task_list)


        self.iterations = self._planning(_id, parent_node_id)
        assert is_tree(self.sol_tree), "Error! Solution graph is not a tree."

        # Store the planning solution as a list of actions to be executed.
        for node_id in dfs_preorder_nodes(self.sol_tree, source=0):
            if self.sol_tree.nodes[node_id]['type'] == 'A':
                self.sol_plan.append(self.sol_tree.nodes[node_id]['info'])

        if not self.is_temporal:
            assert self.node_id_visit_order == [ *dfs_preorder_nodes( self.sol_tree, source=0 ) ]

        return self.sol_plan

    # ******************************        Class Method Declaration        ****************************************** #
    # returns the node id of the next element to be expanded
    # for atemporal planning this is done in dfs order
    # for temporal planning, all open nodes in the frontier are candidates
    def select_next_open_node(
            self, _iter: int, parent_node_id, reference_chronicle: ReferenceChronicle,
            value_chronicle: Optional[ ValueChronicle ],
    ) -> Iterator[ int ]:
        # CHANGE NEEDED: should select from current nodes based on temporal ordering
        # Goals have single time point
        # Actions need some way to identify start time point
        # Singular actions come with time point

        # Get the first Open node from the immediate successors of parent node. (using BFS)
        # NEEDS CHANGES
        # time point ordering (new node type?, method that adds time point to ordering, semisort selection)
        # time advancing (new node type?, method that changes t_now and adds temporal constraint for immediate
        # prior time point in ordering, is there a principled way to do this?)
        # change how nodes are selected for expansion
        # change back track to restore temporal network *
        curr_node_id = None
        sol_tree = self.sol_tree
        # select next node to attempt
        if self.is_temporal and value_chronicle is not None:
            # anchoring time point: the time point associated with a temporal goal, the starting time point in the
            # temporal action parameters, the time point which a temporal singleton action occurs
            # for a node to be considered:
            # 1) must be open
            # 2) must have no children (on the frontier)
            # 3) the anchoring time point must be no less than t_now
            # 4) the anchoring time point must not be required to occur after a time point not in t_ordered

            # filter out nodes not meeting (1) and (2)
            open_frontier_node_tup_filter: Iterator[ Tuple[ Hashable, int ] ] = filter(
                    lambda x: x[ 1 ] == 0 and sol_tree.nodes[ x[ 0 ] ][ "status" ] in { "O", "M" }, sol_tree.out_degree,
            )
            open_frontier_node_map: Iterator[ int ] = map( lambda x: x[ 0 ], open_frontier_node_tup_filter )

            # extract anchoring time point
            # temporal singleton actions have this has the 0 index element of tuple
            # temporal actions have this as the 2 index element of tuple
            # temporal goals have this as the 0 index element of tuple

            # track node id, anchoring time point, type
            node_id_anchor_time_point_tup_lst: List[ Tuple[ Hashable, int, int ] ] = [ ]
            for node_id in open_frontier_node_map:
                node = sol_tree.nodes[ node_id ]
                node_type: str = node[ "type" ]
                node_info = node[ "info" ]
                node_type_enum: int = -1
                # temporal action
                if node_type == "A":
                    anchor_idx = 2
                    node_type_enum = 1
                # temporal goal
                elif node_type == "G":
                    anchor_idx = 0
                    node_type_enum = 2
                # temporal singleton action
                elif node_type == "TSA":
                    anchor_idx = 0
                    node_type_enum = 0
                else:
                    raise (ValueError( "Invalid node type for temporal planning: " + node_type ))
                node_id_anchor_time_point_tup_lst.append( (node_id, node_info[ anchor_idx ], node_type_enum) )

            # filter nodes that do not meet (3) or (4)
            stn: TemporalNetwork = value_chronicle.temporal_network
            # potentially from ordered time points
            t_ordered: List[ int ] = value_chronicle.t_ordered[ :(reference_chronicle.t_ordered + 1) ]
            t_unordered: List[ int ] = value_chronicle.t_unordered[ :(reference_chronicle.t_ordered + 1) ]
            t_now: int = value_chronicle.t_now
            t_now_idx: int = t_ordered.index( t_now )
            potential_time_points: List[ int ] = t_ordered[ t_now_idx: ]
            # potentially from unordered time points
            potential_time_points += stn.get_potential_next_time_points( t_unordered )
            # remove nodes that do not have these time points as anchors
            node_id_anchor_time_point_tup_lst = [
                *filter( lambda x: x[ 1 ] in potential_time_points, node_id_anchor_time_point_tup_lst ),
            ]
            # sort TSA < A < G
            node_id_anchor_time_point_tup_lst.sort( key=lambda x: x[ 2 ] )
            for node_id_anchor_time_point_tup in node_id_anchor_time_point_tup_lst:
                if self._verbose > 1:
                    print(
                            'Iteration {}, Refining node {}.'.format(
                                    _iter, repr( sol_tree.nodes[ node_id_anchor_time_point_tup[ 1 ] ][ 'info' ] ),
                            ),
                    )
                yield cast( int, node_id_anchor_time_point_tup[ 0 ] )


        # expand nodes in dfs order for atemporal planning
        else:
            print( "atemporal" )
            for node_id in dfs_preorder_nodes( sol_tree, 0 ):

                if sol_tree.nodes[ node_id ][ 'status' ] == 'O':

                    curr_node_id = cast( int, node_id )
                    if self._verbose > 1:
                        print(
                                'Iteration {}, Refining node {}.'.format(
                                        _iter, repr( sol_tree.nodes[ node_id ][ 'info' ] ),
                                ),
                        )
                    break
            yield curr_node_id

    # ******************************        Class Method Declaration        ****************************************** #
    def _planning(self, _id, parent_node_id):
        is_temporal = self.is_temporal
        value_chronicle = self.value_chronicle
        select_next_open_node = self.select_next_open_node
        sol_tree = self.sol_tree
        node_id_visit_order = self.node_id_visit_order
        _iter = 0
        gen_inactive = True
        curr_node_id_iter = count
        while True:
            print( parent_node_id )
            print( gen_inactive )
            # increment iteration count
            _iter += 1
            #

            curr_node_id_iter = select_next_open_node( _iter, parent_node_id, self.state, value_chronicle )
            print( "past gen" )
            # pull from generator

            curr_node_id = next( curr_node_id_iter )
            print( "used gen node id: " + str( curr_node_id ) )
            # empty generator back track
            print( "gen empty" )
            gen_inactive = True
            # If Open node wasn't found from the immediate successors
            if curr_node_id is None:
                # Set the parent_node_id as predecessor of parent_node_id if available.
                try:
                    parent_node_id = next( sol_tree.predecessors( parent_node_id ) )
                    if self._verbose > 2:
                        print(
                                'Iteration {}, Parent node modified to {}.'.format(
                                        _iter, repr( sol_tree.nodes[ parent_node_id ][ 'info' ] ),
                                ),
                        )
                    continue
                except StopIteration:  # if the parent_node_id has no predecessors (i.e. it is root) end refinement.
                    if self._verbose > 2:
                        print( 'Iteration {}, Planning Complete.'.format( _iter ) )
                    break

            # Open node was found in the subgraph. Refine the node.
            curr_node = self.sol_tree.nodes[ curr_node_id ]
            if 'state' in curr_node:
                # If curr_node already has a value for state, it means that the algorithm backtracked to this node.
                if curr_node[ 'state' ]:
                    # Modify the current state as the saved state at that node.
                    self.state.update( curr_node[ 'state' ].copy() )
                # If curr_node doesn't have value for state, it means that the node is visited for the first time.
                else:
                    # Save the current state in the node.
                    curr_node[ 'state' ] = self.state.copy()
            curr_node_info = curr_node[ 'info' ]

            # If current node is a Task
            if curr_node[ 'type' ] == 'T':
                subtasks = None
                # If methods are available for refining the task, use them.
                for method in curr_node[ 'available_methods' ]:
                    curr_node[ 'selected_method' ] = method
                    subtasks = method( self.state, *curr_node_info[ 1: ] )
                    if subtasks is not None:
                        curr_node[ 'status' ] = 'C'
                        node_id_visit_order.append( curr_node_id )
                        gen_inactive = True
                        _id = self._add_nodes_and_edges( _id, curr_node_id, subtasks )
                        parent_node_id = curr_node_id
                        if self._verbose > 2:
                            print(
                                    'Iteration {}, Task {} successfully refined'.format(
                                            _iter,
                                            repr( curr_node_info ),
                                    ),
                            )
                            print(
                                    'Iteration {}, Parent node modified to {}.'.format(
                                            _iter, repr( self.sol_tree.nodes[ parent_node_id ][ 'info' ] ),
                                    ),
                            )
                        break
                if subtasks is None:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        print( 'Iteration {}, Task {} refinement failed'.format( _iter, repr( curr_node_info ) ) )
                        print(
                                'Iteration {}, Backtracking to {}.'.format(
                                        _iter, repr( self.sol_tree.nodes[ curr_node_id ][ 'info' ] ),
                                ),
                        )


            # If current node is an Action
            elif curr_node[ 'type' ] == 'A':
                new_state = None
                # If the Action is not blacklisted
                if curr_node_info not in self.blacklist:
                    # handle temporal actions having RestorationTuple Output
                    if is_temporal:
                        temporal_action_output: TemporalActionOutput = curr_node[ 'action' ](
                                self.state.copy(), value_chronicle, *curr_node_info[ 2: ],
                        )
                        if temporal_action_output is not None:
                            restoration_tup: RestorationTuple = temporal_action_output[ 0 ]
                            temporal_singleton_action_lst: List[ TemporalSingletonAction ] = temporal_action_output[
                                1 ]
                            reference_chronicle: ReferenceChronicle = restoration_tup[ 0 ]
                            temporal_restoration_tup: TemporalRestorationTuple = restoration_tup[ 1 ]
                            # this will handle object change and persistence rollback
                            new_state = reference_chronicle
                            # these will handle temporal network rollback
                            curr_node[ "temporal_restoration_tup" ] = temporal_restoration_tup
                            curr_node[ "temporal_singleton_action_lst" ] = temporal_singleton_action_lst
                        else:
                            new_state = None
                    else:
                        new_state = curr_node[ 'action' ]( self.state.copy(), *curr_node_info[ 1: ] )
                    # If Action was successful, update the state.
                    if new_state is not None:
                        curr_node[ 'status' ] = 'C'
                        node_id_visit_order.append( curr_node_id )
                        gen_inactive = True
                        self.state.update( new_state )
                        if self._verbose > 2:
                            print( 'Iteration {}, Action {} successful.'.format( _iter, repr( curr_node_info ) ) )
                if new_state is None:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        print( 'Iteration {}, Action {} failed.'.format( _iter, repr( curr_node_info ) ) )
                        print(
                                'Iteration {}, Backtracking to {}.'.format(
                                        _iter, repr( self.sol_tree.nodes[ curr_node_id ][ 'info' ] ),
                                ),
                        )

            # If current node is a Goal
            elif curr_node[ 'type' ] == 'G':
                subgoals = None

                # Skip goal refinement if already achieved
                # if temporal, check that the state as of t_now would meet this goal
                goal_done = False
                if is_temporal:
                    temporal_goal = curr_node_info
                    if value_chronicle is not None and CI.verify_object_assertion(
                            self.state.copy(),
                            value_chronicle, temporal_goal,
                    ):
                        goal_done = True
                else:
                    state_var, arg, desired_val = curr_node_info
                    if self.state.__dict__[ state_var ][ arg ] == desired_val:
                        goal_done = True
                if goal_done:
                    curr_node[ 'status' ] = 'C'
                    node_id_visit_order.append( curr_node_id )
                    gen_inactive = True
                    subgoals = [ ]
                    if self._verbose > 2:
                        print( 'Iteration {}, Goal {} already achieved'.format( _iter, repr( curr_node_info ) ) )
                else:
                    # If methods are available for refining the goal, use them.
                    for method in curr_node[ 'available_methods' ]:
                        curr_node[ 'selected_method' ] = method
                        subgoals = None
                        # adjust for temporal goal output and save info for back tracking
                        if is_temporal:
                            temporal_method_output: TemporalMethodOutput = method(
                                    self.state.copy(), value_chronicle, *curr_node_info[ 2: ],
                            )
                            if temporal_method_output is not None:
                                restoration_tup: RestorationTuple = temporal_method_output[ 0 ]
                                reference_chronicle: ReferenceChronicle = restoration_tup[ 0 ]
                                temporal_restoration_tup: TemporalRestorationTuple = restoration_tup[ 1 ]
                                # these will handle temporal network rollback
                                curr_node[ "temporal_restoration_tup" ] = temporal_restoration_tup
                                # this will handle object change and persistence rollback
                                if reference_chronicle is not None:
                                    curr_node[ 'status' ] = 'C'
                                    node_id_visit_order.append( curr_node_id )
                                    gen_inactive = True
                                    self.state.update( reference_chronicle )
                                    subgoals: List[ Union[ TemporalGoal, TemporalActionCall ] ] = \
                                        temporal_method_output[
                                            1 ]
                        else:
                            subgoals = method( self.state, *curr_node_info[ 1: ] )
                        if subgoals is not None:
                            curr_node[ 'status' ] = 'C'
                            node_id_visit_order.append( curr_node_id )
                            gen_inactive = True
                            _id = self._add_nodes_and_edges( _id, curr_node_id, subgoals )  # type: ignore
                            parent_node_id = curr_node_id
                            if self._verbose > 2:
                                print(
                                        'Iteration {}, Goal {} successfully refined'.format(
                                                _iter, repr( curr_node_info ),
                                        ),
                                )
                                print(
                                        'Iteration {}, Parent node modified to {}.'.format(
                                                _iter, repr( self.sol_tree.nodes[ parent_node_id ][ 'info' ] ),
                                        ),
                                )
                            break
                if subgoals is None:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        print( 'Iteration {}, Goal {} refinement failed'.format( _iter, repr( curr_node_info ) ) )
                        print(
                                'Iteration {}, Backtracking to {}.'.format(
                                        _iter, repr( self.sol_tree.nodes[ curr_node_id ][ 'info' ] ),
                                ),
                        )

            # If current node is a MultiGoal
            elif curr_node[ 'type' ] == 'M':
                subgoals = None
                unachieved_goals = self._goals_not_achieved( curr_node_id )
                if not unachieved_goals:
                    curr_node[ 'status' ] = "C"
                    gen_inactive = True
                    subgoals = [ ]
                    if self._verbose > 2:
                        print( 'Iteration {}, MultiGoal {} already achieved'.format( _iter, repr( curr_node_info ) ) )
                else:
                    # If methods are available for refining the goal, use them.
                    for method in curr_node[ 'available_methods' ]:
                        curr_node[ 'selected_method' ] = method
                        subgoals = method( self.state, curr_node_info )
                        if subgoals is not None:
                            curr_node[ 'status' ] = 'C'
                            node_id_visit_order.append( curr_node_id )
                            gen_inactive = True
                            _id = self._add_nodes_and_edges( _id, curr_node_id, subgoals )
                            parent_node_id = curr_node_id
                            if self._verbose > 2:
                                print(
                                        'Iteration {}, MultiGoal {} successfully refined'.format(
                                                _iter, repr( curr_node_info ),
                                        ),
                                )
                                print(
                                        'Iteration {}, Parent node modified to {}.'.format(
                                                _iter, repr( self.sol_tree.nodes[ parent_node_id ][ 'info' ] ),
                                        ),
                                )
                            break
                if subgoals is None:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        print(
                                'Iteration {}, MultiGoal {} refinement failed'.format( _iter, repr( curr_node_info ) ),
                        )
                        print(
                                'Iteration {}, Backtracking to {}.'.format(
                                        _iter, repr( self.sol_tree.nodes[ curr_node_id ][ 'info' ] ),
                                ),
                        )

            elif curr_node[ 'type' ] == 'VG':
                state_var, arg, desired_val = self.sol_tree.nodes[ parent_node_id ][ 'info' ]
                if self.state.__dict__[ state_var ][ arg ] == desired_val:
                    curr_node[ 'status' ] = "C"
                    gen_inactive = True
                else:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        curr_node_info = self.sol_tree.nodes[ curr_node_id ][ 'info' ]
                        print( 'Iteration {}, Goal {} Verification failed.'.format( _iter, repr( curr_node_info ) ) )
                        print( 'Iteration {}, Backtracking to {}.'.format( _iter, repr( curr_node_info ) ) )

            elif curr_node[ 'type' ] == 'VM':
                unachieved_goals = self._goals_not_achieved( parent_node_id )
                if not unachieved_goals:
                    curr_node[ 'status' ] = "C"
                    gen_inactive = True
                else:
                    parent_node_id, curr_node_id = self._backtrack( parent_node_id, curr_node_id )
                    if self._verbose > 2:
                        curr_node_info = self.sol_tree.nodes[ curr_node_id ][ 'info' ]
                        print(
                                'Iteration {}, MultiGoal {} Verification failed.'.format(
                                        _iter,
                                        repr( curr_node_info ),
                                ),
                        )
                        print( 'Iteration {}, Backtracking to {}.'.format( _iter, repr( curr_node_info ) ) )

        return _iter

    # ******************************        Class Method Declaration        ****************************************** #
    def replan(self, state: State, fail_node_id: int, verbose: Optional[int] = 0) -> _p_type:
        """
        IPyHOP.replan(state_1, fail_node_id) tells IPyHOP to re-plan the solution tree given that the node with id
        *fail_node_id* has failed. The planning should be accomplished from a new initial state *state_1*,
        using whatever methods and actions IPyHOP was constructed

        Additionally, you can add an optional argument called 'verbose' that tells IPyHOP how much debugging printout
        it should provide:
            * if verbose = 0 (the default), IPyHOP returns the solution but prints nothing;
            * if verbose = 1, it prints the initial parameters and the answer;
            * if verbose = 2, it also prints a message on each iteration;
            * if verbose = 3, it also prints info about what it's computing.

        :param state: An instance of State class containing the collection of variable bindings representing
            the current/initial state in the planning problem.
        :param fail_node_id: The id of the failure node.
        :param verbose: [Optional] An integer specifying the level of verbosity for IPyHOP.
        :return: A list containing the solution plan.
        """

        self.state = state.copy()

        max_id = self._post_failure_modify(fail_node_id)
        parent_node_id, curr_node_id = self._backtrack(list(self.sol_tree.predecessors(fail_node_id))[0], fail_node_id)

        self.iterations = self._planning(max_id, parent_node_id)
        assert is_tree(self.sol_tree), "Error! Solution graph is not a tree."

        self.sol_plan = []
        # Store the planning solution as a list of actions to be executed.
        for node_id in dfs_preorder_nodes(self.sol_tree, source=0):
            if self.sol_tree.nodes[node_id]['type'] == 'A':
                if self.sol_tree.nodes[node_id]['tag'] == 'new':
                    self.sol_plan.append(self.sol_tree.nodes[node_id]['info'])

        return self.sol_plan

    # ******************************        Class Method Declaration        ****************************************** #
    def _add_nodes_and_edges(self, _id: int, parent_node_id: int, children_node_info_list: List[Tuple[str]]):
        for child_node_info in children_node_info_list:
            _id += 1
            if isinstance(child_node_info, MultiGoal):  # equivalent to type(child_node_info) == MultiGoal
                relevant_methods = self.methods.multigoal_method_dict[child_node_info.goal_tag]
                self.sol_tree.add_node(_id, info=child_node_info, type='M', status='O', state=None,
                                       selected_method=None, available_methods=iter(relevant_methods),
                                       methods=relevant_methods, tag='new')
                self.sol_tree.add_edge(parent_node_id, _id)
            elif child_node_info[0] in self.methods.task_method_dict:
                relevant_methods = self.methods.task_method_dict[child_node_info[0]]
                self.sol_tree.add_node(_id, info=child_node_info, type='T', status='O', state=None,
                                       selected_method=None, available_methods=iter(relevant_methods),
                                       methods=relevant_methods, tag='new')
                self.sol_tree.add_edge(parent_node_id, _id)

            elif child_node_info[0] in self.actions.action_dict:
                action = self.actions.action_dict[child_node_info[0]]
                self.sol_tree.add_node(_id, info=child_node_info, type='A', status='O', action=action, tag='new')
                self.sol_tree.add_edge(parent_node_id, _id)
                # if temporal, make spot for temporal restoration tuple
                # this will be used to restore temporal network during back tracking
                if self.is_temporal:
                    self.sol_tree.nodes[ _id ][ "temporal_restoration_tuple" ]: Optional[
                        TemporalRestorationTuple ] = None
                    self.temporal_singleton_action_lst = Optional[ List[ TemporalSingletonAction ] ]

            elif child_node_info[0] in self.methods.goal_method_dict:
                relevant_methods = self.methods.goal_method_dict[child_node_info[0]]
                self.sol_tree.add_node(_id, info=child_node_info, type='G', status='O', state=None,
                                       selected_method=None, available_methods=iter(relevant_methods),
                                       methods=relevant_methods, tag='new')
                self.sol_tree.add_edge(parent_node_id, _id)
                # if temporal, make spot for temporal restoration tuple
                # this will be used to restore temporal network during back tracking
                if self.is_temporal:
                    self.sol_tree.nodes[ _id ][ "temporal_restoration_tuple" ]: Optional[
                        TemporalRestorationTuple ] = None
                    self.temporal_singleton_action_lst = Optional[ List[ TemporalSingletonAction ] ]

        if self.sol_tree.nodes[parent_node_id]['type'] == 'G':
            _id += 1
            self.sol_tree.add_node(_id, info='VerifyGoal', type='VG', status='O', tag='new')
            self.sol_tree.add_edge(parent_node_id, _id)
        elif self.sol_tree.nodes[parent_node_id]['type'] == 'M':
            _id += 1
            self.sol_tree.add_node(_id, info='VerifyMultiGoal', type='VM', status='O', tag='new')
            self.sol_tree.add_edge(parent_node_id, _id)

        return _id

    # ******************************        Class Method Declaration        ****************************************** #
    def _post_failure_modify(self, fail_node_id):

        rev_pre_ord_nodes = reversed(list(dfs_preorder_nodes(self.sol_tree, source=0)))

        for node_id in rev_pre_ord_nodes:

            c_node = self.sol_tree.nodes[node_id]
            c_node['status'] = 'O'

            if node_id == fail_node_id:
                break

            c_type = c_node['type']
            if c_type == 'T' or c_type == 'G' or c_type == 'M':
                c_node['state'] = None
                c_node['selected_method'] = None
                c_node['available_methods'] = iter(c_node['methods'])
                descendant_list = list(descendants(self.sol_tree, node_id))
                self.sol_tree.remove_nodes_from(descendant_list)

        max_id = -1
        for node_id in self.sol_tree.nodes:
            if node_id >= max_id:
                max_id = node_id + 1
            if 'state' in self.sol_tree.nodes[node_id]:
                if self.sol_tree.nodes[node_id]['status'] == 'C':
                    self.sol_tree.nodes[node_id]['state'] = self.state.copy()
                else:
                    self.sol_tree.nodes[node_id]['state'] = None
            if self.sol_tree.nodes[node_id]['status'] == 'C':
                self.sol_tree.nodes[node_id]['tag'] = 'old'

        return max_id

    # ******************************        Class Method Declaration        ****************************************** #
    def _backtrack(self, p_node_id: int, c_node_id: int):
        is_temporal = self.is_temporal
        value_chronicle = self.value_chronicle
        c_node = self.sol_tree.nodes[c_node_id]
        c_type = c_node['type']
        # object variables get rolled back with indices in reference chronicle
        # temporal network needs the temporal restoration tuple for reset
        temporal_restoration_tup = None
        if c_type == 'T' or c_type == 'G' or c_type == 'M':
            if is_temporal and value_chronicle is not None:
                temporal_restoration_tup: TemporalRestorationTuple = c_node[ 'temporal_restoration_tuple' ]
                value_chronicle.temporal_network.restore_graph(
                        *temporal_restoration_tup,
                )
                c_node[ 'temporal_restoration_tuple' ] = None
            c_node['state'] = None
            c_node['selected_method'] = None
            c_node['available_methods'] = iter(c_node['methods'])
        # NEEDS CHANGE
        # backtrack cannot use the dfs list for temporal planning
        # dealing with visitation order will change how this
        # needs to be written
        dfs_list = list(dfs_preorder_nodes(self.sol_tree, source=p_node_id))
        for node_id in reversed(dfs_list):
            node = self.sol_tree.nodes[node_id]
            if node['status'] == 'C':
                node['status'] = 'O'
                self.node_id_visit_order.pop()
                descendant_list = list(descendants(self.sol_tree, node_id))
                if descendant_list:
                    self.sol_tree.remove_nodes_from(descendant_list)
                    p_node_id = next(self.sol_tree.predecessors(node_id))
                    return p_node_id, node_id
                if 'state' in node:
                    node['state'] = None

        self.sol_tree.remove_nodes_from(list(descendants(self.sol_tree, 0)))
        return 0, 0

    # ******************************        Class Method Declaration        ****************************************** #
    def _goals_not_achieved(self, multigoal_node_id):
        multigoal = self.sol_tree.nodes[multigoal_node_id]['info']
        unachieved = {}
        for name in vars(multigoal):
            if name == '__name__' or name == 'goal_tag':
                continue
            for arg in vars(multigoal).get(name):
                val = vars(multigoal).get(name).get(arg)
                if val != vars(self.state).get(name).get(arg):
                    # want arg_value_pairs.name[arg] = val
                    if not unachieved.get(name):
                        unachieved.update({name: {}})
                    unachieved.get(name).update({arg: val})
        return unachieved

    # ******************************        Class Method Declaration        ****************************************** #
    def simulate(self, state: State, start_ind=0) -> List:
        """
        Simulates the generated plan on the given state

        :param state: An instance of State class containing the collection of variable bindings representing
            the current in the planning problem.
        :param start_ind: An integer specifying the index of the command in the generated plan to simulate from.
        :return: A list of states that the system transitions through during simulation of the plan.
        """
        state_list = [state.copy()]
        state_copy = state.copy()
        plan = self.sol_plan[start_ind:]
        for action in plan:
            self.actions.action_dict[action[0]](state_copy, *action[1:])
            state_list.append(state_copy.copy())
        return state_list

    # ******************************        Class Method Declaration        ****************************************** #
    def blacklist_command(self, command: Tuple):
        """
        Blacklists a provided command. Blacklisted commands will fail during planning.

        :param command: A tuple representing a command instance that should be blacklisted.
        """
        self.blacklist.add(command)


# ******************************************    Class Declaration End       ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for IPyHOP isn't implemented.")

"""
Author(s): Yash Bansod
Repository: https://github.com/YashBansod/IPyHOP
"""
