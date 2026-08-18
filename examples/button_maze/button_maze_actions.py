#!/usr/bin/env python

"""
File Description: buttom maze domain actions
There is a maze with doors that have buttons to open them. After a known fixed time delay the gates shut.
A number of patients in the maze need to be stabilized before a set time. The agent must navigate the
maze and stabilize all the patients before their limit.
"""
from itertools import groupby
# from __future__ import annotations
from typing import Dict, List, NewType, Tuple

from ordered_set import OrderedSet

from ipyhop import ChronicleInterface, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, RestorationTuple, \
    State, TemporalAction, TemporalActionOutput, TemporalActions, TemporalConstraint, TemporalNetwork, \
    TemporalRestorationTuple, TemporalSingletonAction, ValueChronicle

# domain typing
Patient = NewType( "Patient", str )
Location = NewType( "Location", int )
Connection = Tuple[ Location, Location ]
Button = NewType( "Button", str )


# class to contain all domain facts that do not change
class ButtonMazeRigidRelations:
    def __init__(
            self, button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at,
    ):
        # location of button with button as key and location as value
        self.button_at: Dict[ Button, Location ] = button_at
        # ordered set of connected locations
        # a connection is always open if ungated
        self.connections: OrderedSet[ Connection ] = connections
        # whether a connection is gated
        self.is_gated: Dict[ Connection, bool ] = is_gated
        # a valid chronicle requires every patient be stabilized before this value
        # the patient is the key and the time value is the value
        self.patient_stabilization_limit: Dict[ Patient, int ] = patient_stabilization_limit
        # dict where gates are keys and the button that opens said gate is the value
        self.opened_by: Dict[ Connection, Button ] = opened_by
        # dict where buttons are keys and the gates opened by the buttons are values
        # simplest case for multiple gates is wanting both the incoming and outgoing edge to open
        opens: Dict[ Button, List[ Connection ] ] = { k: [ ] for k in set( opened_by.values() ) }
        for k, v in opened_by.items():
            opens[ v ].append( k )
        self.opens: Dict[ Button, Tuple[ Connection ] ] = { k: tuple( v ) for k, v in opens.items() }  # type: ignore
        # dict where button are keys and the value is the time value that the gate is open for
        self.open_time: Dict[ Button, int ] = open_time
        # dict with patients as keys and their locations as values
        self.patient_at: Dict[ Patient, Location ] = patient_at
        # # # connections as graph
        # self.connection_graph: nx.Graph = nx.DiGraph( connections )
        # #
        # self.shortest_path_lengths: Dict[ Location, Dict[ Location, int ] ] = dict(  # type: ignore
        #         nx.algorithms.shortest_path_length( self.connection_graph ),
        # )


temporal_actions_instance = TemporalActions()


class ButtonMazeReferenceChronicle( ReferenceChronicle, State ):
    def __init__(
            self, changes: Dict[ str, int ], t_ordered: List[ int ], t_unordered: List[ int ],
            persistences: Dict[ str, int ],
    ):
        super().__init__(
                changes,
                t_ordered,
                t_unordered,
                persistences,
        )
        self.__name__ = "default"


class ButtonMazeValueChronicle( ValueChronicle ):
    # noinspection PyProtocol
    def __init__(
            self,
            changes: Dict[ str, List[ ObjectVarChange ] ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, List[ str ] ],
            rigid_relations: ButtonMazeRigidRelations,
    ):
        super().__init__(
                changes,
                persistences,
                temporal_network,
                domain_objects,
        )
        self.rigid_relations = rigid_relations


CI = ChronicleInterface()

# NOTE: ACTIONS AND METHODS ARE RESPOSIBLE FOR THEIR OWN MESS, RESTORE ON FAILURE
# ON FAILURE SHOULD RETURN INPUT REFERENCE CHRONICLE WITH EMPTY RESTORATION TUPLE

# DESIGN PRINCIPLES:
# bottom level actions should only handle change assertions for single timepoint
# avoid duplicate assertions as much as possible
# methods should not have change assertions
# have time points added at highest level possible in the hierarchy
# have constraint and persistence assertions added at the highest level of the hierarchy as possible
# temporal constraints should be established first as chronicles do not allow for assertions that may be invalid

# corresponds to pseudoaction move_block_to_table
# tga_move_block_to_table_start does nothing
# tga_move_block_to_table_end adds new change assertion

AtGoal = Tuple[ int, str, Location, bool ]

MoveCall = Tuple[ str, Tuple[ int, int ], Location, Location ]


# agent moves from start_loc to end_loc
def move(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        time_point_tup: Tuple[ int, int ], start_loc: Location, end_loc: Location,
) -> TemporalActionOutput:
    # get time point labels
    t_s, t_e = time_point_tup
    # localize variables
    locations = value_chronicle.domain_objects[ "locations" ]
    connections = value_chronicle.domain_objects[ "connections" ]
    goal_connection = (start_loc, end_loc)
    rigid_relations: ButtonMazeRigidRelations = value_chronicle.rigid_relations

    is_open: bool = False

    # can only move across connections that are either ungated or open
    if goal_connection in connections:
        is_gated: bool = rigid_relations.is_gated[ goal_connection ]
        if is_gated:
            is_open = CI.verify_object_assertion_list(
                    reference_chronicle,
                    value_chronicle,
                    [ (t_s, "is_open", goal_connection, True) ],
            )
        if (not is_gated or is_open):
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [
                (t_e, "at", end_loc, True),
                (t_e, "at", start_loc, False),
                *[ (t_e, "at", x, False) for x in filter( lambda y: y != end_loc, locations ) ],
            ]
            # persistence assertions
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                (t_s, t_s, "at", start_loc, True),
                *[ (t_s, t_s, "at", x, False) for x in filter( lambda y: y != start_loc, locations ) ],
            ]
            # temporal assertions
            temporal_constraint_lst: List[ TemporalConstraint ] = [ (t_e, "==", t_s, 1) ]
            temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
            # attempt to add all
            new_reference_chronicle = reference_chronicle.copy()
            if CI.update_chronicle(
                    new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                    temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
            ):
                # define list of singleton actions
                restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                singleton_action_lst: List[ TemporalSingletonAction ] = [ ]
                for k, v in groupby( change_assertion_lst, key=lambda x: x[ 0 ] ):
                    singleton_action_lst.append( ("TSA", k, list( v )) )
                action_output: TemporalActionOutput = (restoration_tup, singleton_action_lst)
                return action_output


PressButtonCall = Tuple[ str, Tuple[ int, int, int, int ], Button ]


# agent presses button at the same starting location
# gates assigned to that button open for the set time
# gates close after that time
def press_button(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        time_point_tup: Tuple[ int, int, int, int ], button: Button,
) -> TemporalActionOutput:
    # get time point labels
    t_s, t_open, t_close_start, t_close_end = time_point_tup
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    # localize variables
    locations = value_chronicle.domain_objects[ "locations" ]
    rigid_relations: ButtonMazeRigidRelations = value_chronicle.rigid_relations
    gate_tup: Tuple[ Connection ] = rigid_relations.opens[ button ]
    button_loc: Location = rigid_relations.button_at[ button ]
    open_time = rigid_relations.open_time[ button ]
    if CI.verify_object_assertion_list(
            reference_chronicle,
            value_chronicle,
            [
                (t_s, "at", button_loc, True),
                *[ (t_s, "is_open", gate, False) for gate in gate_tup ],
            ],
    ):

        # change assertions
        change_assertion_lst: List[ ObjectVarChange ] = [
            *[ (t_open, "is_open", gate, True) for gate in gate_tup ],
            *[ (t_close_end, "is_open", gate, False) for gate in gate_tup ],
        ]
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            *[ (t_s, t_s, "is_open", gate, False) for gate in gate_tup ],
            (t_s, t_s, "at", button_loc, True),
            *[ (t_s, t_s, "at", x, False) for x in filter( lambda x: x != button_loc, locations ) ],
            *[ (t_open, t_close_start, "is_open", gate, True) for gate in gate_tup ],
        ]
        # temporal assertions

        temporal_constraint_lst: List[ TemporalConstraint ] = [
            (t_open, "==", t_s, 1),
            (t_close_end, "==", t_close_start, 1),
            (t_close_start, "==", t_open, open_time),
        ]
        temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
        # attempt to add all
        new_reference_chronicle = reference_chronicle.copy()
        if CI.update_chronicle(
                new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
        ):
            # define list of singleton actions
            restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
            singleton_action_lst: List[ TemporalSingletonAction ] = [ ]
            for k, v in groupby( change_assertion_lst, key=lambda x: x[ 0 ] ):
                singleton_action_lst.append( ("TSA", k, list( v )) )
            action_output: TemporalActionOutput = (restoration_tup, singleton_action_lst)
            return action_output


StabilizeCall = Tuple[ str, Tuple[ int, int ], Patient ]


# agent stabilizes patient at same location
def stabilize(
        reference_chronicle: ButtonMazeReferenceChronicle, value_chronicle: ButtonMazeValueChronicle,
        time_point_tup: Tuple[ int, int ], patient: Patient,
) -> TemporalActionOutput:
    # get time point labels
    t_s, t_e = time_point_tup
    temporal_network: TemporalNetwork = value_chronicle.temporal_network
    # localize variables
    locations = value_chronicle.domain_objects[ "locations" ]
    rigid_relations: ButtonMazeRigidRelations = value_chronicle.rigid_relations
    patient_loc: Location = rigid_relations.patient_at[ patient ]
    if CI.verify_object_assertion_list(
            reference_chronicle,
            value_chronicle,
            [
                (t_s, "at", patient_loc, True),
                (t_s, "is_stable", patient, False),
            ],
    ):
        # change assertions
        change_assertion_lst: List[ ObjectVarChange ] = [
            (t_e, "is_stable", patient, True),
        ]
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_s, t_e, "at", patient_loc, True),
            (t_s, t_s, "is_stable", patient, False),
            *[ (t_s, t_e, "at", False) for x in filter( lambda y: y != patient_loc, locations ) ],
        ]
        # temporal assertions

        temporal_constraint_lst: List[ TemporalConstraint ] = [
            (t_e, "==", t_s, 1),
        ]
        temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
        # attempt to add all
        new_reference_chronicle = reference_chronicle.copy()
        if CI.update_chronicle(
                new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
        ):
            # define list of singleton actions
            restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
            singleton_action_lst: List[ TemporalSingletonAction ] = [ ]
            for k, v in groupby( change_assertion_lst, key=lambda x: x[ 0 ] ):
                singleton_action_lst.append( ("TSA", k, list( v )) )
            action_output: TemporalActionOutput = (restoration_tup, singleton_action_lst)
            return action_output


# NEED temporal extension of actions
temporal_action_lst: List[ TemporalAction ] = [ move, press_button, stabilize ]  # type: ignore

temporal_actions_instance.declare_temporal_actions( temporal_action_lst )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
