#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""

from ipyhop import Methods
from blocks_world_temporal_actions import Surface, Block, Table
methods = Methods()

# progress stack
def tgm_progress_stack( t_s: int, t_e: int, state_ptrs, state, top_block: Block, bot_block: Block ):

    pass

# clear block
def tgm_clear_block( t_s: int, t_e: int,  state_ptrs, state, goal_block: Block,
                     obstacle_block: Block, other_surface: Surface ):
    pass

# NEED: Temporal extension of Goal type: has goal predicate name and time point
methods.declare_goal_methods('on', [tgm_progress_stack])
methods.declare_goal_methods('clear', [tgm_progress_stack])

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Temporal Blocks World not implemented.")

"""
Author(s): Paul Zzaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
