#!/usr/bin/env python
"""
File Description: unit testing for temporal blocks world domain
"""
from typing import Dict, List, Tuple

from examples.blocks_world.temporal.blocks_world_temporal_actions import Block, Surface, Table, \
    temporal_actions_instance
from examples.blocks_world.temporal.blocks_world_temporal_methods import temporal_methods_instance
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
    pass


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
                (t_s, "<=", t_e, 0),
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
    assert False


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
