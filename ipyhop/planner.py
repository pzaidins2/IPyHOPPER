#!/usr/bin/env python
"""
File Description: File used for definition of IPyHOP Class.
"""

# ******************************************    Libraries to be imported    ****************************************** #

from __future__ import division, division, print_function, print_function

import keyword
import re
from copy import deepcopy
from typing import Dict, Hashable, Iterator, List, Optional, Tuple, Union, cast

from networkx import DiGraph, ancestors, bfs_successors, dfs_preorder_nodes, dfs_successors, is_tree, neighbors, \
    predecessor

from ipyhop.actions import Actions
from ipyhop.chronicle import ChronicleInterface, ReferenceChronicle, RestorationTuple, ValueChronicle
from ipyhop.methods import Methods
from ipyhop.mulitgoal import MultiGoal
from ipyhop.state import State
from ipyhop.temporal import TOCSpecTuple, TemporalNetwork, TemporalRestorationTuple
from ipyhop.temporal_actions import TemporalActionCall, TemporalActionOutput, TemporalGoal, \
    TemporalSingletonAction
from ipyhop.temporal_methods import TemporalMethodOutput

CI = ChronicleInterface()
default_separation_condition_tup = ("==", "<")
# ******************************************    Class Declaration Start     ****************************************** #
class IPyHOP(object):
    """
    IPyHOP uses HTN methods to decompose tasks into smaller and smaller subtasks, until it finds tasks that
    correspond directly to actions.

    *   planner = IPyHOP(methods, actions) tells IPyHOP to create a IPyHOP planner object.
        To plan using the planner, you should use planner.plan(state, task_list).
    """

    def __init__(self, methods: Methods, actions: Actions, verbose: Optional[int]=0 ):
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

        self.max_node_id = None

        self._verbose = 3  # temp change

        self.id_counter = 0
        self.node_expansions = 0
        self.depth_step_size=None
        self.max_depth = None

        # when True will perform branch cycle checking, when False will not
        self.branch_cycle_check_flag = False


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

    _t_type = List[ Tuple ]
    _m_type = Optional[Methods]
    _op_type = Optional[Actions]
    _p_type = Union[List[Tuple[str]], bool]
    # group 0: node id
    # group 1: task/action string
    # group 2: child node ids
    re_shop_top_level = re.compile( r"^([0-9]+?)\s\((.+?)\)(\s->\s)?(.*?)$",
                                    flags=re.MULTILINE | re.DOTALL )
    # group 5
    re_task = re.compile( r"(.+?)(?=\s|$)",
                          flags=re.MULTILINE | re.DOTALL )



    # ******************************        Class Method Declaration        ****************************************** #
    def plan(self, state: State, task_list: _t_type, methods: _m_type = None, actions: _op_type = None,
             value_chronicle: Optional[ ValueChronicle ] = None, verbose: Optional[int] = None, initial_max_depth: Optional[int]=None,
             depth_step_size: Optional[int]=None) -> Union[_p_type,bool]:

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
        :return:
        """

        # handle temporal flagging
        self.is_temporal = False
        self.methods = self.methods if methods is None else methods
        self.actions = self.actions if actions is None else actions
        how_many_temporal = sum(
                [
                    self.actions.is_temporal, self.methods.is_temporal,
                    value_chronicle is not None,
                ],
        )
        print(
                [
                    self.actions.is_temporal, self.methods.is_temporal,
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

        if verbose is None:
            verbose = self._verbose
        self.depth_step_size=depth_step_size
        self.max_depth=initial_max_depth if initial_max_depth is not None else depth_step_size
        self.iterations = 0

        if verbose > 0:
            run_info = '**IPyHOP, verbose = {verbosity}: **\n\tstate = {state}\n\ttasks/goals = {task_list}.'
            print(run_info.format(verbosity=verbose, state=self.state.__name__, task_list=task_list))

        self.sol_plan = []
        self.sol_tree = DiGraph()

        self.node_id_visit_order: List[ int ] = [ 0 ]
        _id = 0
        self.max_node_id = _id
        parent_node_id = _id
        self.sol_tree.add_node(
                _id, info=('root',), type='NA',
                status='C', next_node_id_iter=None, next_node_id=None, depth=0, state=state.copy()
        )
        # assign TOC node to every time point as root child
        toc_lst = [ ]
        if self.is_temporal:
            # unordered time points should be open
            t_unordered: List[ int ] = self.state.t_unordered
            toc_lst: List[ TOCSpecTuple ] = [ ("TOC", x) for x in t_unordered ]
            # ordered time points should be closed
            t_ordered: List[ int ] = self.state.t_ordered
            toc_lst += [ ("TOC", x) for x in t_ordered ]
        _id = self._add_nodes_and_edges( _id, self.task_list + toc_lst )
        # mark ordered time points as closed
        if self.is_temporal:
            for node_id in self.sol_tree.nodes:
                node = self.sol_tree.nodes[ node_id ]
                if node[ "type" ] == "TOC":
                    if node[ "info" ][ 1 ] in t_ordered:
                        node[ "status" ] = "C"
        print( [ self.sol_tree.nodes[ x ][ "info" ] for x in self.sol_tree.nodes ] )
        while True:
            # if solution tree root node is open then planning failed
            # this only occurs when the next_node_iter for the root is exhausted, so backtracking opens the root node
            if self.sol_tree.nodes[ 0 ][ 'status' ] == 'O':
                print( "No valid plan found" )
                return None

            self.iterations += self._planning( parent_node_id )
            assert is_tree( self.sol_tree ), "Error! Solution graph is not a tree."


            # Store the planning solution as a list of actions to be executed.
            for node_id in dfs_preorder_nodes(self.sol_tree, source=0):
                if self.sol_tree.nodes[node_id]['type'] == 'A':
                    self.sol_plan.append( self.sol_tree.nodes[node_id]['info'] )
            # if only root remains we need to increase max depth and try again
            if len(self.sol_tree.nodes) > 1 or depth_step_size is None:
                break
            elif verbose>0:
                print( "No solution for max depth of " + str(self.max_depth))
                print( "Increasing max depth to " + str( self.max_depth + self.depth_step_size ) )
            _id = self._add_nodes_and_edges( 0, self.task_list )

        if not self.is_temporal and self.sol_tree.nodes[ 0 ][ 'status' ] != 'O':
            dfs_preorder_lst = [ *dfs_preorder_nodes( self.sol_tree, source=0 ) ]
            assert self.node_id_visit_order == dfs_preorder_lst

        return self.sol_plan

    # ******************************        Class Method Declaration        ****************************************** #
    # returns the node id of the next element to be expanded
    # for atemporal planning this is done in dfs order
    # for temporal planning, all open nodes in the frontier are candidates
    def select_next_open_node(
            self, _iter: int, reference_chronicle: ReferenceChronicle,
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
        node_id_visit_order = self.node_id_visit_order
        # select next node to attempt
        if self.is_temporal and value_chronicle is not None:

            t_ordered: List[ int ] = [ *reference_chronicle.t_ordered ]
            t_now = t_ordered[ -1 ]
            # node must be open
            open_frontier_node_tup_filter: Iterator[ Tuple[ Hashable, int ] ] = filter(
                    lambda x: sol_tree.nodes[ x ][ "status" ] == "O", sol_tree.nodes,
            )

            # filter/sort nodes by the following:
            # node type order [TSA < A < G] (t_now) < G < TOC (only for time points that have no
            # mandatory preceding time point in t_unordered, any other would fail)
            # MAY BENEFIT FROM ADDITIONAL ORDERING

            # filter TOC nodes to only those that could be next time point
            # stable sort
            stn: TemporalNetwork = value_chronicle.temporal_network
            # only allow for last ordered time point (t_now)
            # potentially from unordered time points
            t_unordered: List[ int ] = [ *reference_chronicle.t_unordered ]
            potential_time_points = stn.get_potential_next_time_points( t_unordered )
            print( "UNORDERED TIME POINTS" )
            print( t_unordered )
            print( "POTENTIAL TIME POINTS" )
            print( potential_time_points )

            # track node id, anchoring time point, type
            node_id_anchor_time_point_tup_lst: List[ Tuple[ int, int, int ] ] = [ ]
            for node_id in open_frontier_node_tup_filter:
                node = sol_tree.nodes[ node_id ]
                node_type: str = node[ "type" ]
                node_info = node[ "info" ]
                node_group: int = None
                keep_flag = False
                # only temporal singleton actions for the current time point
                if node_type == "TSA":
                    anchor_idx = 1
                    node_group = 1
                    anchor_tp = node_info[ anchor_idx ]
                    if anchor_tp == t_now:
                        keep_flag = True
                # high priority to actions
                elif node_type == "A":
                    node_info = node_info[ 1 ]
                    anchor_idx = 1
                    keep_flag = True
                    anchor_tp = node_info[ anchor_idx ]
                    if anchor_tp == t_now:
                        node_group = 2
                    else:
                        node_group = 3
                # high priority to goals for t_now, else medium priority
                elif node_type == "G":
                    keep_flag = True
                    anchor_idx = 0
                    anchor_tp = node_info[ anchor_idx ]
                    if anchor_tp == t_now:
                        node_group = 4
                    else:
                        node_group = 5
                # temporal ordering choices should only be considered if they have no timepoint in t_unordered
                # that must precede them, if criteria met low priority
                elif node_type == "TOC":
                    anchor_idx = 1
                    anchor_tp = node_info[ anchor_idx ]
                    if anchor_tp in potential_time_points:
                        keep_flag = True
                        node_group = 6
                # goal verification nodes
                # only choose if parent goal anchoring time point is t_now
                # for those maximum priority
                elif node_type == "VG":
                    # print( node_id_visit_order )
                    # print( node_id )
                    # print( [ *sol_tree.edges ] )
                    # print( [ *sol_tree.nodes ] )
                    parent_node_id = [ *sol_tree.pred[ node_id ].keys() ][ 0 ]
                    # print( node_id )
                    # print( parent_node_id )
                    # print( [ *sol_tree.edges ] )

                    parent_node_info = sol_tree.nodes[ parent_node_id ][ "info" ]
                    anchor_idx = 0
                    anchor_tp = parent_node_info[ anchor_idx ]
                    if anchor_tp == t_now:
                        keep_flag = True
                        node_group = 0
                else:
                    # print( node_info )
                    raise (ValueError( "Invalid node type for temporal planning: " + node_type ))
                if keep_flag:
                    node_id_anchor_time_point_tup_lst.append( (node_id, node_info[ anchor_idx ], node_group) )
            # print( node_id_anchor_time_point_tup_lst )
            # sort TSA < A < G (t_now) < G (other) TOC
            node_id_anchor_time_point_tup_lst.sort( key=lambda x: x[ 2 ] )
            for node_id_anchor_time_point_tup in node_id_anchor_time_point_tup_lst:
                if self._verbose > 1:
                    print(
                            'Iteration {}, Refining Node {}:\n {}'.format(
                                    _iter, node_id_anchor_time_point_tup[ 0 ],
                                    repr( sol_tree.nodes[ node_id_anchor_time_point_tup[ 0 ] ][ 'info' ] ),

                            ),
                    )
                yield cast( int, node_id_anchor_time_point_tup[ 0 ] )


        # expand nodes in dfs order for atemporal planning
        else:
            # print( "atemporal" )
            for node_id in dfs_preorder_nodes( sol_tree, source=0 ):
                node = sol_tree.nodes[ node_id ]
                if node[ 'status' ] == "O":
                    curr_node_id = cast( int, node_id )
                    if self._verbose > 1:
                        print(
                                'Iteration {}, Refining Node {}:\n {}'.format(
                                        _iter, curr_node_id,
                                        str( sol_tree.nodes[ curr_node_id ][ 'info' ] ),
                                )
                        ),
                    yield curr_node_id
                    break

    # ******************************        Class Method Declaration        ****************************************** #
    def _planning(self, root_node_id):
        is_temporal = self.is_temporal
        value_chronicle = self.value_chronicle
        select_next_open_node = self.select_next_open_node
        sol_tree = self.sol_tree
        node_id_visit_order = self.node_id_visit_order
        backtrack = self._backtrack
        node_refine = self._node_refine
        add_nodes_and_edges = self._add_nodes_and_edges
        goals_not_achieved = self._goals_not_achieved
        _iter = 0
        # prev_node is the node id that was last closed
        # for initial planning the root node id is used and considered closed
        verbose = self._verbose
        while True:
            print( "VISIT ORDER" )
            print( [ sol_tree.nodes[ x ][ "info" ] for x in node_id_visit_order ] )
            print( "CURRENT GOAL NETWORK" )
            print( [ sol_tree.nodes[ x ][ "info" ] for x in sol_tree.nodes ] )
            if is_temporal:
                toc_closed_node_id_lst = [
                    *filter(
                            lambda x: sol_tree.nodes[ x ][ "type" ] == "TOC" and sol_tree.nodes[ x ][ "status" ] == "C",
                            sol_tree.nodes,
                    ),
                ]
                toc_closed_node_lst = [
                    *map(
                            lambda x: sol_tree.nodes[ x ][ "info" ][ 1 ], toc_closed_node_id_lst,
                    ),
                ]
                toc_open_node_id_lst = [
                    *filter(
                            lambda x: sol_tree.nodes[ x ][ "type" ] == "TOC" and sol_tree.nodes[ x ][ "status" ] == "O",
                            sol_tree.nodes,
                    ),
                ]
                toc_open_node_lst = [
                    *map(
                            lambda x: sol_tree.nodes[ x ][ "info" ][ 1 ], toc_open_node_id_lst,
                    ),
                ]
                print( "CLOSED TIMEPOINTS" )
                print( toc_closed_node_lst )
                print( "ORDERED TIME POINTS" )
                print( self.state.t_ordered )
                print( "OPEN TIMEPOINTS" )
                print( toc_open_node_lst )
                print( "UNORDERED TIME POINTS" )
                print( self.state.t_unordered )
                assert set( toc_open_node_lst ) == set( self.state.t_unordered )
                assert set( toc_closed_node_lst ) == set( self.state.t_ordered )

            prev_node_id = -1
            # curr_node_id = -1
            # print( node_id_visit_order )
            # print( "CLOSED NODES" )
            # print(
            #         [ sol_tree.nodes[ x ][ "info" ] for x in
            #             filter( lambda y: sol_tree.nodes[ y ][ "status" ] == "C", sol_tree.nodes ) ],
            # )
            # print( "OPEN NODES" )
            # print(
            #         [ sol_tree.nodes[ x ][ "info" ] for x in
            #             filter( lambda y: sol_tree.nodes[ y ][ "status" ] == "O", sol_tree.nodes ) ],
            # )

            # print( [ *sol_tree.nodes ] )
            # if every node in tree is closed, then planning has completed successfully
            if (sol_tree.nodes[ root_node_id ][ 'status' ] == 'O' or all(
                    [ sol_tree.nodes[ node_id ][ 'status' ] == 'C' for node_id in
                        dfs_preorder_nodes( sol_tree, root_node_id ) ],
            )):
                return _iter

            # increment iteration count
            _iter += 1
            # get previous node from node_id_visit_order
            # curr_node will be gotten from prev_node
            prev_node_id = node_id_visit_order[ -1 ]
            # print( prev_node_id )
            prev_node = sol_tree.nodes[ prev_node_id ]
            # if prev_node does not have an iterator to find current node, instantiate one
            # having the iterator on the node allows for us to avoid nodes we checked already

            if prev_node[ "next_node_id_iter" ] is None:
                if verbose > 2:
                    print(
                            "Iteration " + str( _iter ) + " " +
                            "Node " + str( prev_node_id ) + "; " + str(
                                    prev_node[ "info" ],
                            ) + "; has no next_node_id_iter, instantiating",
                    )
                prev_node[ "next_node_id_iter" ] = select_next_open_node(
                        _iter, self.state.copy(), value_chronicle,
                )
                assert (prev_node[ "next_node_id_iter" ] is not None)
            # check for cases where new current node is needed
            need_new_curr_node = False
            # prev_node is freshly closed, iterator used first time
            if prev_node[ "next_node_id" ] is None:
                if verbose > 2:
                    print(
                            "Node " + str( prev_node_id ) + ": " + str(
                                    prev_node[ "info" ],
                            ) + ", has no next_node_id, preparing to select",
                    )
                    # print( "next_node_id was None" )
                    need_new_curr_node = True
            # some current nodes (as of now goals and tasks) will need multiple iterations to
            # exhaust all potential methods, here we check if a new current node should be set
            # or to use the old (same as previous iteration) current node again
            else:
                curr_node_id = cast( int, prev_node[ "next_node_id" ] )
                # print( node_id_visit_order )
                # print( sol_tree.nodes[ prev_node_id ][ 'info' ] )
                # print( curr_node_id )
                curr_node = sol_tree.nodes[ curr_node_id ]
                # check if goal or task
                if curr_node[ "type" ] in { "G", "T", "M" }:
                    # check if methods have been exhausted
                    if curr_node[ "exhausted_methods" ]:
                        need_new_curr_node = True
                        if verbose > 2:
                            print( "Node " + str( curr_node_id ) + " has exhausted methods for present current node" )
                            # print( "curr_node was " + str( curr_node_id ) )
                else:
                    need_new_curr_node = True
                    # print( "type was not in {G,T,M}" )
                    # print( "curr_node was " + str( curr_node_id ) )
                    # print( "curr_node_type was " + str( curr_node[ "type" ] ) )

            # set current node for this iteration, need_new_curr_node pull from iterator
            # if the iterator has been exhausted, we will need to reopen the previous node and set as current node,
            # pop the previous node off of node_id_vist_order, set the
            # previous node to the last id in the node_id_visit_order, and return to top of loop
            if need_new_curr_node:
                try:
                    curr_node_id = next( prev_node[ "next_node_id_iter" ] )
                    prev_node[ "next_node_id" ] = curr_node_id
                except StopIteration:

                    # current prev_node_id is the root_node_id, planning has failed

                    # if prev_node_id == root_node_id:
                    #     print( "Cannot backtrack from root node, terminating planning" )
                    #     return _iter
                    # otherwise backtrack
                    # print( node_id_visit_order )
                    backtrack()
                    if verbose > 2:
                        print(
                                "Node " + str(
                                        prev_node_id,
                                ) + ", has exhausted its next_node_id_iter, backtracking",
                        )
                    # return to loop start
                    continue
            else:
                curr_node_id = cast( int, prev_node[ "next_node_id" ] )

            node_refine( curr_node_id, _iter, value_chronicle=value_chronicle, verbose=verbose )


    # ******************************        Class Method Declaration        ****************************************** #
    def _node_refine(
            self, curr_node_id: int, _iter: int, verbose: Optional[ int ] = None,
        value_chronicle: Optional[ValueChronicle]=None ):
        node_id_visit_order = self.node_id_visit_order
        sol_tree = self.sol_tree
        is_temporal = self.is_temporal
        if verbose is None:
            verbose = self._verbose
        self.node_expansions += 1
        curr_node = self.sol_tree.nodes[curr_node_id]
        # If curr_node already has a value for state, it means that the algorithm backtracked to this node.
        if curr_node[ 'state' ] is not None:
            # Modify the current state as the saved state at that node.
            self.state.update( curr_node[ 'state' ].copy() )
        # If curr_node doesn't have value for state, it means that the node is visited for the first time.
        else:
            # Save the current state in the node.
            curr_node[ 'state' ] = self.state.copy()
        curr_node_info = curr_node['info']

        # If current node is a Task
        if curr_node['type'] == 'T':

            subtasks = None
            # consider failure if next decomposition would exceed max depth
            # print(curr_node["depth"], self.max_depth)
            if self.max_depth is None or curr_node["depth"] < self.max_depth:
                # If methods are available for refining the task, use them.
                while curr_node[ 'available_methods' ] != [ ]:
                    # get method instance
                    if curr_node[ 'selected_method_instances' ] is None:
                        method = curr_node[ 'available_methods' ][ 0 ]
                        curr_node[ 'selected_method' ] = method
                        # create method instance generator
                        curr_node[ 'selected_method_instances' ] = method( self.state.copy(), *curr_node_info[ 1: ] )
                    try:
                        subtasks = next( curr_node[ 'selected_method_instances' ] )
                    # exhausted all instances of selected method select new method
                    except StopIteration:
                        # get next method
                        curr_node[ 'available_methods' ].pop( 0 )
                        if len( curr_node[ 'available_methods' ] ) > 0:
                            method = curr_node[ 'available_methods' ][ 0 ]
                            curr_node[ 'selected_method' ] = method
                            # create method instance generator
                            curr_node[ 'selected_method_instances' ] = method(
                                    self.state.copy(), *curr_node_info[ 1: ],
                            )
                    if subtasks is not None:
                        curr_node[ 'status' ] = 'C'
                        # if curr_node_id not in node_id_visit_order:
                        node_id_visit_order.append( curr_node_id )
                        _id = self._add_nodes_and_edges( curr_node_id, subtasks )

                        if verbose > 2:
                            print(
                                    'Iteration {}, Task {} successfully refined\n Subtasks: {}'.format(
                                            _iter,
                                            repr( curr_node_info ),
                                            str( subtasks ),
                                    ),
                            )
                        break
            if subtasks is None:
                if verbose > 2:
                    print('Iteration {}, Task {} refinement failed'.format(_iter, repr(curr_node_info)))
                    print('Iteration {}, Backtracking to {}.'.format(
                        _iter, repr(self.sol_tree.nodes[curr_node_id]['info'])))
                curr_node[ 'exhausted_methods' ] = True
                # curr_node[ 'available_methods' ] = iter( curr_node[ 'methods' ] )

        # If current node is an Action
        elif curr_node['type'] == 'A':
            new_state = None
            # If the Action is not blacklisted
            if curr_node_info not in self.blacklist:
                # handle temporal actions having RestorationTuple Output
                if is_temporal:
                    # print( "TEMPORAL ACTION" )
                    # print( curr_node_info )
                    # print( self.state )
                    # print( value_chronicle.changes )
                    temporal_action_output: TemporalActionOutput = curr_node[ 'action' ](
                            self.state.copy(), value_chronicle, *curr_node_info[ 1: ],
                    )
                    if temporal_action_output is not None:
                        restoration_tup: RestorationTuple = temporal_action_output[ 0 ]
                        temporal_singleton_action_lst: List[ TemporalSingletonAction ] = temporal_action_output[
                            1 ]
                        # this will handle object change and persistence rollback
                        new_state: ReferenceChronicle = restoration_tup[ 0 ]
                        temporal_restoration_tup: TemporalRestorationTuple = restoration_tup[ 1 ]
                        # these will handle temporal network rollback
                        curr_node[ "temporal_restoration_tup" ] = temporal_restoration_tup
                        curr_node[ "temporal_singleton_action_lst" ] = temporal_singleton_action_lst
                        # adds a temporal order choice node for every new time point label
                        time_point_add_lst: List[ int ] = temporal_restoration_tup[ 0 ]
                        toc_lst: List[ TOCSpecTuple ] = [ ("TOC", x) for x in time_point_add_lst ]
                        # update unordered
                        new_state.t_unordered += time_point_add_lst
                        # adds TSA and TOC nodes as children
                        self._add_nodes_and_edges( curr_node_id, temporal_singleton_action_lst + toc_lst )
                    else:
                        new_state = None
                else:
                    new_state = curr_node['action'](self.state.copy(), *curr_node_info[1:])
                if new_state is None or self.branch_cyclic( new_state, curr_node_id ):
                    new_state = None
                # If Action was successful, update the state.
                if new_state is not None:
                    curr_node['status'] = 'C'
                    # if curr_node_id not in node_id_visit_order:
                    node_id_visit_order.append( curr_node_id )
                    self.state.update( new_state.copy() )
                    if verbose > 2:
                        print('Iteration {}, Action {} successful.'.format(_iter, repr(curr_node_info)))
            if new_state is None:
                if verbose > 2:
                    print('Iteration {}, Action {} failed.'.format(_iter, repr(curr_node_info)))

        # If current node is a Goal
        elif curr_node['type'] == 'G':
            subgoals = None
            # Skip goal refinement if already achieved
            # if temporal, check that the state as of t_now would meet this goal
            goal_done = False
            if is_temporal:
                temporal_goal = curr_node_info
                if value_chronicle is not None and CI.verify_object_assertion(
                        self.state.copy(), value_chronicle, temporal_goal
                ):
                    goal_done = True
            else:
                state_var, arg, desired_val = curr_node_info
                if self.state.__dict__[ state_var ][ arg ] == desired_val:
                    goal_done = True
            if goal_done:
                curr_node[ 'status' ] = 'C'
                # if curr_node_id not in node_id_visit_order:
                node_id_visit_order.append( curr_node_id )
                subgoals = [ ]
                if self._verbose > 2:
                    print( 'Iteration {}, Goal {} already achieved'.format( _iter, repr( curr_node_info ) ) )
            else:
                # consider failure if next decomposition would exceed max depth
                if self.max_depth is None or curr_node[ "depth" ] < self.max_depth:
                    # If methods are available for refining the goal, use them.
                    while curr_node[ 'available_methods' ] != [ ]:
                        # get method instance
                        if curr_node[ 'selected_method_instances' ] is None:
                            method = curr_node[ 'available_methods' ][ 0 ]
                            curr_node[ 'selected_method' ] = method
                            # create method instance generator
                            # print( curr_node_info )
                            if is_temporal:
                                curr_node[ 'selected_method_instances' ] = method(
                                        self.state.copy(), value_chronicle, curr_node_info,
                                )

                            else:
                                curr_node[ 'selected_method_instances' ] = method(
                                        self.state.copy(), *curr_node_info[ 1: ],
                                )
                        try:
                            # adjusted for temporal goal output and save info for back tracking

                            if is_temporal:
                                temporal_method_output: TemporalMethodOutput = next(
                                        curr_node[ 'selected_method_instances' ],
                                )
                                if temporal_method_output is not None:
                                    restoration_tup: RestorationTuple = temporal_method_output[ 0 ]
                                    reference_chronicle: ReferenceChronicle = restoration_tup[ 0 ]
                                    temporal_restoration_tup: TemporalRestorationTuple = restoration_tup[ 1 ]
                                    # these will handle temporal network rollback
                                    curr_node[ "temporal_restoration_tup" ] = temporal_restoration_tup
                                    # this will handle object change and persistence rollback
                                    if reference_chronicle is not None:

                                        subgoals: List[ Union[ TemporalGoal, TemporalActionCall ] ] = \
                                            temporal_method_output[ 1 ]
                                        # adds a temporal order choice node for every new time point label
                                        time_point_add_lst: List[ int ] = temporal_restoration_tup[ 0 ]
                                        toc_lst: List[ TOCSpecTuple ] = [ ("TOC", x) for x in time_point_add_lst ]
                                        # update unordered
                                        reference_chronicle.t_unordered += time_point_add_lst
                                        # include TOC nodes as children
                                        subgoals += toc_lst
                                        self.state.update( reference_chronicle.copy() )

                            else:
                                subgoals = next( curr_node[ 'selected_method_instances' ] )
                        # exhausted all instances of selected method select new method
                        except StopIteration:
                            # get next method
                            curr_node[ 'available_methods' ].pop( 0 )
                            if len( curr_node[ 'available_methods' ] ) > 0:

                                method = curr_node[ 'available_methods' ][ 0 ]
                                curr_node[ 'selected_method' ] = method
                                # create method instance generator
                                curr_node[ 'selected_method_instances' ] = method(
                                        self.state.copy(), *curr_node_info[ 1: ],
                                )
                        if subgoals is not None:
                            curr_node[ 'status' ] = 'C'
                            # if curr_node_id not in node_id_visit_order:
                            node_id_visit_order.append( curr_node_id )

                            _id = self._add_nodes_and_edges( curr_node_id, subgoals )
                            parent_node_id = curr_node_id
                            if verbose > 2:

                                print(
                                        'Iteration {}, Goal {} successfully refined\n Subgoals: {}'.format(
                                                _iter,
                                                repr( curr_node_info ),
                                                str( subgoals ),
                                        ),
                                )
                            break
            if subgoals is None:
                if verbose > 2:
                    print('Iteration {}, Goal {} refinement failed'.format(_iter, repr(curr_node_info)))
                curr_node[ 'exhausted_methods' ] = True
                # print( self.state.t_ordered )
                # print( self.state.t_unordered )
                # print( value_chronicle.changes[ "clear" ][ :self.state.changes[ "clear" ] + 1 ] )
                # print( value_chronicle.persistences[ "clear" ][ :self.state.persistences[ "clear" ] + 1 ] )

                # curr_node[ 'available_methods' ] = iter( curr_node[ 'methods' ] )

        # If current node is a MultiGoal
        elif curr_node['type'] == 'M':
            subgoals = None
            unachieved_goals = self._goals_not_achieved(curr_node_id)
            if not unachieved_goals:
                curr_node['status'] = "C"
                subgoals = []
                if verbose > 2:
                    print('Iteration {}, MultiGoal {} already achieved'.format(_iter, repr(curr_node_info)))
            else:
                # consider failure if next decomposition would exceed max depth
                if self.max_depth is None or curr_node[ "depth" ] < self.max_depth:
                    # If methods are available for refining the multigoal, use them.
                    while curr_node[ 'available_methods' ] != [ ]:
                        # get method instance
                        if curr_node[ 'selected_method_instances' ] is None:
                            # get next method
                            method = curr_node[ 'available_methods' ][ 0 ]
                            # print( method )
                            curr_node[ 'selected_method' ] = method
                            # create method instance generator
                            curr_node[ 'selected_method_instances' ] = method( self.state.copy(), curr_node_info )
                        try:
                            # print( curr_node[ 'selected_method_instances' ] )
                            subgoals = next( curr_node[ 'selected_method_instances' ] )
                            # print( subgoals )
                        # exhausted all instances of selected method select new method
                        except StopIteration:
                            # get next method
                            curr_node[ 'available_methods' ].pop( 0 )
                            if len( curr_node[ 'available_methods' ] ) > 0:
                                method = curr_node[ 'available_methods' ][ 0 ]
                                # print(method)
                                curr_node[ 'selected_method' ] = method
                                # create method instance generator
                                curr_node[ 'selected_method_instances' ] = method( self.state.copy(), curr_node_info )
                                # print( method( self.state, curr_node_info ) )
                                # print( [  *curr_node[ 'selected_method_instances' ] ] )
                        if subgoals is not None:
                            curr_node[ 'status' ] = 'C'
                            # if curr_node_id not in node_id_visit_order:
                            node_id_visit_order.append( curr_node_id )
                            _id = self._add_nodes_and_edges( curr_node_id, subgoals )
                            if verbose > 2:
                                print( 'Iteration {}, MultiGoal {} successfully refined'.format( _iter,
                                                                                            repr( curr_node_info ) ) )
                            break
            if subgoals is None:
                if verbose > 2:
                    print(
                        'Iteration {}, MultiGoal {} refinement failed'.format(_iter, repr(curr_node_info)))
                curr_node[ 'exhausted_methods' ] = True
                curr_node[ 'available_methods' ] = iter( curr_node[ 'methods' ] )

        elif curr_node['type'] == 'VG':
            parent_node_id = predecessor( self.sol_tree, curr_node_id )
            # if temporal, verify that temporal goal is met
            # assumption is that temporal goals are verified when their anchor is t_now
            # new change assertions can only disrupt this if they have a time point
            # that is equal to the goal time point, but has not yet occurred
            # verify that the existing assertions entails the temporal goal
            # holds true and then place an equivalent change assertion to prevent
            # future clobbering
            # ALTERNATIVE FIND THE CHANGE ASSERTION THAT MAKES THE GOAL TRUE
            # AND ADD PERSISTANCE ASSERTION FROM THERE TO NOW
            if is_temporal:
                # get goal from parent
                temporal_goal: TemporalGoal = sol_tree.nodes[ parent_node_id ][ 'info' ]
                new_state = self.state.copy()
                # test that the goal is entailed by the existing assertions
                success_flag = False
                if value_chronicle is not None and CI.verify_object_assertion(
                        new_state, value_chronicle, temporal_goal,
                ):
                    # add change assertion equivalent to goal as guard against clobbering
                    # attempt chronicle update
                    change_update_dict = dict()
                    success_flag = CI.add_changes(
                            new_state, value_chronicle, [ temporal_goal, ], change_update_dict,
                    )
                # on success change reference chronicle (state) and close node
                if success_flag:
                    curr_node[ 'status' ] = "C"
                    self.state.update( new_state.copy() )
            else:
                state_var, arg, desired_val = self.sol_tree.nodes[ parent_node_id ][ 'info' ]
                if self.state.__dict__[ state_var ][ arg ] == desired_val:
                    curr_node[ 'status' ] = "C"
                    if curr_node_id not in node_id_visit_order:
                        node_id_visit_order.append( curr_node_id )
                else:
                    if verbose > 2:
                        curr_node_info = self.sol_tree.nodes[ curr_node_id ][ 'info' ]
                        print( 'Iteration {}, Goal {} Verification failed.'.format( _iter, repr( curr_node_info ) ) )


        elif curr_node['type'] == 'VM':
            parent_node_id = predecessor( sol_tree, curr_node_id )
            unachieved_goals = self._goals_not_achieved(parent_node_id)
            if not unachieved_goals:
                curr_node['status'] = "C"
                if curr_node_id not in node_id_visit_order:
                    node_id_visit_order.append( curr_node_id )
            else:
                if verbose > 2:
                    curr_node_info = self.sol_tree.nodes[curr_node_id]['info']
                    print('Iteration {}, MultiGoal {} Verification failed.'.format(_iter,
                                                                                   repr(curr_node_info)))
        # adds time point to ordered_time_points and equivalent time constraint
        elif is_temporal and curr_node[ 'type' ] == "TOC":
            curr_node = sol_tree.nodes[ curr_node_id ]
            curr_node_info = curr_node[ 'info' ]
            curr_node_time_point = curr_node_info[ 1 ]
            success_flag = False
            # try setting equal to last node in t_ordered and then try strictly greater than
            while curr_node[ 'seperation_condition_lst' ] != [ ] and not (success_flag):
                separation_condition = curr_node[ 'seperation_condition_lst' ].pop()
                if value_chronicle is not None:
                    # attempt inserting temporal constraint
                    new_state = self.state.copy()

                    time_point_order_result = CI.order_time_point(
                            new_state, value_chronicle, curr_node_time_point, separation_condition,
                    )
                    success_flag, temporal_restoration_tup = time_point_order_result
                    # if successful update, close node
                    if success_flag:
                        curr_node[ 'status' ] = "C"
                        node_id_visit_order.append( curr_node_id )
                        self.state.update( new_state.copy() )
                        curr_node[ "temporal_restoration_tup" ] = temporal_restoration_tup
                        if verbose > 2:
                            print(
                                    'Iteration {}, Time point {} successfully placed in ordering'.format(
                                            _iter,
                                            repr( curr_node_info[ 1 ] ),
                                    ),
                            )
            if not success_flag:
                if verbose > 2:
                    print(
                            'Iteration {}, Time point {} was not able to be placed in the ordering'.format(
                                    _iter,
                                    repr( curr_node_info[ 1 ] ),
                            ),
                    )
        # attempt to insert changes associated with temporal singleton action
        elif is_temporal and curr_node[ 'type' ] == "TSA":
            # collect time point and effects list
            curr_node = sol_tree.nodes[ curr_node_id ]
            curr_node_info = curr_node[ 'info' ]
            # time_point = curr_node_info[0]
            object_var_change_lst = curr_node_info[ 2 ]
            change_update_dict = dict()
            if value_chronicle is not None:
                # attempt chronicle update
                new_state = self.state.copy()
                success_flag = CI.add_changes(
                        self.state.copy(), value_chronicle, object_var_change_lst, change_update_dict,
                )
                # on success change reference chronicle (state) and close node
                if success_flag:
                    curr_node[ 'status' ] = "C"
                    self.state.update( new_state )
        else:
            raise (ValueError( curr_node[ 'type' ] + " ia an unsupported node type" ))

    # # ******************************        Class Method Declaration
    # ****************************************** #
    # def replan(self, state: State, fail_node_id: int, verbose: Optional[int] = 0) -> _p_type:
    #     """
    #     IPyHOP.replan(state_1, fail_node_id) tells IPyHOP to re-plan the solution tree given that the node with id
    #     *fail_node_id* has failed. The planning should be accomplished from a new initial state *state_1*,
    #     using whatever methods and actions IPyHOP was constructed
    #
    #     Additionally, you can add an optional argument called 'verbose' that tells IPyHOP how much debugging printout
    #     it should provide:
    #         * if verbose = 0 (the default), IPyHOP returns the solution but prints nothing;
    #         * if verbose = 1, it prints the initial parameters and the answer;
    #         * if verbose = 2, it also prints a message on each iteration;
    #         * if verbose = 3, it also prints info about what it's computing.
    #
    #     :param state: An instance of State class containing the collection of variable bindings representing
    #         the current/initial state in the planning problem.
    #     :param fail_node_id: The id of the failure node.
    #     :param verbose: [Optional] An integer specifying the level of verbosity for IPyHOP.
    #     :return: A list containing the solution plan.
    #     """
    #
    #     self.state = state.copy()
    #
    #     max_id = self._post_failure_modify(fail_node_id)
    #     parent_node_id, curr_node_id = self._backtrack(list(self.sol_tree.predecessors(fail_node_id))[0],
    #     fail_node_id)
    #
    #     self.iterations = self._planning(max_id, parent_node_id)
    #     assert is_tree(self.sol_tree), "Error! Solution graph is not a tree."
    #
    #     self.sol_plan = []
    #     # Store the planning solution as a list of actions to be executed.
    #     for node_id in dfs_preorder_nodes(self.sol_tree, source=0):
    #         if self.sol_tree.nodes[node_id]['type'] == 'A':
    #             if self.sol_tree.nodes[node_id]['tag'] == 'new':
    #                 self.sol_plan.append(self.sol_tree.nodes[node_id]['info'])
    #
    #     return self.sol_plan

    # # ******************************        Class Method Declaration        ****************************************** #
    # def replan(self, state: State, action_position: int, verbose: Optional[int] = 0,
    #            depth_step_size: Optional[int]=None) -> Union[Tuple[_p_type,int],bool]:
    #     """
    #     repairs stored solution tree for a failure occuring at action_position given
    #     the state of the world
    #     Parameters
    #     ----------
    #     state           :   State
    #                     world state after failure
    #     action_position :   int
    #                     index immediately after last successful plan action
    #     verbose         :   int
    #                     higher verbosity increases detail of output in stdout valid for {0,1,2,3}
    #     depth_step_size :   Optional[int]
    #                     if set will limit how deep the solution tree may expand, otherwise unlimited
    #
    #     Returns
    #     -------
    #     Union[_p_type,bool]
    #                     if planning succeeds return a tuple with the plan at index 0 and the index where
    #                     execution should resume at index 1, if planning fails returns False
    #
    #     """
    #     sol_tree = self.sol_tree
    #     # get root children for plan success validation
    #     original_task_list = [*sol_tree.successors(0)]
    #     # get node id of action
    #     dfs_node_ids = [*dfs_preorder_nodes( sol_tree )]
    #     # print(dfs_node_ids)
    #     dfs_action_node_ids = [ *filter( lambda x: sol_tree.nodes[ x ][ "type" ] == "A", dfs_node_ids ) ]
    #     # print(dfs_action_node_ids)
    #     fail_node_id = dfs_action_node_ids[ action_position ]
    #     # fail node should always be action so move up to parent node before start
    #
    #     node_id_stack = [ next( sol_tree.predecessors( fail_node_id ) ) ]
    #     state_stack = [ state.copy() ]
    #     node_id = node_id_stack[ 0 ]
    #     plan = []
    #     exec_preorder_index = action_position
    #     exec_plan_index = exec_preorder_index
    #     # problem state and node are stored in stacks
    #     # if node cannot be repaired try reparing parent
    #     # once repair complete simulate until problem or success
    #     # if problem place on stack and repeat repair process
    #     # if at any point in repair process the previous node on the stack is descendant of current problem,
    #     # pop from stack and continue repair procedure from previous node
    #     # print(exec_plan_index )
    #     while node_id_stack != []:
    #
    #         if verbose >= 3:
    #             print("Loop Head, Node Stack is: " + str( node_id_stack ) )
    #         # get top of stack
    #         node_id = node_id_stack[ 0 ]
    #         # root has no parent we have exhausted all methods
    #         if node_id == 0:
    #             break
    #         true_state = state_stack[ 0 ]
    #         # get parent id
    #         parent_id = next( sol_tree.predecessors( node_id ) )
    #         parent_node = sol_tree.nodes[ parent_id ]
    #
    #         # print( parent_id )
    #         # unexpand node
    #         sol_tree.remove_nodes_from( descendants( sol_tree, node_id ) )
    #         node = sol_tree.nodes[ node_id ]
    #         # print(node["info"])
    #         node[ "status" ] = "O"
    #         node[ 'available_methods' ] = [ *node[ 'methods' ] ] # CHANGE
    #         node[ "selected_method" ] = None
    #         node[ "state" ] = None
    #         # node[ "state" ] = true_state
    #         node[ "selected_method_instances" ] = None # CHANGE
    #
    #         # replace child with parent on stack
    #         node_id_stack[ 0 ] = parent_id
    #         # print(self.sol_tree.nodes[parent_id]["info"])
    #
    #         # there exists relevant methods we have not tried
    #         # propagate expansion downward, backtracking if needed but never higher than current node
    #         if node[ "available_methods" ] != []:
    #             self.state = true_state.copy()
    #             _iter, exec_id = self._planning(parent_id ,verbose=verbose)
    #             self.iterations += _iter
    #             if node[ "status" ] == "O":
    #                 continue
    #         # deadend move up
    #         else:
    #             # check if root is reached
    #             # if parent_id == 0:
    #             #     break
    #             # if so return to previous node on stack else continue traversing up
    #             prev_node = node_id_stack[ 1 ] if len( node_id_stack ) > 1 else None
    #             grandparent_id = next( sol_tree.predecessors( parent_id ) )
    #             # do this to prevent altering precondition guarantees
    #             # that is we have gone far enough up the tree that the previous node will be orphaned by repair
    #             if prev_node in descendants( sol_tree, grandparent_id ):
    #                 node_id_stack.pop(0)
    #                 state_stack.pop(0)
    #             continue
    #         # print("HERE_0")
    #         # get new plan
    #         # plan is actions in left-right order, ignore previously executed commands unless
    #         # needed to complete immediate goal/task
    #
    #         # don't reexecute tree branches prior to current failure point parent
    #         preorder_nodes = [*dfs_preorder_nodes( sol_tree )]
    #         exec_preorder_index = preorder_nodes.index( exec_id )
    #         # we care only about actions that still need to be executed
    #         plan = [*filter(lambda x: sol_tree.nodes[x]["type"] == "A", preorder_nodes)]
    #         plan_node_indices = [ *map( lambda x: preorder_nodes.index( x ), plan ) ]
    #         for i in range( len( plan_node_indices ) ):
    #             if plan_node_indices[ i ] >= exec_preorder_index:
    #                 exec_plan_index = i
    #                 break
    #         # print(exec_plan_index)
    #
    #         # plan going forward is stored in PyHOP object
    #
    #         # simulate new plan from current point
    #         # print("STATE")
    #         # print(true_state)
    #         act_plan = [ sol_tree.nodes[ x ][ "info" ] for x in plan ]
    #         sim_state, sim_index, sim_success = self.simulate_no_copy( true_state, act_plan, exec_plan_index )
    #         # if a problem occurs put state at failure and attempted node on stack
    #
    #         if not sim_success:
    #             state_stack.insert( 0, sim_state )
    #             node_id_stack.insert( 0, next( sol_tree.predecessors( plan[ sim_index ] ) ) )
    #             continue
    #         # print( "HERE_2" )
    #         # plan worked
    #         break
    #     # check for solution failure
    #     new_task_list = [*sol_tree.successors(0)]
    #     # plan repair failure
    #     if new_task_list != original_task_list:
    #         return False
    #     # plan repair success
    #     else:
    #         self.sol_plan = act_plan
    #         return act_plan, exec_plan_index
    #     # return self.sol_plan

    # ******************************        Class Method Declaration        ******************************************
    def _add_nodes_and_edges(self, parent_node_id: int, children_node_info_list: List[ Tuple ]):
        _id = None
        is_temporal = self.is_temporal
        parent_depth=self.sol_tree.nodes[parent_node_id]["depth"]
        for child_node_info in children_node_info_list:
            _id = self.get_next_id()
            # TOC nodes are when the planner decides to add a node to the ordered nodes
            if is_temporal and child_node_info[ 0 ] == "TOC":
                self.sol_tree.add_node(
                        _id, info=child_node_info, type='TOC', status='O', state=None,
                        depth=parent_depth + 1, seperation_condition_lst=[ *default_separation_condition_tup ],
                        tag='new', next_node_id_iter=None, next_node_id=None, temporal_restoration_tuple=None,
                )
                self.sol_tree.add_edge( parent_node_id, _id )
            # TSA nodes bundle action effects by timepoint
            elif is_temporal and child_node_info[ 0 ] == "TSA":
                self.sol_tree.add_node(
                        _id, info=child_node_info, type='TSA', status='O', state=None,
                        depth=parent_depth + 1,
                        tag='new', next_node_id_iter=None, next_node_id=None,
                )
                self.sol_tree.add_edge( parent_node_id, _id )
            elif isinstance( child_node_info, MultiGoal ):  # equivalent to type(child_node_info) == MultiGoal
                relevant_methods = self.methods.multigoal_method_dict[child_node_info.goal_tag]
                self.sol_tree.add_node(_id, info=child_node_info, type='M', status='O', state=None,
                        selected_method=None, available_methods=[ *relevant_methods ],
                        methods=relevant_methods, selected_method_instances=None, depth=parent_depth + 1,
                        tag='new', exhausted_methods=False, next_node_id_iter=None, next_node_id=None
                )
                self.sol_tree.add_edge(parent_node_id, _id)
            elif child_node_info[0] in self.methods.task_method_dict:
                relevant_methods = self.methods.task_method_dict[child_node_info[0]]
                self.sol_tree.add_node(_id, info=child_node_info, type='T', status='O', state=None,

                selected_method = None, available_methods = [ *relevant_methods ],
                methods = relevant_methods, selected_method_instances = None, depth = parent_depth + 1, tag='new',
                exhausted_methods=False, next_node_id_iter=None, next_node_id=None)
                self.sol_tree.add_edge(parent_node_id, _id)

            elif child_node_info[0] in self.actions.action_dict:
                action = self.actions.action_dict[child_node_info[0]]
                self.sol_tree.add_node(
                        _id, info=child_node_info, type='A', status='O', action=action, tag='new',
                        next_node_id_iter=None, next_node_id=None, depth=parent_depth + 1, state=None,
                )
                self.sol_tree.add_edge(parent_node_id, _id)
                # if temporal, make spot for temporal restoration tuple
                # this will be used to restore temporal network during back tracking
                if is_temporal:
                    self.sol_tree.nodes[ _id ][ "temporal_restoration_tuple" ]: Optional[
                        TemporalRestorationTuple ] = None
                    self.sol_tree.nodes[ _id ][ "temporal_singleton_action_lst" ] = None

            elif child_node_info[ 0 ] in self.methods.goal_method_dict or (
                    is_temporal and child_node_info[ 1 ] in self.methods.goal_method_dict):
                if is_temporal:
                    goal_label_idx = 1
                else:
                    goal_label_idx = 0
                relevant_methods = self.methods.goal_method_dict[ child_node_info[ goal_label_idx ] ]
                self.sol_tree.add_node(_id, info=child_node_info, type='G', status='O', state=None,
                selected_method = None, available_methods = [ *relevant_methods ],
                methods = relevant_methods, selected_method_instances = None, depth = parent_depth + 1, tag='new',
                        exhausted_methods=False, next_node_id_iter=None, next_node_id=None, )


                # if temporal, make spot for temporal restoration tuple
                # this will be used to restore temporal network during back tracking
                if is_temporal:
                    self.sol_tree.nodes[ _id ][ "temporal_restoration_tuple" ]: Optional[
                        TemporalRestorationTuple ] = None
                self.sol_tree.add_edge( parent_node_id, _id )
        if self.sol_tree.nodes[parent_node_id]['type'] == 'G':
            _id = self.get_next_id()
            self.sol_tree.add_node(_id, info='VerifyGoal', type='VG', status='O', depth=parent_depth+1, next_node_id_iter=None,
                    next_node_id=None, state=None, )
            self.sol_tree.add_edge(parent_node_id, _id)
        elif self.sol_tree.nodes[parent_node_id]['type'] == 'M':
            _id = self.get_next_id()
            self.sol_tree.add_node(_id, info='VerifyMultiGoal', type='VM', status='O', depth=parent_depth+1, next_node_id_iter=None,
                    next_node_id=None, state=None, )
            self.sol_tree.add_edge(parent_node_id, _id)
        return _id

    # ******************************        Class Method Declaration        ****************************************** #
    # NO LONGER NEEDED
    # def _post_failure_modify(self, fail_node_id):
    #
    #     rev_pre_ord_nodes = reversed(list(dfs_preorder_nodes(self.sol_tree, source=0)))
    #
    #     for node_id in rev_pre_ord_nodes:
    #
    #         c_node = self.sol_tree.nodes[node_id]
    #         c_node['status'] = 'O'
    #
    #         if node_id == fail_node_id:
    #             break
    #
    #         c_type = c_node['type']
    #         if c_type == 'T' or c_type == 'G' or c_type == 'M':
    #             c_node['state'] = None
    #             c_node['selected_method'] = None
    #             c_node['available_methods'] = [*c_node['methods']]
    #             c_node[ "selected_method_instances" ] = None
    #             descendant_list = list(descendants(self.sol_tree, node_id))
    #             self.sol_tree.remove_nodes_from(descendant_list)
    #
    #     max_id = -1
    #     for node_id in self.sol_tree.nodes:
    #         if node_id >= max_id:
    #             max_id = node_id + 1
    #         if 'state' in self.sol_tree.nodes[node_id]:
    #             if self.sol_tree.nodes[node_id]['status'] == 'C':
    #                 self.sol_tree.nodes[node_id]['state'] = self.state.copy()
    #             else:
    #                 self.sol_tree.nodes[node_id]['state'] = None
    #
    #     return max_id

    # ******************************        Class Method Declaration        ****************************************** #

    # resets node currently being probed
    # if there are no other options for the next node of the last visited node, reopen previous node
    ### CURRENT PROBLEM ###
    # types of backtrack: right sibling, parent, rightmost descendant of left sibling
    # conversely going forward: left sibling, child, the first right sibling of an ancestor going up the tree
    # when backtracking to task/goal the next_node_id will point to original first child (no longer in tree)
    # resetting the next_node or iter causes backtracking to root (exact reason unclear)
    # resetting selected_method and method iter with above causes infinite loop (cant determine previous attempts)
    # restting state with next_node+ gives incorrect plan
    # likely needs to manipulate current prev_node and the one before
    # resets the current prev_node
    # reopens the previous prev_node and makes the planners current state the same as the previous prev_node state
    def _backtrack(self):
        is_temporal = self.is_temporal
        value_chronicle = self.value_chronicle
        node_id_visit_order = self.node_id_visit_order
        sol_tree = self.sol_tree
        prev_node_id = node_id_visit_order[ -1 ]
        prev_node = sol_tree.nodes[ prev_node_id ]
        curr_node_id = prev_node[ 'next_node_id' ]
        # curr_node_id should only be None if prev_node_id has exhausted potential next nodes
        if curr_node_id is None:
            node_id_visit_order.pop()
            self.state.update( prev_node[ 'state' ].copy() )
            prev_node[ 'status' ] = 'O'
            prev_node[ 'next_node_id_iter' ] = None

            dfs_successor_dict = dfs_successors( self.sol_tree, prev_node_id )
            if prev_node_id in dfs_successor_dict.keys():
                sol_tree.remove_nodes_from( dfs_successor_dict[ prev_node_id ] )

            if is_temporal and value_chronicle is not None:
                value_chronicle.temporal_network.restore_graph(
                        *prev_node[ 'temporal_restoration_tuple' ],
                )
                prev_node[ 'temporal_restoration_tuple' ] = None
        else:

            curr_node = sol_tree.nodes[ curr_node_id ]
            if is_temporal:
                print( "CURRENT ORDERED TIME POINTS" )
                print( curr_node[ "state" ].t_ordered )
                print( "PREVIOUS ORDERED TIME POINTS" )
                print( prev_node[ "state" ].t_ordered )
            # print( prev_node )
            prev_type = prev_node[ 'type' ]
            curr_type = curr_node[ 'type' ]
            # reset previous node (as it was at creation)
            # nodes with methods
            dfs_successor_dict = dfs_successors( self.sol_tree, curr_node_id )
            if curr_node_id in dfs_successor_dict.keys():
                sol_tree.remove_nodes_from( dfs_successor_dict[ curr_node_id ] )

            if curr_type in [ 'G', 'M', 'T' ]:
                relevant_methods = curr_node[ 'methods' ]
                curr_node[ 'selected_method' ] = None
                curr_node[ 'available_methods' ] = [ *relevant_methods ]
                curr_node[ 'selected_method_instances' ] = None
                curr_node[ 'exhausted_methods' ] = False
            if curr_type in [ 'TOC', ]:
                curr_node[ 'seperation_condition_lst' ] = [ *default_separation_condition_tup ]
            if is_temporal and value_chronicle is not None:

                if curr_type in [ 'G', 'A', 'TOC' ]:
                    # print( curr_type )
                    if curr_node[ 'temporal_restoration_tuple' ] is not None:
                        value_chronicle.temporal_network.restore_graph(
                                *curr_node[ 'temporal_restoration_tuple' ],
                        )
                        curr_node[ 'temporal_restoration_tuple' ] = None

            curr_node[ 'status' ] = 'O'
            curr_node[ 'next_node_id_iter' ] = None
            curr_node[ 'next_node_id' ] = None
            curr_node[ 'state' ] = None
        prev_node[ 'next_node_id' ] = None

        # print( "PREV NODE BACKTRACK" )
        # print( prev_node[ "info" ] )
        # print( prev_node[ 'state' ] )
        # print( prev_prev_node )

        return



    # ******************************        Class Method Declaration        ****************************************** #
    def _goals_not_achieved(self, multigoal_node_id):
        # insure that all subgoal of multigoal are achieved
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

    def simulate_no_copy(self, state: State, act_plan: List[Tuple], start_ind=0) -> List:
        """
        Simulates the generated plan on the given state without keeping intermediate states

        :param state: An instance of State class containing the collection of variable bindings representing
            the current in the planning problem.
        :param start_ind: An integer specifying the index of the command in the generated plan to simulate from.
        :return: last state not None and index in plan where this occured
        """
        prev_state = state.copy()
        curr_state = prev_state
        # print("SIMULATE")
        for i, action in enumerate( act_plan[ start_ind: ] ):
            curr_state = self.actions.action_dict[action[0]](prev_state, *action[1:])
            if curr_state is None:
                return ( prev_state, start_ind + i, False )
            prev_state = curr_state
        return ( curr_state, len( act_plan ) - 1, True )
    # ******************************        Class Method Declaration        ****************************************** #
    def blacklist_command(self, command: Tuple):
        """
        Blacklists a provided command. Blacklisted commands will fail during planning.

        :param command: A tuple representing a command instance that should be blacklisted.
        """
        self.blacklist.add(command)

    # ******************************        Class Method Declaration        ****************************************** #
    def get_next_id(self):
        """
                Used to ensure all nodes have unique id

        """
        self.id_counter += 1
        return self.id_counter

    # ******************************        Class Method Declaration        ****************************************** #
    # returns true if the new state for the node at node_id is equal to any state on the path from that node
    # to the root, else returns false
    def branch_cyclic( self, new_state: State, node_id: int ) -> bool:
        if self.branch_cycle_check_flag:
            sol_tree = self.sol_tree
            sol_tree_nodes = sol_tree.nodes
            node_ancestors = ancestors( sol_tree, node_id )
            # do want to look at root which is stateless
            node_ancestors.remove(0)
            ancestor_states = map( lambda x: sol_tree_nodes[x]["state"], node_ancestors )

            return any( new_state == a_node_state for a_node_state in ancestor_states )
        else:
            return False

    # # ******************************        Class Method Declaration        ****************************************** #
    # def is_dependency_of(self, node_1_id: int, node_2_id: int) -> bool:
    #     """
    #             returns True if node_2 occurs after node_1 in preorder sort or is node_1
    #
    #     """
    #     # get tree in preorder
    #     preorder_nodes = dfs_preorder_nodes( 0 )
    #     if preorder_nodes.index( node_1_id ) <= preorder_nodes.index( node_1_id ):
    #         return True

    # ******************************        Class Method Declaration        ****************************************** #
    #
    def hddl_plan_str( self, name_mapping: Optional[Dict[str,str]]=None ) -> str:
        """
        Get IPC plan solution tree str representation of IPyHOPPER solution tree

        Parameters
        ----------
        name_mapping    :   Optional[Dict[str,str]]
                        dictionary mapping every IPyHOPPER term to desired string representation

        Returns
        -------
        str
                        IPyHOPPER plan in IPC format using str
        """
        sol_tree = self.sol_tree
        # output header
        output_str = "==>\n"
        # plan
        preorder_node_ids = [ *dfs_preorder_nodes( sol_tree ) ]
        dfs_action_node_ids = [ *filter( lambda x: sol_tree.nodes[ x ][ "type" ] == "A", preorder_node_ids ) ]
        dfs_action_nodes = [*map( lambda x: (x, sol_tree.nodes[ x ]), dfs_action_node_ids )]
        # unpack each action into string
        for node_id, node in dfs_action_nodes:
            # id
            output_str += str(node_id) + " "
            # action name and arguements
            for arg in node[ "info" ]:
                arg_str = str( arg )
                if name_mapping is not None:
                    arg_str = name_mapping[ arg_str ]
                output_str += arg_str + " "
            output_str += "\n"
        # decomposition
        output_str += "\n"
        dfs_nonaction_node_ids = [ *filter( lambda x: sol_tree.nodes[ x ][ "type" ] != "A", preorder_node_ids ) ]
        dfs_nonaction_nodes = [ *map( lambda x: (x, sol_tree.nodes[ x ]), dfs_nonaction_node_ids ) ]
        # unpack each method into string
        for node_id, node in dfs_nonaction_nodes:
            node_info = node[ "info" ]
            # root node
            if node_id == 0:
                output_str += node_info[ 0 ] + " "
                # top level children
                for child_id in neighbors( sol_tree, node_id ):
                    output_str += str(child_id) + " "

            else:
                # all other nonprimitive nodes
                # id
                output_str += str( node_id ) + " "
                # method name and arguments
                for arg in node[ "info" ]:
                    arg_str = str( arg )
                    if name_mapping is not None:
                        arg_str = name_mapping[ arg_str ]
                    output_str += arg_str + " "
                # subtasks
                output_str += "-> "
                # method of decomposition
                try:
                    decomp_str = node["selected_method"].func.__name__
                except AttributeError:
                    decomp_str = node[ "selected_method" ].__name__
                if name_mapping is not None:
                    decomp_str = name_mapping[ decomp_str ]
                output_str += decomp_str + " "
                # child node ids
                for child_id in neighbors( sol_tree, node_id ):
                    output_str += str(child_id) + " "
            output_str += "\n"
        output_str += "<==\n"
        return output_str


    def read_SHOP( self, SHOP_sol_tree_path: str, initial_state: State ):
        """
        Replicate SHOP solution tree in IPyHOPPER

        Parameters
        ----------
        SHOP_sol_tree_path      :   str
                                file path to SHOP tree (IPC format)
        initial_state           :   State
                                state at start of the plan

        Returns
        -------

        """
        re_shop_top_level = self.re_shop_top_level
        re_task= self.re_task
        # make empty solution tree
        self.plan( { }, [ ] )
        # read in SHOP tree
        with open( SHOP_sol_tree_path, "r" ) as f:
            shop_str = f.read()
        # list of match tuples
        top_level = re_shop_top_level.findall( shop_str )
        # add nodes first
        sol_tree = self.sol_tree
        info_dict = dict()
        info_dict[ 0 ] = { "info": ("root",), "type": "D", "status": 'NA', "depth": 0 }
        # get child node ids
        child_id_set = set()
        # for each tuple add node and edges
        for str_tuple in top_level:
            # id as int
            task_id = int( str_tuple[ 0 ] )
            # find name (grab first match for name) and clean
            parameter_list = [ ]
            for i, parameter in enumerate( re_task.findall( str_tuple[ 1 ] ) ):
                parameter_list.append( clean_string( parameter ) )
            task_name = parameter_list[ 0 ]
            # build node dict
            case = "A" if str_tuple[ 2 ] == "" else "T"
            info_dict[ task_id ] = {
                "info": tuple( parameter_list ),
                "type": case,
                "status": 'C',
                "state": None,
                "depth": None
            }
            methods = self.methods
            actions = self.actions
            # make tree skeleton
            if case == "T":
                # attach correct methods
                child_ids = str_tuple[ 3 ].split()
                method_name = clean_string( child_ids.pop( 0 ) )
                # allows for partial function currying
                try:
                    # partial case
                    selected_method_name = [ *filter( lambda x: x.func.__name__ == method_name, methods.task_method_dict[ task_name ] ) ][0]
                except AttributeError:
                    # normal case
                    selected_method_name = [ *filter( lambda x: x.__name__ == method_name, methods.task_method_dict[ task_name ] ) ][0]
                except KeyError:
                    # method not found
                    raise KeyError("Input tree contains method, " + method_name +
                                   ", but no method of this name was found in the domain definition")
                except IndexError:
                    # method not found
                    raise KeyError("Input tree contains method, " + method_name +
                                   ", but no method of this name was found in the domain definition")

                info_dict[ task_id ].update(
                    {
                        "selected_method": selected_method_name,
                        "available_methods": [ *methods.task_method_dict[ task_name ] ],
                        "methods": [ *methods.task_method_dict[ task_name ] ],
                        "selected_method_instances": None,
                    }
                )
                # add children
                child_id_list = [ *map( int, child_ids ) ]
                task_from_edge_list = [ *map( lambda x: (task_id, x), child_id_list ) ]
                sol_tree.add_edges_from( task_from_edge_list )
                # any task that is a child may never be an
                child_id_set |= { *child_id_list }
            # name action
            else:
                action_func = actions.action_dict[ task_name ]
                info_dict[ task_id ].update(
                    {
                        "action": action_func,
                    }
                )
        # get all top level tasks and add as root children
        top_level_task_id_list = [ *sorted( { *sol_tree.nodes } - child_id_set - { 0 } ) ]
        root_child_edges = map( lambda x: (0, x), top_level_task_id_list )
        sol_tree.add_edges_from( root_child_edges )
        # fill in node info for all nodes
        for node_id in sol_tree.nodes:
            node = sol_tree.nodes[ node_id ]
            for k, v in info_dict[ node_id ].items():
                node[ k ] = v
        # get plan node ids
        sol_tree_nodes = sol_tree.nodes
        plan_node_ids = [*filter( lambda x: sol_tree_nodes[x]["type"] == "A", dfs_preorder_nodes(sol_tree) )]
        sol_plan = [*map( lambda x: sol_tree_nodes[x]["info"], plan_node_ids )]
        self.sol_plan = sol_plan
        # simulate state progression
        state_list = self.simulate( initial_state, start_ind=0 )
        # in reverse order assign states to ancestors
        for act_id, act_state in zip(reversed(plan_node_ids), reversed(state_list[:-1])):
            ancestor_id_set = ({*ancestors(sol_tree,act_id)} - {0}) | {act_id}
            for ancestor_id in ancestor_id_set:
                sol_tree_nodes[ancestor_id]["state"] = act_state.copy()
        # for methods without action descendants copy from left
        preorder_node_ids = [*dfs_preorder_nodes(sol_tree)]
        rev_preorder_node_ids = [*reversed(preorder_node_ids)]
        for i in range(len(preorder_node_ids)):
            node_id = rev_preorder_node_ids[i]
            # method without action descendant
            if node_id != 0 and ( "state" not in sol_tree_nodes[ node_id ].keys() or sol_tree_nodes[ node_id ][ "state" ] is None ):
                # tail end
                if node_id == rev_preorder_node_ids[0]:
                    sol_tree_nodes[ node_id ][ "state" ] = state_list[-1].copy()
                # base case
                else:
                    next_node_id = rev_preorder_node_ids[i-1]
                    sol_tree_nodes[ node_id ][ "state" ] = sol_tree_nodes[ next_node_id ][ "state" ].copy()
        # set depth
        node_depth = 0
        for parent_id, child_id_list in bfs_successors(sol_tree,0):
            node_depth = sol_tree_nodes[parent_id]["depth"] + 1
            for node_id in child_id_list:
                sol_tree_nodes[ node_id ][ "depth" ] = node_depth
        self.id_counter = max( sol_tree.nodes )
        return







# takes PDDL strings and makes them assignable to python boundVars
def clean_string( input_str: str ) -> str:
    # ? must be removed
    new_str = input_str.replace( "?", "" )
    # ! must be removed
    new_str = new_str.replace( "!", "" )
    # - must be replaced with _
    new_str = new_str.replace( "-", "__" )
    # PDDL is case insensitive so we are going to make everything lower case
    new_str = new_str.lower()
    # we cannot allow keywords
    if keyword.iskeyword(new_str):
        new_str += "___"
    # remove leading and trailing
    new_str = new_str.strip()
    return new_str

# ******************************************    Class Declaration End       ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for IPyHOP isn't implemented.")

"""
Author(s): Yash Bansod and Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
"""
