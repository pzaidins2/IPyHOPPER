#!/usr/bin/env python

"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
# from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, List, NewType, Tuple, Union

from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, RestorationTuple,
    TemporalNetwork, ValueChronicle)

# NEEDS TO BE EXPANDED, PLACEHOLDER FOR TYPE CHECKING
# placeholder for temporal goal which is specified as timepoint and a predicate with its args
# and the bool value it should evaluate to at that timepoint
TemporalGoal = Tuple[ int, str, *Tuple[ Any, ... ], bool ]
# lowest level of method-action hierarchy that declares that a list of predicate-arg-bools happens
# at the timepoint, no logic/search when IPyHOPPER reads this it checks that no contradictions
# are introduced
# extra layer helps with concurrent nature of temporal planning
TemporalSingletonAction = Tuple[ int, List[ Tuple[ str, *Tuple[ Any, ... ], bool ] ] ]
# middle level of hierarchy, corresponds to formalism actions
# function given reference and value chronicles and a temporal goal (t,...) returns a list of
# singleton actions (with restoration tuple) that will make said goal true at t
TemporalActionOutput = Tuple[ RestorationTuple, List[ TemporalSingletonAction ] ]
TemporalAction = Callable[
    [ ReferenceChronicle, ValueChronicle, TemporalGoal, ... ], List[ TemporalActionOutput ] ]
# highest level of hierarchy, corresponds to formalism methods
# function given reference and value chronicles and a temporal goal (t,...) returns a itertator
# that returns all valid bindings one at a time  as a list of
# temporal goals and or singleton actions (with restoration tuple)
TemporalMethodOutput = Tuple[ RestorationTuple, List[ Union[ TemporalGoal, TemporalSingletonAction ] ] ]
TemporalMethod = Callable[
    [ ReferenceChronicle, ValueChronicle, TemporalGoal, ... ], Iterator[ List[ TemporalActionOutput ] ] ]


# domain typing
Surface = NewType( "Surface", str )
Block = NewType( "Block", Surface )
Table = NewType( "Table", Surface )


# class TemporalBlocksWorldDomainObjects( Protocol ):
#     blocks: List[ Block ]
#     table: Table
#     surfaces: List[ Surface ]
class BlocksWorldReferenceChronicle( ReferenceChronicle ):
    def __init__(
            self, changes: Dict[ str, int ], t_ordered: int, t_unordered: int,
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
            t_now: int,
            t_ordered: List[ int ],
            t_unordered: List[ int ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, List[ str ] ],
    ):
        super().__init__(
                changes,
                t_now,
                t_ordered,
                t_unordered,
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

# # does nothing
# def tga_move_block_to_table_start(
#         reference_chronicle: BlocksWorldReferenceChronicle,
#         value_chronicle: BlocksWorldValueChronicle,
# ) -> Union[ RestorationTuple, None ]:
#     return (reference_chronicle, ([ ], [ ], [ ]))


# # move block from start_pos to the table at t_end
# def tgs_move_block_to_table_end(
#         reference_chronicle: BlocksWorldReferenceChronicle,
#         value_chronicle: BlocksWorldValueChronicle,
#         temporal_goal: TemporalGoal,
#         block: Block,
#         start_pos: Block,
# ) -> Union[ ActionMethodOutput, None ]:
#     (t_end, *goal) = temporal_goal
#     change_assertion_lst = [
#         (t_end, "is_on", block, start_pos, False),
#         (t_end, "is_on", block, value_chronicle.domain_objects[ "table" ][ 0 ], True),
#     ]
#     change_update_dict: Dict[ str, int ] = { }
#     success_flag = CI.add_changes(
#             reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict,
#     )
#     if success_flag:
#         return ((reference_chronicle, ([ ], [ ], [ ])), [ ])
#
#     CI.restore_chronicle(
#             reference_chronicle, value_chronicle,
#             change_update_dict, { }, ([ ], [ ], [ ]),
#     )
#
#
# # corresponds to pseudoaction move_block_to_block
# # # moves block from start_pos to end_pos
# # def tga_move_block_to_block_start( reference_chronicle: BlocksWorldReferenceChronicle,)
# #     return (reference_chronicle, ([ ], [ ], [ ]))
#
# # move block from start_pos to end_pos at t_end
# def tgs_move_block_to_block_end(
#         reference_chronicle: BlocksWorldReferenceChronicle,
#         value_chronicle: BlocksWorldValueChronicle,
#         t_end: int,
#         block: Block,
#         start_pos: Surface,
#         end_pos: Block,
# ) -> Union[ ActionMethodOutput, None ]:
#     change_assertion_lst = [
#         (t_end, "is_on", block, start_pos, False),
#         (t_end, "is_on", block, end_pos, True),
#     ]
#     change_update_dict: Dict[ str, int ] = { }
#     if CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, { } ):
#         return ((reference_chronicle, ([ ], [ ], [ ])), [ ])
#
#     CI.restore_chronicle(
#             reference_chronicle, value_chronicle,
#             change_update_dict, { }, ([ ], [ ], [ ]),
#     )

# NEED temporal extension of actions
# actions = Actions()
# actions.declare_actions( [ tga_move_block_to_table_start, ] )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
