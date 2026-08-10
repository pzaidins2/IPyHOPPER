#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Iterator, List, Tuple

from examples.button_maze.button_maze_actions import (ButtonMazeReferenceChronicle, ButtonMazeValueChronicle,
    Connection, Location, MoveCall)
from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence, RestorationTuple,
    TemporalConstraint, TemporalMethodOutput, TemporalMethods,
    TemporalNetwork, TemporalRestorationTuple)

CI = ChronicleInterface()
temporal_methods_instance = TemporalMethods()

AtGoal = Tuple[ int, str, Location, bool ]


# helper functions for finding valid paths between two points in button maze
def path_planning_helper(start_loc, end_loc, ):
    pass


# a single open connection exists between current location and goal location at t_now
def tgm_navigate_single_move(
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
    assert predicate == "at" and bool_val == True
    # object constraints
    t_now = reference_chronicle.t_ordered[ -1 ]
    # t_0 = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    # must currently be a single open connection away from the goal
    for start_loc in locations:
        connection: Connection = (start_loc, goal_loc)
        if connection in connections:
            # connection is either open or ungated
            if not is_gated[ connection ] or CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [
                        (t_now, "at", goal_loc, True),
                        (t_now, "is_open", connection, True),
                    ],
            ):
                # temporal constraints
                temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, "==", t_now, 1),
                ]
                # change assertions
                change_assertion_lst: List[ ObjectVarChange ] = [
                    (t_e, "at", goal_loc, True),
                    *[ (t_e, "at", x, False) for x in locations ],
                ]
                # persistence assertions
                persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                    (t_now, t_now, "at", start_loc, True),
                    *[ (t_now, t_now, "at", x, False) for x in locations ],
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

                    subgoal_lst: List[ MoveCall ] = [ ("move", (t_now, t_e), start_loc, goal_loc) ]
                    restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # break


# navigate recursive call no buttons
def tgm_navigate_multi_move(
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
    t_now = reference_chronicle.t_ordered[ -1 ]
    assert predicate == "at" and bool_val == True
    # new time point
    t_s = temporal_network.get_n_new_time_point_labels( 1 )[ 0 ]

    # iterate over locations
    for mid_loc in locations:
        # location is connected to goal location
        goal_connection: Connection = (mid_loc, goal_loc)
        if goal_connection in connections:
            # if the agent is located at the location at t_now the previous method covers that
            # case, ignore
            if CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [
                        (t_now, "at", mid_loc, False),
                    ],
            ):

                # temporal constraints
                # not t_now and move duration is 1
                temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, "==", t_s, 1),
                    (t_now, "<", t_s, 0),
                ]
                # change assertions
                change_assertion_lst: List[ ObjectVarChange ] = [ ]
                # persistence assertions
                # exclusive at mid_loc for t_s
                persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                    (t_s, t_s, "at", mid_loc, True),
                    *[ (t_s, t_s, "at", x, False) for x in filter( lambda y: y != mid_loc, locations ) ],
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
                    # navigate to mid_loc by t_s and then move from mid_loc to goal_loc
                    subgoal_lst: List[ MoveCall | AtGoal ] = [
                        (t_s, "at", mid_loc, True),
                        ("move", (t_s, t_e), mid_loc, goal_loc),
                    ]
                    restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # break


# NEED TO EXTEND VERIFY OBJECT ASSERTION TO OPERATE BEYOND ORDERED TIME POINTS
# FIND AND RETURN SEPARATION CONSTRAINTS
# navigate recursive call with buttons
# def tgm_navigate_with_button(
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
#     t_now = reference_chronicle.t_ordered[ -1 ]
#     assert predicate == "at" and bool_val == True
#     # new time point
#     t_b, t_s = temporal_network.get_n_new_time_point_labels( 2 )
#
#     # iterate over locations
#     for mid_loc in locations:
#         # location is connected to goal location
#         if (mid_loc, goal_loc) in connections:
#             # if the agent is located at the location at t_now the previous method covers that
#             # case, ignore
#             if CI.verify_object_assertion_list(
#                     reference_chronicle,
#                     value_chronicle,
#                     [
#                         (t_now, "at", mid_loc, False),
#                     ],
#             ):
#
#                 # temporal constraints
#                 # not t_now and move duration is 1
#                 temporal_constraint_lst: List[ TemporalConstraint ] = [
#                     (t_e, "==", t_s, 1),
#                     (t_now, "<", t_s, 0),
#                 ]
#                 # change assertions
#                 change_assertion_lst: List[ ObjectVarChange ] = [ ]
#                 # persistence assertions
#                 # exclusive at mid_loc for t_s
#                 persistence_assertion_lst: List[ ObjectVarPersistence ] = [
#                     (t_s, t_s, "at", mid_loc, True),
#                     *[ (t_s, t_s, "at", x, False) for x in filter( lambda y: y != mid_loc, locations ) ],
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
#                     # navigate to mid_loc by t_s and then move from mid_loc to goal_loc
#                     subgoal_lst: List[ MoveCall | AtGoal ] = [
#                         (t_s, "at", mid_loc, True),
#                         ("move", (t_s, t_e), mid_loc, goal_loc),
#                     ]
#                     restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
#                     method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
#                     yield method_output
#                     # break


# navigate and stabilize patient
# stabilize all patients

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
