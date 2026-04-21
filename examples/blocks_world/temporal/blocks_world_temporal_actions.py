#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Any, List, NewType, Protocol, Tuple

from ipyhop import Actions, State, TemporalNetwork

# domain typing
Surface = NewType( "Surface", str )
Block = NewType( "Block", Surface )
Table = NewType( "Table", Surface )

ObjectVarAssertion = Tuple[ int, *Tuple[ Any, ... ], bool ]
ObjectVarPersistence = Tuple[ int, int, *Tuple[ Any, ... ], bool ]


class TemporalBlocksWorldDomainObjects( Protocol ):
    blocks: List[ Block ]
    table: Table
    surfaces: List[ Surface ]


class TemporalBlocksWorldStateValues( Protocol ):
    object_var: List[ ObjectVarAssertion ]
    t_now: int
    t_ordered: List[ int ]
    t_unordered: List[ int ]
    persistences: List[ ObjectVarPersistence ]
    domain_objects: TemporalBlocksWorldDomainObjects


'''
note: we handle time points by integer label rather than temporal value
state description
state_references: everything but time points are by reference (this is passed through State object)
    object_var: consists of lists of object variable temporal assignments
        for each predicate 
        predicate_name: list of tuples (tp, *predicate_args, bool_val) where predicate_name(*predicate_args) 
        evaluates bool_val (True or False) as of time point tp, the absence of predicate_args implies bool_val is 
        False          
    t_now: the latest timepoint for which there can be no further assignment statements added, it is always in t_ordered
        but might not be the last time point in t_ordered, all timepoints in t_ordered after t_now are assumed equal to
        t_now until t_now is advanced
    t_ordered: list of time points such that for all timepoints in the list, no later (in the list)
        time point is earlier (temporal relation) t_ordered[i].value <= t_ordered[j].value for all i<=j
    t_unordered: unordered list of time points yet to be placed into total ordering
    persistences: consists of lists of object variable restrictions
        for each predicate
        predicate_name: list of tuples (tp_s, tp_e, *predicate_args, bool_val) where predicate_name(*predicate_args) 
        must evaluate as bool_val (True or False) for all time points inclusive contained by tp_s and tp_e
    domain_objects: fixed typing of all domain objects
        blocks: list of all objects of type Blocks
        table: singular table object (type Table)
        surfaces: list of all objects of type Surface 
temporal_network: TemporalNetwork class object instance that tracks temporal constraints for consistency. Successful 
insertion
    of new constraints returns list of nodes added, edges added, and edges removed for when rollback is needed. 
    Failed insertions
    return the network prior to last batch of added constraints. (this is curried in action/method functions)
state_values: contains lists corresponding to indices in state_references (this is curried in action/method functions)
Note: rollbacks of values in State object are automatically handled by IPyHOP but involve deep copying. Additional 
mechanisms
must be added to roll back everything else.
'''


# helper functions
# bulk insert elements into list overwriting and appending as needed
# this return the new last_valid_index
def safe_list_update(lst: List, update_element_lst: List, update_start_index: int):
    # size of original list (including garbage)
    lst_size = len( lst )
    # size of update
    update_size = len( update_element_lst )
    # new last valid index
    last_valid_index = update_start_index + update_size - 1
    # if list exists at index replace else extend
    for i in range( update_size ):
        current_index = update_start_index + i
        # out of bounds add remainder via extend
        if current_index >= lst_size:
            break
        # in bounds insert into existing spot
        lst[ current_index ] = update_element_lst[ i ]
    if current_index >= lst_size:
        print( update_element_lst[ i: ] )
        lst.extend( update_element_lst[ i: ] )
    return last_valid_index


# returns generator that yields potentially relevant variable assignments
# given a list of tuples, the last valid index, and a predicate and list of predicate values return
# the first match going in reverse order of indices
# given (t_0, on, A, B), (t_0, on, B, C), (t_1, on, A, T), (t_1, clear, A)
# the input (on,) would give (t_1, on, A, T) and input (on,B) would
# give (t_0,on,B,C)
# if no pattern match returns empty generator else returns generator for matching pattern
def object_variable_lookup_generator(object_var_lst: List[ Tuple ], last_valid_index: int, pred_pat: Tuple,
                                     t_ordered: List[ int ],
                                     t_now: int):
    # cycle through list in reverse
    for i in reversed( range( last_valid_index + 1 ) ):
        current_tuple = object_var_lst[ i ]
        for j in range( len( pred_pat ) ):
            # break out of inner loop on mismatch
            if current_tuple[ j + 1 ] != pred_pat[ j ]:
                break
            # match found if every arg in pred_pat matched
            if j == len( pred_pat ) - 1:
                # make sure the time point is before t_now in the ordering
                t_then = current_tuple[ 0 ]
                now_index = t_ordered.index( t_now )
                then_index = t_ordered.index( t_then )
                if now_index >= then_index:
                    match = current_tuple
                    yield match


# returns generator which yields potentially relevant temporal constraints
# the following are considered relevant
def temporal_constraint_lookup_generator(temporal_con_lst: List[ Tuple ], last_valid_index: int, temporal_pat: Tuple,
                                         t_ordered: List[ int ], t_now: int):
    # # cycle through list in reverse starting at last valid index
    # for temporal_con in reversed(temporal_con_lst[:last_valid_index+1]):
    #     t_con_0, t_op, t_con_1 = temporal_con
    pass


# check for evaluated predicate contradicting any member of the persistent conditions
# a contradiction requires the current time point to be within the bound of a persistence condition starting and
# ending times with the predicate and predicate arguements matching and the values being different
# only persistence conditions at indices smaller than last valid index count
def persistence_check(pers_con_lst: List[ Tuple ], pers_con_last_val_idx: int,
                      eval_pred: Tuple, t_ordered: List[ int ], t_now: int):
    # iterate in reverse over persistences within last valid index
    for pers_con in reversed( pers_con_lst[ :pers_con_last_val_idx + 1 ] ):
        # check if t_now is within persistence condition bound
        t_start = pers_con[ 0 ]
        t_end = pers_con[ 1 ]
        t_now_idx = t_ordered.index( t_now )
        t_start_idx = t_ordered.index( t_start )
        t_end_idx = t_ordered.index( t_end )
        if t_now_idx >= t_start_idx and t_now_idx <= t_end_idx:
            # check if predicate name and args match
            if eval_pred[ 1:-1 ] == pers_con[ 2:-1 ]:
                # check if value contradicts
                if eval_pred[ -1 ] != pers_con[ -1 ]:
                    return False
    return True


# return true if no contradiction in state would be created by adding new tuple
# object variable 
def contradiction_check(lst_type: str, lst: List[ Tuple ], eval_pred: Tuple, t_ordered: List[ int ], t_now: int):
    if lst_type == "object":
        return object_contradiction_check()
    elif lst_type == "temporal":
        return temporal_contradiction_check()
    else:
        raise ValueError( lst_type + "is not a supported value for the type of list" )


# if an assignment at the time of the predicate exists already, returns False if the value is different else
# returns True
def object_contradiction_check(object_var_lst: List[ Tuple ], last_valid_index: int, pred_pat: Tuple,
                               t_ordered: List[ int ], t_now: int):
    # find any assignment at t_now for the predicate
    rel_obj_gen = object_variable_lookup_generator( object_var_lst, last_valid_index, pred_pat[ :-1 ], t_ordered,
                                                    t_now )
    for rel_obj_var in rel_obj_gen:
        # check if value is different
        if rel_obj_var[ -1 ] != pred_pat[ -1 ]:
            return False
    return True


def temporal_contradiction_check():
    pass


# return true if tuple can be added without contradiction or persistence condition violation
def can_add_assertion():
    if contradiction_check() and persistence_check():
        return True


# given list of assertions check to see if they can all be added without issue
def can_add_all_assertions():

    pass


# get all time points that are plausible candidates for next time point to add to ordering
# find all timepoints that have no timepoint not in t_ordered that must precede them
def next_timepoint_generator():
    pass


# ADD universal low priority methods for advancing time and choosing next timepoint
# NEED actions will need wrapper methods to work for goals

actions = Actions()


# from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
def move_block_to_table(state_references: State, temporal_network: TemporalNetwork,
                        state_values: TemporalBlocksWorldStateValues,
                        temporal_goal: ObjectVarAssertion,
                        t_start: int, block: Block, start_pos: Block, table: Table):
    # retrieve goal values and some checks
    t_end, predicate_label, top_block, bot_block, bool_val = temporal_goal
    # goal is relevant goal and parameters match goal
    if all( [
        predicate_label == "on",
        top_block == block,
        bot_block == start_pos,
        bool_val,
    ] ):
        # simple constraint check
        if all( [
            t_end == t_start + 1,
            start_pos != table,
        ] ):
            # temporal network consistency check
            # t_end == t_start + 1
            temporal_constraint = (t_end, "==", t_start, 1)
            success_flag, node_add_lst, edge_add_lst, edge_remove_lst = temporal_network.add_temporal_constraints_from(
                    [
                        temporal_constraint,
                    ] )
            if success_flag:
                object_var_assertions: List[ ObjectVarAssertion ] = [
                    (t_end, "on", top_block, table, True),
                ]


# Need temporal extension of actions
actions.declare_actions( [ move_block_to_table, ] )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
