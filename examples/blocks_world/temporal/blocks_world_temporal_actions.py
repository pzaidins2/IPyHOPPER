#!/usr/bin/env python

"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from itertools import groupby
# from __future__ import annotations
from typing import Dict, List, NewType, Tuple

from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, RestorationTuple,
    TemporalAction, TemporalActionOutput, TemporalActions, TemporalConstraint, TemporalGoal, TemporalNetwork,
    TemporalRestorationTuple, TemporalSingletonAction, ValueChronicle)

# domain typing
Surface = NewType( "Surface", str )
Block = NewType( "Block", Surface )
Table = NewType( "Table", Surface )
IsOnGoal = Tuple[ int, str, Block, Surface, bool ]
ClearGoal = Tuple[ int, str, Surface, bool ]

# # take change assertion list and turn into singleton action list
# def change_assertion_lst_to_singleton_action_lst(
#         change_assertion_lst: List[ ObjectVarChange ],
# ) -> List[ TemporalSingletonAction ]:
#     singleton_action_lst: List[ TemporalSingletonAction ] = [ ]
#     for k, v in groupby( change_assertion_lst, key=lambda x: x[ 0 ] ):
#         singleton_action = (k, change_format( v ))
#         singleton_action_lst.append( singleton_action )
#     return singleton_action_lst
#
# # alter groupby groups to fit format
# def change_format(group: Iterator[ ObjectVarChange ]) -> List[ Tuple[ str, *Tuple[ Any, ... ], bool ] ]:
#     more_formatted_lst: List[ Tuple[ str, *Tuple[ Any, ... ], bool ] ] = [ ]
#     for item in group:
#         more_formatted_lst.append( (item[ 1 ], item[ 2:-1 ], item[ -1 ]) )
#     return more_formatted_lst


# class TemporalBlocksWorldDomainObjects( Protocol ):
#     blocks: List[ Block ]
#     table: Table
#     surfaces: List[ Surface ]
class BlocksWorldReferenceChronicle( ReferenceChronicle ):
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


class BlocksWorldValueChronicle( ValueChronicle ):
    def __init__(
            self, changes: Dict[ str, List[ ObjectVarChange ] ],
            # t_now: int,
            # t_ordered: List[ int ],
            # t_unordered: List[ int ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, List[ str ] ],
    ):
        super().__init__(
                changes,
                # t_now,
                # t_ordered,
                # t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )


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

# action for moving block from being on block start_pos to the table
MoveBlockToTableCall = Tuple[ str, IsOnGoal, Block, Block ]
def move_block_to_table(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle, t_s: int,
        temporal_goal: TemporalGoal, block: Block, start_pos: Block,
) -> TemporalActionOutput:
    # localize variables
    t_e, *goal = temporal_goal
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    # change assertions
    change_assertion_lst: List[ ObjectVarChange ] = [
        (t_e, "is_on", block, start_pos, False),
        (t_e, "is_on", block, table, True),
    ]
    # persistence assertions
    persistence_assertion_lst: List[ ObjectVarPersistence ] = [
        (t_s, t_e, "clear", block, True),
    ]
    # temporal assertions
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_e, "==", t_s, 1),
    ]
    temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
    # attempt to add all
    if CI.update_chronicle(
            reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
            temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
    ):
        # define list of singleton actions
        restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
        singleton_action_lst: List[ TemporalSingletonAction ] = [ ]
        for k, v in groupby( change_assertion_lst, key=lambda x: x[ 0 ] ):
            singleton_action_lst.append( ("TSA", k, list( v )) )
        action_output: TemporalActionOutput = (restoration_tup, singleton_action_lst)
        return action_output


# action for moving block from being on block start_pos to block end_pos
MoveBlockToBlockCall = Tuple[ str, IsOnGoal, Block, Surface, Block ]
def move_block_to_block(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle, t_s: int,
        temporal_goal: TemporalGoal, block: Block, start_pos: Surface, end_pos: Block,
) -> TemporalActionOutput:
    # localize variables
    t_e, *goal = temporal_goal
    # change assertions
    change_assertion_lst: List[ ObjectVarChange ] = [
        (t_e, "is_on", block, start_pos, False),
        (t_e, "is_on", block, end_pos, True),
    ]
    # persistence assertions
    persistence_assertion_lst: List[ ObjectVarPersistence ] = [ ]
    # temporal assertions
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_e, "==", t_s, 1),
    ]
    temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
    # attempt to add all
    if CI.update_chronicle(
            reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
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
temporal_actions: List[ TemporalAction ] = [ move_block_to_table, move_block_to_block ]
actions = TemporalActions()
actions.declare_temporal_actions( temporal_actions )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
