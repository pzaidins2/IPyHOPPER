#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""

from ipyhop import Actions
from typing import NewType, List, Tuple
from ipyhop import State

# typing
Surface = NewType("Surface", str)
Block = NewType("Block", Surface)
Table = NewType("Table", Surface)

'''
note: we handle time points by integer label rather than temporal value
where appropriate we store a list and a last valid index (everything past this index is garbage)
state description
state: ipyhop state object
    object_var: list of tuples (time_point, predicate_name, *predicate_args) where
        predicate_name( *predicate_args ) is true of the state at time_point
    temporal_var: list of tuples (time_point_0, comp_op, int_eval) where time_point_0 is a time point
        comp_op is a comparison operator and int_eval is an expression that evaluates to an int (usually a time point
        or fixed integer)
    t_now: latest time point for which all incoming effects have been resolved
    t_ordered: list of time points such that for all timepoints in the list, no later (in the list)
        time point is earlier (temporal relation) t_ordered[i] <= t_ordered[j] for all i<=j
    t_unordered: unordered list of time points yet to be placed into total ordering
    t_all: unordered list of all time points (t_0 has the label found at t_all[0])
    persistences: list of tuples (t_start, t_end, desired_bool, predicate_name, *predicate_args)
        where for all time points between t_start and t_end (predicate_name, *predicate_args) holds true
        if desired_bool is true else it must hold false
    domain_objects: fixed typing of all domain objects
        blocks: list of all objects of type Blocks
        table: singular table object (type Table)
        surfaces: list of all objects of type Surface
'''

# helper functions
# bulk insert elements into list overwriting and appending as needed
# this return the new last_valid_index
def safe_list_update( lst: List, update_element_lst: List,  update_start_index: int):
    # size of original list (including garbage)
    lst_size = len(lst)
    # size of update
    update_size = len(update_element_lst)
    # new last valid index
    last_valid_index = update_start_index + update_size - 1
    # if list exists at index replace else extend
    for i in range(update_size):
        current_index = update_start_index + i
        # out of bounds add remainder via extend
        if current_index >= lst_size:
            break
        # in bounds insert into existing spot
        lst[current_index] = update_element_lst[i]
    if i < update_size - 1:
        lst.extend(update_element_lst[i:])
    return last_valid_index


#
# actions = Actions()
#
# # from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
# def move_block_to_table( state: State, t_start: int, block: Block, start_pos: Block):
#     # type checking
#     if all([
#         t_start is int,
#         block is Block,
#         start_pos is Block,
#     ]):
#         pass





# actions.declare_actions( [move_block_to_table, ])

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Temporal Blocks World not implemented.")

"""
Author(s): Paul Zzaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
