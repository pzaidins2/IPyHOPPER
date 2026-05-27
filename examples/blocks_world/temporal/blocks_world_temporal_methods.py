#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Dict, List, Union

from blocks_world_temporal_actions import ActionMethodOutput, Block, Surface, TemporalGoal
from ipyhop import (ChronicleInterface, Methods, ObjectVarPersistence, ReferenceChronicle, TemporalConstraint,
    ValueChronicle)

methods = Methods()

CI = ChronicleInterface()

# progress stack
def tgm_progress_stack( t_s: int, t_e: int, state_ptrs, state, top_block: Block, bot_block: Block ):

    pass

# clear block
def tgm_clear_block( t_s: int, t_e: int,  state_ptrs, state, goal_block: Block,
                     obstacle_block: Block, other_surface: Surface ):
    pass


# move block to table
def tgm_move_block_to_table(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle, goal: TemporalGoal,
        block: Block, start_pos: Block,
) -> Union[ ActionMethodOutput, None ]:
    # initialization
    persistence_update_dict: Dict[ str, int ] = { }
    change_update_dict: Dict[ str, int ] = { }
    t_end: int = goal[ 0 ]

    (t_start,) = value_chronicle.temporal_network.get_n_new_time_point_labels( 1 )
    # add temporal constraints
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_start, "==", t_end, 1),
    ]
    success_flag, *temporal_rest_tuple = CI.add_temporal_constraints_from(
            value_chronicle, temporal_constraint_lst,
    )
    if success_flag:
        # add persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_start, t_end, "clear", block, True),
        ]
        if CI.add_persistences( reference_chronicle, value_chronicle,
                persistence_assertion_lst, persistence_update_dict ):
            return

    CI.restore_chronicle(
            reference_chronicle, value_chronicle, change_update_dict,
            persistence_update_dict, temporal_rest_tuple,
    )


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
