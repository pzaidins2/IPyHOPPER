#!/usr/bin/env python
"""
File Description: unit testing for temporal blocks world domain
"""
from typing import Collection, Dict, List, Tuple

from ordered_set import OrderedSet

from examples.button_maze.button_maze_actions import Button, ButtonMazeReferenceChronicle, ButtonMazeRigidRelations, \
    ButtonMazeValueChronicle, Location, MoveCall, Patient, PressButtonCall, StabilizeCall, temporal_actions_instance
from examples.button_maze.button_maze_methods import temporal_methods_instance
from ipyhop import (ChronicleInterface, IPyHOP, ObjectVarChange, ObjectVarPersistence, TemporalGoal, TemporalNetwork)

CI = ChronicleInterface()


def make_button_maze_chronicle_pair(
        t_ordered: List[ int ],
        t_unordered: List[ int ],
        changes: Dict[ str, List[ ObjectVarChange ] ],
        persistences: Dict[ str, List[ ObjectVarPersistence ] ],
        temporal_network: TemporalNetwork,
        domain_objects: Dict[ str, Collection ],
        rigid_relations: ButtonMazeRigidRelations,
) -> Tuple[ ButtonMazeReferenceChronicle, ButtonMazeValueChronicle ]:
    ref_chron, val_chron = CI.make_chronicle_pair(
            ButtonMazeReferenceChronicle, ButtonMazeValueChronicle, t_ordered, t_unordered, changes, persistences,
            temporal_network, domain_objects, rigid_relations

    )
    return ref_chron, val_chron


# empty
def test_empty():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=max( patient_stabilization_limit.values() ) + max( open_time.values() ) + 1,
    )

    t_s, t_0, t_1, t_e = stn.get_n_new_time_point_labels( 4 )
    stn.add_temporal_constraints_from(
            [
                (t_0, "==", t_s, 1),
                (t_1, "==", t_0, open_time[ buttons[ 0 ] ]),
                (t_e, "==", t_1, 1),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [

    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", button_at[ buttons[ 0 ] ], True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_0, t_1, t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]


# action
def test_button():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=max( patient_stabilization_limit.values() ) + max( open_time.values() ) + 1,
    )

    t_s, t_0, t_1, t_e = stn.get_n_new_time_point_labels( 4 )
    stn.add_temporal_constraints_from(
            [
                (t_0, "==", t_s, 1),
                (t_1, "==", t_0, open_time[ buttons[ 0 ] ]),
                (t_e, "==", t_1, 1),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        ("press_button", (t_s, t_0, t_1, t_e), buttons[ 0 ]),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", button_at[ buttons[ 0 ] ], True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_0, t_1, t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('press_button', (0, 1, 1 + open_time[ buttons[ 0 ] ], 2 + open_time[ buttons[ 0 ] ]), buttons[ 0 ]),
    ]


def test_move():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 0 ]
    end_loc = locations[ 1 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=max( patient_stabilization_limit.values() ) + max( open_time.values() ) + 1,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, "==", t_s, 1),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        ("move", (t_s, t_e), start_loc, end_loc),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('move', (0, 1), start_loc, end_loc),
    ]
    assert all(
            (x in value_chronicle.changes[ "at" ][ :planner.state.changes[ "at" ] + 1 ] for x in
                [ (1, "at", end_loc, True), (1, "at", start_loc, False) ]),
    )


def test_simple_navigate():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 0 ]
    end_loc = locations[ 1 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=max( patient_stabilization_limit.values() ) + max( open_time.values() ) + 1,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, "==", t_s, 1),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        (t_e, "at", end_loc, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('move', (0, 1), start_loc, end_loc),
    ]


# stabilize
def test_stabilize():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 0 ]
    end_loc = locations[ 1 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=max( patient_stabilization_limit.values() ) + max( open_time.values() ) + 1,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, "==", t_s, 1),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        (t_e, "is_stable", patients[ 0 ], True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('stabilize', (0, 1), patients[ 0 ]),
    ]
    assert all(
            (x in value_chronicle.changes[ "is_stable" ][ :planner.state.changes[ "is_stable" ] + 1 ] for x in
                [ (1, "is_stable", patients[ 0 ], True) ]),
    )


# multi move
def test_long_navigate():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 6 ]
    end_loc = locations[ 1 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=3,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, ">", t_s, 0),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        (t_e, "at", end_loc, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('move', (0, 1), start_loc, locations[ 3 ]), ('move', (1, 2), locations[ 3 ], locations[ 0 ]),
        ('move', (2, 3), locations[ 0 ], end_loc),
    ]


# move and stabilize
def test_move_and_stabilize():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 6 ]
    target_patient = patients[ 0 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [ "Green", "Red", "Orange" ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=3,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, ">", t_s, 0),
                # (t_e, "<=", t_s, patient_stabilization_limit[ target_patient ]),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        (t_e, "is_stable", target_patient, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('move', (0, 1), start_loc, locations[ 3 ]), ('move', (1, 2), locations[ 3 ], locations[ 0 ]),
        ('stabilize', (2, 3), target_patient),
    ]
# multi move with button
def test_button_navigate():
    patients = [ Patient( x ) for x in [ "Blue", "Purple", "Pink" ] ]
    locations = [ Location( x ) for x in range( 9 ) ]
    start_loc = locations[ 6 ]
    end_loc = locations[ 7 ]
    connections = OrderedSet(
            [
                (locations[ 0 ], locations[ 1 ]), (locations[ 1 ], locations[ 0 ]),
                (locations[ 0 ], locations[ 3 ]), (locations[ 3 ], locations[ 0 ]),
                (locations[ 1 ], locations[ 2 ]), (locations[ 2 ], locations[ 1 ]),
                # (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
                (locations[ 2 ], locations[ 5 ]), (locations[ 5 ], locations[ 2 ]),
                (locations[ 3 ], locations[ 6 ]), (locations[ 6 ], locations[ 3 ]),
                # (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
                (locations[ 5 ], locations[ 8 ]), (locations[ 8 ], locations[ 5 ]),
                (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
            ],
    )
    buttons = [ Button( x ) for x in [
        "Green",
        "Red",
        "Orange",
    ] ]
    button_at = {
        buttons[ 0 ]: locations[ 3 ],
        buttons[ 1 ]: locations[ 1 ],
        buttons[ 2 ]: locations[ 5 ],
    }
    is_gated = { k: False for k in connections }
    gated_connections = [
        (locations[ 4 ], locations[ 7 ]), (locations[ 7 ], locations[ 4 ]),
        (locations[ 7 ], locations[ 8 ]), (locations[ 8 ], locations[ 7 ]),
        (locations[ 1 ], locations[ 4 ]), (locations[ 4 ], locations[ 1 ]),
    ]
    for connection in gated_connections:
        is_gated[ connection ] = True

    patient_stabilization_limit = {
        patients[ 0 ]: 20,
        patients[ 1 ]: 17,
        patients[ 2 ]: 12,
    }
    opened_by = dict()
    # opens = { k: [ ] for k in buttons }
    for i in range( len( gated_connections ) ):
        connection = gated_connections[ i ]
        button = buttons[ i // 2 ]
        opened_by[ connection ] = button

    open_time = {
        # buttons[ 0 ]: 11,
        buttons[ 1 ]: 11,
        # buttons[ 2 ]: 8,
    }

    patient_at = {
        patients[ 0 ]: locations[ 0 ],
        patients[ 1 ]: locations[ 4 ],
        patients[ 2 ]: locations[ 8 ],
    }
    rigid_relations = ButtonMazeRigidRelations(
            button_at, connections, is_gated,
            patient_stabilization_limit, opened_by, open_time, patient_at, )

    stn: TemporalNetwork = TemporalNetwork(
            t_min=0, t_max=open_time[ buttons[ 1 ] ] + 7,
    )

    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_e, ">", t_s, 0),
            ],
    )

    goal_lst: List[ TemporalGoal | MoveCall | StabilizeCall | PressButtonCall ] = [
        (t_e, "at", end_loc, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "at":        [ (t_s, "at", start_loc, True) ],
        "is_open":   [ ],
        "is_stable": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "at":        [ ],
        "is_open":   [ ],
        "is_stable": [ ],
    }

    domain_objects: Dict[ str, Collection ] = {
        "locations":   locations,
        "connections": connections,
        "patients":    patients,
        "buttons":     buttons,
    }
    reference_chronicle, value_chronicle = make_button_maze_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
            rigid_relations,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [
        ('move', (0, 1), start_loc, locations[ 3 ]), ('move', (1, 2), locations[ 3 ], locations[ 0 ]),
        ('move', (2, 3), locations[ 0 ], locations[ 1 ]),
        ("press_button", (3, 4), buttons[ 1 ]), ('move', (3, 4), locations[ 1 ], locations[ 2 ]),
        ('move', (4, 5), locations[ 2 ], locations[ 5 ]), ('move', (5, 6), locations[ 5 ], locations[ 8 ]),
        ('move', (6, 7), locations[ 8 ], locations[ 7 ]),
    ]
# multiple patients
# multiple patients needing button

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
