#!/usr/bin/env python
"""
File Description: unit testing for temporal blocks world domain
"""
from typing import Dict, List, Tuple

from examples.blocks_world.temporal.blocks_world_temporal_actions import Block, Surface, Table, \
    temporal_actions_instance
from examples.blocks_world.temporal.blocks_world_temporal_methods import temporal_methods_instance
from ipyhop import (ChronicleInterface, IPyHOP, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, State,
    TemporalActionCall, TemporalGoal, TemporalNetwork, ValueChronicle)

CI = ChronicleInterface()


# chronicle classes for temporal blocks world
class BlocksWorldReferenceChronicle( ReferenceChronicle, State ):
    def __init__(
            self, changes: Dict[ str, int ],
            t_ordered: List[ int ], t_unordered: List[ int ],
            persistences: Dict[ str, int ],
    ):
        super().__init__(
                changes,
                t_ordered,
                t_unordered,
                persistences,
        )
        self.__name__ = "reference"


class BlocksWorldValueChronicle( ValueChronicle ):
    def __init__(
            self,
            changes: Dict[ str, List[ ObjectVarChange ] ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, List ],
    ):
        super().__init__(
                changes,
                persistences,
                temporal_network,
                domain_objects,
        )


def make_blocks_world_chronicle_pair(
        t_ordered: List[ int ],
        t_unordered: List[ int ],
        changes: Dict[ str, List[ ObjectVarChange ] ],
        persistences: Dict[ str, List[ ObjectVarPersistence ] ],
        temporal_network: TemporalNetwork,
        domain_objects: Dict[ str, List ],
) -> Tuple[ BlocksWorldReferenceChronicle, BlocksWorldValueChronicle ]:
    return CI.make_chronicle_pair(
            BlocksWorldReferenceChronicle, BlocksWorldValueChronicle, t_ordered, t_unordered, changes, persistences,
            temporal_network, domain_objects,
    )


# reference_chronicle, value_chronicle = \
#         CI.make_chronicle_pair(
#                 BlocksWorldReferenceChronicle,
#                 BlocksWorldValueChronicle,
#                 changes,
#                 # t_now,
#                 t_ordered,
#                 t_unordered,
#                 persistences,
#                 temporal_network,
#                 domain_objects,
#         )

# no initial goals
def test_empty_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s = stn.get_n_new_time_point_labels( 1 )[ 0 ]
    stn.add_temporal_constraints_from(
            [ ],
    )

    goal_lst: List[ TemporalGoal ] = [ ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [ ("root",), ("TOC", 0) ]


# completed goal
def test_goal_done_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [ (t_s, "<=", t_e, 0) ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "clear", A, True), ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [ ],
        "clear": [
            (t_s, "clear", A, True),
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), (1, 'clear', 'A', True), ('TOC', 1), ('TOC', 0), 'VerifyGoal',
    ]


# completed multiple goals
def test_many_goal_done_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [ (t_s, "<=", t_e, 0) ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "clear", A, True), (t_e, "is_on", A, B, True) ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, B, True),
        ],
        "clear": [
            (t_s, "clear", A, True),
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',),
        (1, 'clear', 'A', True),
        (1, 'is_on', 'A', 'B', True),
        ('TOC', 1),
        ('TOC', 0),
        'VerifyGoal',
        'VerifyGoal',
    ]


# single action
def test_action_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [ (t_s, "<", t_e, 0) ],
    )

    goal_lst: List[ TemporalGoal | TemporalActionCall ] = [
        ("move_block_to_table", (t_s, t_e), A, B),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, B, True),

        ],
        "clear": [
            (t_s, "clear", A, True),
            (t_s, "clear", TABLE, True),
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == goal_lst
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',),
        ('move_block_to_table', (0, 1), 'A', 'B'),
        ('TOC', 1),
        ('TOC', 0),
        (
            'TSA',
            1,
            [
                (1, 'is_on', 'A', 'A', False),
                (1, 'is_on', 'A', 'B', False),
                (1, 'is_on', 'A', 'Table', True),
                (1, 'clear', 'B', True),
            ],
        ),
    ]


# ordering time points
def test_time_point_ordering_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=10 )
    t_0, t_1, t_2, t_3, t_4, t_5 = stn.get_n_new_time_point_labels( 6 )
    stn.add_temporal_constraints_from(
            [
                (t_0, "<", t_1, 0),
                (t_1, "<=", t_2, 0),
                (t_2, "<", t_3, 0),
                (t_3, "<=", t_4, 0),
                (t_4, "<", t_5, 0),

            ],
    )

    goal_lst: List[ TemporalGoal | TemporalActionCall ] = [ ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }
    t_ordered: List[ int ] = [ t_0, ]
    t_unordered: List[ int ] = [ t_1, t_2, t_3, t_4, t_5 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]
    assert reference_chronicle.t_ordered == [ 0 ]
    assert reference_chronicle.t_unordered == [ 1, 2, 3, 4, 5 ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), ('TOC', 1), ('TOC', 2), ('TOC', 3), ('TOC', 4), ('TOC', 5), ('TOC', 0),
    ]
    for node_id in planner.sol_tree.nodes:
        node = planner.sol_tree.nodes[ node_id ]
        node_info = node[ "info" ]
        if node_info == ("TOC", 5):
            node_state = node[ "state" ]
            assert node_state.t_ordered == [ 0, 1, 2, 3, 4 ]
            assert node_state.t_unordered == [ 5 ]
            break


# ordering time points with backtracking
def test_time_point_ordering_backtrack_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=10 )
    t_0, t_1, t_2, t_3, t_4, t_5 = stn.get_n_new_time_point_labels( 6 )
    stn.add_temporal_constraints_from(
            [
                (t_0, "<", t_1, 0),
                (t_1, "<=", t_2, 0),
                (t_2, "<", t_4, 0),
                (t_4, "<=", t_3, 0),
                (t_5, "<", t_4, 0),

            ],
    )

    goal_lst: List[ TemporalGoal | TemporalActionCall ] = [ ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }
    t_ordered: List[ int ] = [ t_0, ]
    t_unordered: List[ int ] = [ t_1, t_2, t_3, t_4, t_5 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    sol_plan = planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert sol_plan == [ ]
    assert reference_chronicle.t_ordered == [ 0 ]
    assert reference_chronicle.t_unordered == [ 1, 2, 3, 4, 5 ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), ('TOC', 1), ('TOC', 2), ('TOC', 3), ('TOC', 4), ('TOC', 5), ('TOC', 0),
    ]
    for node_id in planner.sol_tree.nodes:
        node = planner.sol_tree.nodes[ node_id ]
        node_info = node[ "info" ]
        if node_info == ("TOC", 5):
            node_state = node[ "state" ]
            assert node_state.t_ordered == [ 0, 1, 2, ]
            assert node_state.t_unordered == [ 3, 4, 5 ]
        if node_info == ("TOC", 4):
            node_state = node[ "state" ]
            assert node_state.t_ordered == [ 0, 1, 2, 5, 3 ]
            assert node_state.t_unordered == [ 4, ]


# blocks A starts on block B, move block A to table
def test_unstack_blocks_world():
    # print( temporal_action_lst )
    # print( temporal_actions_instance )
    # print( type( temporal_actions_instance ) )
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_e, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "clear", B, True) ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, B, True),
            (t_s, "is_on", B, TABLE, True),
        ],
        "clear": [
            (t_s, "clear", A, True),
            (t_s, "clear", B, False),
            (t_s, "clear", TABLE, True),  # always true, simplified some logic
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
    )
    assert [
        ('root',), (1, 'is_on', 'A', 'Table', True), ('TOC', 1), ('TOC', 0), (3, 'clear', 'A', True),
        (4, 'clear', 'Table', True), ('move_block_to_table', (6, 1), 'A', 'B'), ('TOC', 6), ('TOC', 3),
        ('TOC', 4), ('TOC', 5), 'VerifyGoal',
        ('TSA', 1, [ (1, 'is_on', 'A', 'B', False), (1, 'is_on', 'A', 'Table', True) ]),
    ]
    # print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )

# blocks A and B start on table, move block A on to block B
def test_stack_blocks_world():
    # print( temporal_action_lst )
    # print( temporal_actions_instance )
    # print( type( temporal_actions_instance ) )
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=1 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_e, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "is_on", A, B, True) ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, TABLE, True),
            (t_s, "is_on", B, TABLE, True),
        ],
        "clear": [
            (t_s, "clear", A, True),
            (t_s, "clear", B, True),
            (t_s, "clear", TABLE, True),  # always true, simplified some logic
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
            # depth_step_size=2,
    )
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',),
        (1, 'is_on', 'A', 'B', True),
        ('TOC', 1),
        ('TOC', 0),
        ('move_block_to_block', (0, 1), 'A', 'Table', 'B'),
        'VerifyGoal',
        (
            'TSA',
            1,
            [
                (1, 'is_on', 'A', 'A', False),
                (1, 'is_on', 'A', 'Table', False),
                (1, 'is_on', 'B', 'B', False),
                (1, 'is_on', 'A', 'B', True),
                (1, 'clear', 'Table', True),
                (1, 'clear', 'B', False),
            ],
        ),
    ]
    # print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )

# block B starts on block A, flip positions
def test_reverse_stack_blocks_world():
    # print( temporal_action_lst )
    # print( temporal_actions_instance )
    # print( type( temporal_actions_instance ) )
    surfaces = [ Surface( x ) for x in [ "A", "B", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=3 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_e, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "is_on", A, B, True) ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, TABLE, True),
            (t_s, "is_on", B, A, True),
        ],
        "clear": [
            (t_s, "clear", A, False),
            (t_s, "clear", B, True),
            (t_s, "clear", TABLE, True),  # always true, simplified some logic
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
            # initial_max_depth=4,
            # depth_step_size=2,
    )
    assert planner.state.t_ordered == [ 0, 3, 7, 1 ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',),
        (1, 'is_on', 'A', 'B', True),
        ('TOC', 1),
        ('TOC', 0),
        (3, 'clear', 'A', True),
        (3, 'clear', 'B', True),
        (1, 'is_on', 'A', 'B', True),
        ('TOC', 3),
        'VerifyGoal',
        ('move_block_to_table', (0, 3), 'B', 'A'),
        'VerifyGoal',
        (7, 'clear', 'A', True),
        (7, 'clear', 'B', True),
        (1, 'is_on', 'A', 'B', True),
        ('TOC', 7),
        'VerifyGoal',
        (
            'TSA',
            3,
            [
                (3, 'is_on', 'B', 'A', False),
                (3, 'is_on', 'B', 'B', False),
                (3, 'is_on', 'B', 'Table', True),
                (3, 'clear', 'A', True),
            ],
        ),
        'VerifyGoal',
        'VerifyGoal',
        'VerifyGoal',
        ('move_block_to_block', (7, 1), 'A', 'Table', 'B'),
        'VerifyGoal',
        (
            'TSA',
            1,
            [
                (1, 'is_on', 'A', 'A', False),
                (1, 'is_on', 'A', 'Table', False),
                (1, 'is_on', 'B', 'B', False),
                (1, 'is_on', 'A', 'B', True),
                (1, 'clear', 'Table', True),
                (1, 'clear', 'B', False),
            ],
        ),
    ]
    print( planner.state.t_ordered )
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )

# blocks A, B, and C start on table
# stack A on B on C
def test_triple_stack_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "C", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B, C = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=3 )
    t_s, t_BC, t_AB = stn.get_n_new_time_point_labels( 3 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_BC, 0),
                (t_BC, "<", t_AB, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [
        (t_AB, "is_on", A, B, True),
        (t_BC, "is_on", B, C, True),
        (t_BC, "is_on", C, TABLE, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, TABLE, True),
            (t_s, "is_on", B, TABLE, True),
            (t_s, "is_on", C, TABLE, True),
        ],
        "clear": [
            (t_s, "clear", A, True),
            (t_s, "clear", B, True),
            (t_s, "clear", C, True),
            (t_s, "clear", TABLE, True),  # always true, simplified some logic
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_AB, t_BC ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [
            (t_BC, t_AB, "is_on", B, C, True),
        ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
            # depth_step_size=5,
    )
    assert planner.state.t_ordered == [ 0, 1, 2 ]
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',),
        (2, 'is_on', 'A', 'B', True),
        (1, 'is_on', 'B', 'C', True),
        (1, 'is_on', 'C', 'Table', True),
        ('TOC', 2),
        ('TOC', 1),
        ('TOC', 0),
        ('move_block_to_block', (0, 1), 'B', 'Table', 'C'),
        'VerifyGoal',
        (
            'TSA',
            1,
            [
                (1, 'is_on', 'B', 'A', False),
                (1, 'is_on', 'B', 'B', False),
                (1, 'is_on', 'B', 'Table', False),
                (1, 'is_on', 'A', 'C', False),
                (1, 'is_on', 'C', 'C', False),
                (1, 'is_on', 'B', 'C', True),
                (1, 'clear', 'Table', True),
                (1, 'clear', 'C', False),
            ],
        ),
        'VerifyGoal',
        ('move_block_to_block', (1, 2), 'A', 'Table', 'B'),
        'VerifyGoal',
        (
            'TSA',
            2,
            [
                (2, 'is_on', 'A', 'A', False),
                (2, 'is_on', 'A', 'C', False),
                (2, 'is_on', 'A', 'Table', False),
                (2, 'is_on', 'B', 'B', False),
                (2, 'is_on', 'C', 'B', False),
                (2, 'is_on', 'A', 'B', True),
                (2, 'clear', 'Table', True),
                (2, 'clear', 'B', False),
            ],
        ),
    ]
    # print( planner.state.t_ordered )
    # print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )

# block D is on block A, block B is on block C
# move block A on to block B and Block C on to block D
def test_concurrent_stack_blocks_world():
    surfaces = [ Surface( x ) for x in [ "A", "B", "C", "D", "Table" ] ]
    table = [ Table( surfaces[ -1 ] ), ]
    blocks = [ Block( x ) for x in surfaces[ :-1 ] ]
    A, B, C, D = blocks
    TABLE = table[ 0 ]
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=2 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_e, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [
        (t_e, "is_on", A, B, True),
        (t_e, "is_on", C, D, True),
    ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", D, A, True),
            (t_s, "is_on", A, TABLE, True),
            (t_s, "is_on", C, B, True),
            (t_s, "is_on", B, TABLE, True),
        ],
        "clear": [
            (t_s, "clear", C, True),
            (t_s, "clear", D, True),
            (t_s, "clear", TABLE, True),  # always true, simplified some logic
        ],
    }
    t_ordered: List[ int ] = [ t_s, ]
    t_unordered: List[ int ] = [ t_e, ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "is_on": [ ],
        "clear": [ ],
    }

    domain_objects: Dict[ str, List ] = {
        "surfaces": surfaces,
        "table":    table,
        "blocks":   blocks,
    }
    reference_chronicle, value_chronicle = make_blocks_world_chronicle_pair(
            t_ordered,
            t_unordered,
            changes,
            persistences,
            stn,
            domain_objects,
    )
    planner = IPyHOP( temporal_methods_instance, temporal_actions_instance, verbose=3 )
    planner.plan(
            reference_chronicle, goal_lst, methods=temporal_methods_instance,
            actions=temporal_actions_instance,
            value_chronicle=value_chronicle,
            initial_max_depth=5,
            depth_step_size=2,
    )
    # assert planner.state.t_ordered == [ 0, 1, 4, 10, 2 ]
    # assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
    #     ('root',),
    #     (2, 'is_on', 'A', 'B', True),
    #     (1, 'is_on', 'B', 'C', True),
    #     ('TOC', 2),
    #     ('TOC', 1),
    #     ('TOC', 0),
    #     (4, 'clear', 'A', True),
    #     (4, 'clear', 'B', True),
    #     (2, 'is_on', 'A', 'B', True),
    #     ('TOC', 4),
    #     'VerifyGoal',
    #     ('move_block_to_block', (0, 1), 'B', 'Table', 'C'),
    #     'VerifyGoal',
    #     (10, 'clear', 'A', True),
    #     (10, 'clear', 'B', True),
    #     (2, 'is_on', 'A', 'B', True),
    #     ('TOC', 10),
    #     'VerifyGoal',
    #     (
    #         'TSA',
    #         1,
    #         [
    #             (1, 'is_on', 'B', 'A', False),
    #             (1, 'is_on', 'B', 'B', False),
    #             (1, 'is_on', 'B', 'Table', False),
    #             (1, 'is_on', 'A', 'C', False),
    #             (1, 'is_on', 'C', 'C', False),
    #             (1, 'is_on', 'B', 'C', True),
    #             (1, 'clear', 'Table', True),
    #             (1, 'clear', 'C', False),
    #         ],
    #     ),
    #     'VerifyGoal',
    #     'VerifyGoal',
    #     ('move_block_to_block', (4, 2), 'A', 'Table', 'B'),
    #     'VerifyGoal',
    #     (
    #         'TSA',
    #         2,
    #         [
    #             (2, 'is_on', 'A', 'A', False),
    #             (2, 'is_on', 'A', 'C', False),
    #             (2, 'is_on', 'A', 'Table', False),
    #             (2, 'is_on', 'B', 'B', False),
    #             (2, 'is_on', 'C', 'B', False),
    #             (2, 'is_on', 'A', 'B', True),
    #             (2, 'clear', 'Table', True),
    #             (2, 'clear', 'B', False),
    #         ],
    #     ),
    #     'VerifyGoal',
    #     'VerifyGoal',
    # ]
    print( planner.state.t_ordered )
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
