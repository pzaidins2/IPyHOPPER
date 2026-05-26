#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Dict, List, NewType, Protocol

from ipyhop import Actions, ObjectVarChange, ObjectVarPersistence

# domain typing
Surface = NewType( "Surface", str )
Block = NewType( "Block", Surface )
Table = NewType( "Table", Surface )
# class TemporalBlocksWorldDomainObjects( Protocol ):
#     blocks: List[ Block ]
#     table: Table
#     surfaces: List[ Surface ]
class

actions = Actions()

# # from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
# # corresponds to pseudoaction move_block_to_table
# # tga_move_block_to_table_start checks conditions at t_start
# # tga_move_block_to_table_end check
# def tga_move_block_to_table_start(
#         state_references: State, temporal_network: TemporalNetwork, state_values: TemporalBlocksWorldStateValues,
#         t_start: int, block: Block, start_pos: Block,
# ):
#     object_var_assertion: ObjectVarChange = (t_start, "on", block, start_pos, True)
#     # check assertion and constraints
#     # conditions at t_start are met
#     # [t_start] on(block) = start_pos, start_pos is a block
#     # check that on(block) = start_pos
#     if all(
#             [
#                 type( block ) == Block,
#                 type( start_pos ) == Block,
#                 verify_object_assertion( state_references, state_values, object_var_assertion ),
#             ],
#     ):
#         # this action is t_start and only checks constraints, return
#         return state_references


# NEED temporal extension of actions
# actions.declare_actions( [ tga_move_block_to_table_start, ] )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
