#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Iterator, List, Tuple

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
    if t_now == t_e:
        return
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
                        (t_now, "at", start_loc, True),
                        (t_now, "is_open", connection, True),
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
                    (t_now, t_now, "at", start_loc, True),
                    *[ (t_now, t_now, "at", x, False) for x in filter( lambda x: x != start_loc, locations ) ],
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
    if t_now == t_e:
        return
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
                if not is_gated[ goal_connection ] or CI.verify_object_assertion_list(
                        reference_chronicle,
                        value_chronicle,
                        [ (t_s, "is_open", goal_connection, True) ],
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
    t_now = reference_chronicle.t_ordered[ -1 ]
    assert predicate == "at" and bool_val == True
    # new time points
    # start of button press, end of button press, last time point gate is open, close time, start of move
    t_o_0, t_o_1, t_c_0, t_c_1, t_s = temporal_network.get_n_new_time_point_labels( 5 )
    if t_now == t_e:
        return
    # iterate over locations
    for mid_loc in locations:
        # location is connected to goal location
        goal_connection: Connection = (mid_loc, goal_loc)
        if goal_connection in connections and value_chronicle.rigid_relations.is_gated[ goal_connection ]:
            # if the gate would be open, non-button method would work
            if not CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [
                        (t_s, "is_open", goal_connection, True),
                    ],
            ):
                continue
            button: Button = value_chronicle.rigid_relations.opened_by[ goal_connection ]
            button_loc: Location = value_chronicle.rigid_relations.button_at[ button ]
            button_connection_lst: List[ Connection ] = [ *value_chronicle.rigid_relations.opens[ button ] ]
            open_time = value_chronicle.rigid_relations.open_time[ button ]
            # temporal constraints
            # move and button press have duration one
            # the gate opens at the end of the press and closes after being open for open_time
            # button press must occur before move
            temporal_constraint_lst: List[ TemporalConstraint ] = [
                (t_e, "==", t_s, 1),
                (t_o_1, "<=", t_s, 0),
                (t_o_1, "==", t_o_0, 1),
                (t_c_0, "==", t_o_1, open_time),
                (t_c_1, "==", t_c_0, 1),
                (t_now, "<=", t_o_0, 0),
            ]
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [ ]
            # persistence assertions
            # exclusive at mid_loc for t_s
            # exclusive at button_loc for t_0_0
            # gate is open for open time
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                (t_o_0, t_o_0, "at", button_loc, True),
                *[ (t_o_0, t_o_0, "at", x, False) for x in filter( lambda y: y != mid_loc, locations ) ],
                (t_s, t_s, "at", mid_loc, True),
                *[ (t_s, t_s, "at", x, False) for x in filter( lambda y: y != mid_loc, locations ) ],
                *[ (t_o_1, t_c_0, "is_open", x, True) for x in button_connection_lst ],
                *[ (t_c_1, t_c_1, "is_open", x, False) for x in button_connection_lst ],
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
                subgoal_lst: List[ MoveCall | AtGoal | PressButtonCall ] = [
                    (t_o_0, "at", button_loc, True),
                    ("press_button", (t_o_0, t_o_1, t_c_0, t_c_1), button),
                    (t_s, "at", mid_loc, True),
                    ("move", (t_s, t_e), mid_loc, goal_loc),
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
    patient_loc = value_chronicle.rigid_relations.patient_at[ Patient ]
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
            (t_a, "<", t_now, 0),
        ]
        # change assertions
        change_assertion_lst: List[ ObjectVarChange ] = [ ]
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_a, t_a, "at", patient_loc, True),
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

            subgoal_lst: List[ AtGoal | StabilizeGoal ] = [
                (t_a, "at", patient_loc, True),
                (t_e, "is_stable", patient_loc, True),
            ]
            restoration_tup: RestorationTuple = (new_reference_chronicle, temporal_restoration_tup)
            method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
            yield method_output
            # break


temporal_methods_instance.declare_temporal_goal_methods(
        "at", [ tgm_navigate_single_move, tgm_navigate_multi_move, tgm_navigate_with_button ],  # type: ignore
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
