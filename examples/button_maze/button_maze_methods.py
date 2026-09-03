#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Iterator, List, Optional, Tuple

import networkx as nx

from examples.button_maze.button_maze_actions import (Button, ButtonMazeReferenceChronicle, ButtonMazeValueChronicle,
    Connection, Location, MoveCall, Patient, PressButtonCall, StabilizeCall)
from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence, RestorationTuple,
    TemporalConstraint, TemporalMethodOutput, TemporalMethods,
    TemporalNetwork, TemporalRestorationTuple)

# Potential additions
# use shortest paths to lowerbound travel time - prune dead ends as early as possible
#

CI = ChronicleInterface()
temporal_methods_instance = TemporalMethods()

AtGoal = Tuple[ int, str, Location, bool ]
StabilizeGoal = Tuple[ int, str, Patient, bool ]


# helper functions for finding valid paths between two points in button maze
def path_planning_helper(start_loc, end_loc, ):
    pass


# # a single open connection exists between current location and goal location at t_now
# def tgm_navigate_single_move(
#         reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
#         temporal_goal: AtGoal,
# ) -> Iterator[ TemporalMethodOutput ]:
#     # localize variables
#     t_e: int = temporal_goal[ 0 ]
#     predicate: str = temporal_goal[ 1 ]
#     goal_loc: Location = temporal_goal[ 2 ]
#     bool_val: bool = temporal_goal[ -1 ]
#     temporal_network: TemporalNetwork = value_chronicle.temporal_network
#     locations = value_chronicle.domain_objects[ "locations" ]
#     connections = value_chronicle.domain_objects[ "connections" ]
#     is_gated = value_chronicle.rigid_relations.is_gated
#     assert predicate == "at" and bool_val == True
#     # object constraints
#     t_now = reference_chronicle.t_ordered[ -1 ]
#     if t_now == t_e:
#         return
#         # t_0 = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
#     # must currently be a single open connection away from the goal
#     for start_loc in locations:
#         connection: Connection = (start_loc, goal_loc)
#         if connection in connections:
#             # connection is either open or ungated
#             if not is_gated[ connection ] or CI.verify_object_assertion_list(
#                     reference_chronicle,
#                     value_chronicle,
#                     [
#                         (t_now, "at", start_loc, True),
#                         (t_now, "is_open", connection, True),
#                     ],
#             ):
#                 # temporal constraints
#                 temporal_constraint_lst: List[ TemporalConstraint ] = [
#                     (t_e, "==", t_now, 1),
#                 ]
#                 # change assertions
#                 change_assertion_lst: List[ ObjectVarChange ] = [ ]
#                 # persistence assertions
#                 persistence_assertion_lst: List[ ObjectVarPersistence ] = [
#                     (t_now, t_now, "at", start_loc, True),
#                     *[ (t_now, t_now, "at", x, False) for x in filter( lambda x: x != start_loc, locations ) ],
#                 ]
#                 # initialize rollback data structures
#                 temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
#                 change_update_dict = { }
#                 persistence_update_dict = { }
#                 new_reference_chronicle = reference_chronicle.copy()
#                 if CI.update_chronicle(
#                         new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
#                         temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
#                         change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
#                 ):
#                     # define list of subgoals
#
#                     subgoal_lst: List[ MoveCall ] = [ ("move", (t_now, t_e), start_loc, goal_loc) ]
#                     restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
#                     method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
#                     yield method_output
#                     # break


# navigate recursive call no buttons
def tgm_navigate_base(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        temporal_goal: AtGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    goal_loc: Location = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    locations = value_chronicle.domain_objects[ "locations" ]
    connections = value_chronicle.domain_objects[ "connections" ]
    is_gated = value_chronicle.rigid_relations.is_gated
    connection_graph: nx.Graph = value_chronicle.rigid_relations.connection_graph
    t_now = reference_chronicle.t_ordered[ -1 ]
    assert predicate == "at" and bool_val == True
    # current position
    start_loc = None
    for loc in locations:
        if CI.verify_object_assertion_list(
                reference_chronicle,
                value_chronicle,
                [
                    (t_now, "at", loc, True),
                ],
        ):
            start_loc: Location = loc
            break
    if start_loc == goal_loc:
        return
    # maximum time allowed for travel
    print( "TIME OFFSET CHECK" )
    print( t_now, t_e )
    print( [ *temporal_network.min_stn.edges.data() ] )

    offset_bounds: Optional[ Tuple[ int, int ] ] = temporal_network.get_offset_bounds( t_now, t_e )
    if offset_bounds is None:
        delta_t_max: int = abs( temporal_network.t_max - temporal_network.t_min )
    else:
        delta_t_max: int = offset_bounds[ 1 ]
    # consider all simple paths between start_loc and goal_loc short enough to allow for travel
    path_gen: Iterator[ List[ Location ] ] = nx.all_simple_paths( connection_graph, start_loc, goal_loc, delta_t_max )
    # sort paths shortest to longest
    path_lst: List[ List[ Location ] ] = sorted( path_gen, key=lambda x: len( x ) )
    # time point label for next move action end
    t_move_end = temporal_network.get_n_new_time_point_labels( 1 )[ 0 ]
    valid_path_lst: List[ List[ Location ] ] = [ ]
    valid_paths_temporal_constraint_lst_lst: List[ List[ TemporalConstraint ] ] = [ ]
    # consider each path
    for path in path_lst:
        path_valid: bool = True
        # temporal constraints
        # not t_now and move duration is 1

        # ensure each edge in path would be open for passage
        for i in range( len( path ) - 1 ):
            curr_loc: Location = path[ i ]
            next_loc: Location = path[ i + 1 ]
            next_connection: Connection = (curr_loc, next_loc)
            # ungated connections are always open
            if is_gated[ next_connection ]:
                # okay if gate would be open for traversal at arrival estimate (i units in the future)
                if not CI.verify_object_assertion_list(
                        reference_chronicle,
                        value_chronicle,
                        [
                            (t_now, "is_open", next_connection, True),
                        ],
                        offset=i,
                ):
                    path_valid = False
                    break
        # only paths already set as open
        if path_valid:
            # ignore paths that have the same first move
            # not doing this results in a large number of redundant calls
            if all( map( lambda x: path[ 0 ] != x[ 0 ], valid_path_lst ) ):
                valid_path_lst.append( path )
                # test if enough time
                path_temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, ">=", t_now, len( path ) - 1),
                    (t_move_end, "==", t_now, 1),
                ]
                valid_paths_temporal_constraint_lst_lst.append( path_temporal_constraint_lst )
    if start_loc is not None:
        for i in range( len( valid_path_lst ) ):
            chosen_path: List[ Location ] = valid_path_lst[ i ]
            next_loc: Location = chosen_path[ 1 ]
            temporal_constraint_lst: List[ TemporalConstraint ] = valid_paths_temporal_constraint_lst_lst[ i ]
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [ ]
            # persistence assertions
            # don't revisit start location until goal achieved
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                (t_move_end, t_e, "at", start_loc, False),
            ]
            # initialize rollback data structures
            temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
            change_update_dict = { }
            persistence_update_dict = { }
            new_reference_chronicle = reference_chronicle.copy()
            # don't allow duplicate move
            if not CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [ (t_now, "at", next_loc, True) ],
                    offset=1,
            ):
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
                ):
                    # define list of subgoals
                    # move first step in path
                    subgoal_lst: List[ MoveCall | AtGoal ] = [
                        ("move", (t_now, t_move_end), start_loc, next_loc),
                        temporal_goal,
                    ]
                    restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # break

# navigate recursive call with buttons
def tgm_navigate_with_button(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        temporal_goal: AtGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    goal_loc: Location = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    locations = value_chronicle.domain_objects[ "locations" ]
    connections = value_chronicle.domain_objects[ "connections" ]
    is_gated = value_chronicle.rigid_relations.is_gated
    connection_graph: nx.Graph = value_chronicle.rigid_relations.connection_graph
    opened_by = value_chronicle.rigid_relations.opened_by
    button_at = value_chronicle.rigid_relations.button_at
    open_time = value_chronicle.rigid_relations.open_time
    t_now = reference_chronicle.t_ordered[ -1 ]
    assert predicate == "at" and bool_val == True
    # current position
    start_loc = None
    for loc in locations:
        if CI.verify_object_assertion_list(
                reference_chronicle,
                value_chronicle,
                [
                    (t_now, "at", loc, True),
                ],
        ):
            start_loc: Location = loc
            break
    if start_loc == goal_loc:
        return
    print( "OFFSET BOUND BUTTON METHOD" )
    print( t_now, t_e )
    print( [ *temporal_network.min_stn.edges.data() ] )
    # maximum time allowed for travel
    offset_bounds: Optional[ Tuple[ int, int ] ] = temporal_network.get_offset_bounds( t_now, t_e )
    if offset_bounds is None:
        delta_t_max = abs( temporal_network.t_max - temporal_network.t_min )
    else:
        delta_t_max: int = offset_bounds[ 1 ]
    # consider all simple paths between start_loc and goal_loc short enough to allow for travel
    path_gen: Iterator[ List[ Location ] ] = nx.all_simple_paths( connection_graph, start_loc, goal_loc, delta_t_max )
    # sort paths shortest to longest
    path_lst: List[ List[ Location ] ] = sorted( path_gen, key=lambda x: len( x ) )
    # time point label for next move action end
    t_move_end = temporal_network.get_n_new_time_point_labels( 1 )[ 0 ]
    # track paths to destination from current location
    valid_path_lst: List[ List[ Location ] ] = [ ]
    # temporal constraints by path
    valid_paths_temporal_constraint_lst_lst: List[ List[ TemporalConstraint ] ] = [ ]
    # buttons needed for each path
    buttons_needed_lst_lst: List[ List[ Button ] ] = [ ]
    # time point labels
    button_start_time_points_lst_lst: List[ List[ int ] ] = [ ]
    gate_open_time_points_lst_lst: List[ List[ int ] ] = [ ]
    gate_last_open_time_points_lst_lst: List[ List[ int ] ] = [ ]
    gate_close_time_points_lst_lst: List[ List[ int ] ] = [ ]
    # how long each gate is open
    gate_open_time_offset_lst_lst: List[ List[ int ] ] = [ ]
    # consider each path
    for path in path_lst:
        has_gate: bool = True
        buttons_needed_lst: List[ Button ] = [ ]
        # not t_now and move duration is
        # ensure each edge in path would be open for passage
        for i in range( len( path ) - 1 ):
            curr_loc: Location = path[ i ]
            next_loc: Location = path[ i + 1 ]
            next_connection: Connection = (curr_loc, next_loc)
            # ungated connections are always open
            if is_gated[ next_connection ]:
                # okay if gate would be open for traversal at arrival estimate (i units in the future)
                if not CI.verify_object_assertion_list(
                        reference_chronicle,
                        value_chronicle,
                        [
                            (t_now, "is_open", next_connection, True),
                        ],
                        offset=i,
                ):
                    has_gate = True
                    gate_button: Button = opened_by[ next_connection ]
                    buttons_needed_lst.append( gate_button )

        # previous method handles cases where button presses are uneeded
        if has_gate:
            # only care about unique next location, sets of buttons needed tuples
            if all(
                    map(
                            lambda x: (path[ 0 ], set( buttons_needed_lst )) != (x[ 0 ], set( x[ 1 ] )),
                            zip( valid_path_lst, buttons_needed_lst_lst ),
                    ),
            ):
                valid_path_lst.append( path )
                buttons_needed_lst_lst.append( buttons_needed_lst )
                button_start_time_points = temporal_network.get_n_new_time_point_labels( len( buttons_needed_lst ) )
                gate_open_time_points = temporal_network.get_n_new_time_point_labels( len( buttons_needed_lst ) )
                gate_last_open_time_points = temporal_network.get_n_new_time_point_labels( len( buttons_needed_lst ) )
                gate_close_time_points = temporal_network.get_n_new_time_point_labels( len( buttons_needed_lst ) )
                gate_open_time_offsets = [ open_time[ x ] for x in buttons_needed_lst ]
                # test if enough time
                path_temporal_constraint_lst: List[ TemporalConstraint ] = [
                    # minimum time is length of path minus initial position
                    (t_e, ">=", t_now, len( path ) - 1),
                    # next move takes single time unit
                    (t_move_end, "==", t_now, 1),
                    # button press must be between t_now (included) and t_end (excluded)
                    *[ (t_now, "<=", x, 0) for x in button_start_time_points ],
                    *[ (t_e, "<", x, 0) for x in gate_close_time_points ],
                    # gate opens
                    *[ (x[ 1 ], "==", x[ 0 ], 1) for x in zip( button_start_time_points, gate_open_time_points ) ],
                    # when gate is open for
                    *[ (x[ 1 ], "==", x[ 0 ], x[ 2 ]) for x in
                        zip( gate_open_time_points, gate_last_open_time_points, gate_open_time_offsets ) ],
                    # gate closing
                    *[ (x[ 1 ], "==", x[ 0 ], 1) for x in zip( gate_last_open_time_points, gate_close_time_points ) ],
                ]
                valid_paths_temporal_constraint_lst_lst.append( path_temporal_constraint_lst )
                button_start_time_points_lst_lst.append( button_start_time_points )
                gate_open_time_points_lst_lst.append( gate_open_time_points )
                gate_last_open_time_points_lst_lst.append( gate_last_open_time_points )
                gate_close_time_points_lst_lst.append( gate_close_time_points )
                gate_open_time_offset_lst_lst.append( gate_open_time_offsets )
    if start_loc is not None:
        for i in range( len( valid_path_lst ) ):
            chosen_path: List[ Location ] = valid_path_lst[ i ]
            next_loc: Location = chosen_path[ 1 ]
            buttons_needed_lst: List[ Button ] = buttons_needed_lst_lst[ i ]
            button_loc_lst: List[ Location ] = [ *map( lambda x: button_at[ x ], buttons_needed_lst ) ]
            button_start_time_points: List[ int ] = button_start_time_points_lst_lst[ i ]
            gate_open_time_points: List[ int ] = gate_open_time_points_lst_lst[ i ]
            gate_last_open_time_points: List[ int ] = gate_last_open_time_points_lst_lst[ i ]
            gate_close_time_points: List[ int ] = gate_close_time_points_lst_lst[ i ]
            temporal_constraint_lst: List[ TemporalConstraint ] = valid_paths_temporal_constraint_lst_lst[ i ]
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [ ]
            # persistence assertions
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [ ]
            # initialize rollback data structures
            temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
            change_update_dict = { }
            persistence_update_dict = { }
            new_reference_chronicle = reference_chronicle.copy()
            # don't allow duplicate move
            if not CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [ (t_now, "at", next_loc, True) ],
                    offset=1,
            ):
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
                ):
                    # define list of subgoals
                    # move first step in path
                    subgoal_lst: List[ MoveCall | AtGoal | PressButtonCall ] = [
                        # ("move", (t_now, t_move_end), start_loc, next_loc),
                        *[ (x[ 1 ], "at", x[ 0 ], True) for x in zip( button_loc_lst, button_start_time_points ) ],
                        *[ ("press_button", (x[ 1 ], x[ 2 ], x[ 3 ], x[ 4 ]), x[ 0 ]) for x in
                            zip(
                                    buttons_needed_lst, button_start_time_points,
                                    gate_open_time_points, gate_last_open_time_points, gate_close_time_points,
                            ) ],
                        temporal_goal,
                    ]
                    restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # break


# at patient stabilize
def tgm_base_stabilize(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        temporal_goal: StabilizeGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    goal_patient: Patient = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    locations = value_chronicle.domain_objects[ "locations" ]
    patient_loc = value_chronicle.rigid_relations.patient_at[ goal_patient ]
    assert predicate == "is_stable" and bool_val == True
    # object constraints
    t_now = reference_chronicle.t_ordered[ -1 ]
    # t_0 = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    # agent is at patient
    if CI.verify_object_assertion_list(
            reference_chronicle,
            value_chronicle,
            [
                (t_now, "at", patient_loc, True),
            ],
    ):
        # temporal constraints
        temporal_constraint_lst: List[ TemporalConstraint ] = [
            (t_e, "==", t_now, 1),
        ]
        # change assertions
        change_assertion_lst: List[ ObjectVarChange ] = [ ]
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_now, t_now, "at", patient_loc, True),
            *[ (t_now, t_now, "at", x, False) for x in filter( lambda x: x != patient_loc, locations ) ],
            (t_e, t_e, "is_stable", goal_patient, True),
        ]
        # initialize rollback data structures
        temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
        change_update_dict = { }
        persistence_update_dict = { }
        new_reference_chronicle = reference_chronicle.copy()
        if CI.update_chronicle(
                new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
        ):
            # define list of subgoals

            subgoal_lst: List[ StabilizeCall ] = [ ("stabilize", (t_now, t_e), goal_patient) ]
            restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
            method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
            yield method_output
            # break

# navigate and stabilize patient
def tgm_navigate_and_stabilize(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        temporal_goal: StabilizeGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    goal_patient: Patient = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    locations = value_chronicle.domain_objects[ "locations" ]
    patient_loc = value_chronicle.rigid_relations.patient_at[ goal_patient ]
    assert predicate == "is_stable" and bool_val == True
    # object constraints
    t_now = reference_chronicle.t_ordered[ -1 ]
    t_a = temporal_network.get_n_new_time_point_labels( 1 )[ 0 ]
    # t_0 = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    # agent is at patient
    if not CI.verify_object_assertion_list(
            reference_chronicle,
            value_chronicle,
            [
                (t_now, "at", patient_loc, True),
            ],
    ):
        # temporal constraints
        temporal_constraint_lst: List[ TemporalConstraint ] = [
            (t_e, ">", t_a, 0),
            (t_a, ">", t_now, 0),
        ]
        # change assertions
        change_assertion_lst: List[ ObjectVarChange ] = [ ]
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_a, t_a, "at", patient_loc, True),
            *[ (t_a, t_a, "at", x, False) for x in filter( lambda x: x != patient_loc, locations ) ],
            (t_e, t_e, "is_stable", goal_patient, True),
        ]
        # initialize rollback data structures
        temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
        change_update_dict = { }
        persistence_update_dict = { }
        new_reference_chronicle = reference_chronicle.copy()
        if CI.update_chronicle(
                new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
        ):
            # define list of subgoals

            subgoal_lst: List[ AtGoal | StabilizeCall ] = [
                (t_a, "at", patient_loc, True),
                ("stabilize", (t_a, t_e), goal_patient),
            ]
            restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
            method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
            yield method_output
            # break


temporal_methods_instance.declare_temporal_goal_methods(
        "at", [ tgm_navigate_base, tgm_navigate_with_button ],  # type: ignore
)
temporal_methods_instance.declare_temporal_goal_methods(
        "is_stable", [ tgm_base_stabilize, tgm_navigate_and_stabilize ],  # type: ignore
)
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
