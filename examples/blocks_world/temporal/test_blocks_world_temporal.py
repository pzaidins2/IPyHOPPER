#!/usr/bin/env python
"""
File Description: unit testing for temporal blocks world domain
"""
from typing import Dict, List, Tuple

from examples.blocks_world.temporal.blocks_world_temporal_actions import Block, Surface, Table, \
    temporal_actions_instance
from examples.blocks_world.temporal.blocks_world_temporal_methods import TemporalActionCall, temporal_methods_instance
from ipyhop import (ChronicleInterface, IPyHOP, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, State,
    TemporalGoal, TemporalNetwork, ValueChronicle)

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
    t_s = stn.get_n_new_time_point_labels( 1 )[ 0 ]
    stn.add_temporal_constraints_from(
            [ ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_s, "clear", A, True), ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [ ],
        "clear": [
            (t_s, "clear", A, True),
        ],
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
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), (0, 'clear', 'A', True), ('TOC', 0),
    ]


# completed multiple goals
def test_many_goal_done_blocks_world():
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

    goal_lst: List[ TemporalGoal ] = [ (t_s, "clear", A, True), (t_s, "is_on", A, B, True) ]
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "is_on": [
            (t_s, "is_on", A, B, True),
        ],
        "clear": [
            (t_s, "clear", A, True),
        ],
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
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), (0, 'clear', 'A', True), (0, 'is_on', 'A', 'B', True), ('TOC', 0),
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
        ("move_block_to_table", (t_e, "is_on", A, TABLE, True), A, B),
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
    assert [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] == [
        ('root',), ('move_block_to_table', (1, 'is_on', 'A', 'Table', True), 'A', 'B'), ('TOC', 1), ('TOC', 0),
        ('TSA', 1, [ (1, 'is_on', 'A', 'B', False), (1, 'is_on', 'A', 'Table', True) ]), ('TOC', 3),
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
    stn: TemporalNetwork = TemporalNetwork( t_min=0, t_max=5 )
    t_s, t_e = stn.get_n_new_time_point_labels( 2 )
    stn.add_temporal_constraints_from(
            [
                (t_s, "<", t_e, 0),
            ],
    )

    goal_lst: List[ TemporalGoal ] = [ (t_e, "is_on", A, TABLE, True) ]
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
    print( [ planner.sol_tree.nodes[ x ][ "info" ] for x in planner.sol_tree.nodes ] )


# blocks A and B start on table, move block A on to block B

# block B starts on block A, flip positions

# blocks A, B, and C start on table
# stack A on B on C

# blocks A and B are on the table, block C is on block B
# stack A on B on C

# block D is on block A, block B is on block C
# move block A on to block B and Block C on to block D

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
