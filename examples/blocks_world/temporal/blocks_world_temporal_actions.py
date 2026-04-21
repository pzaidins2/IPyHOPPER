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

type ObjectVarAssertion = Tuple[ int, str, *Tuple[ Any, ... ], bool ]
type GenericObjectVarAssertion = Tuple[ str, *Tuple[ Any, ... ], bool ]
type ObjectVarPersistence = Tuple[ int, int, str, *Tuple[ Any, ... ], bool ]


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
    current_index = -1
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


# given state specified by state_references and state_values find whether object_var_assertion
# is true
# this happens if object_var[1:] is found at a time point before object_var[0] and the negation is not
def check_object_assertion(
        state_references: State, state_values: TemporalBlocksWorldStateValues,
        object_var_assertion: ObjectVarAssertion,
):
    # object variable assertion without time
    generic_assertion: GenericObjectVarAssertion = (object_var_assertion[ 1 ], *object_var_assertion[ 2: ])
    # object variable assertion negated
    negated_generic_assertion: GenericObjectVarAssertion = (*generic_assertion, not (generic_assertion[ -1 ]))
    # predicate to search
    predicate_label: str = generic_assertion[ 0 ]
    # list to be searched (cutoff based on reference index
    # assertions are placed in order of t_ordered
    search_lst: List[ ObjectVarAssertion ] = \
        state_values.__getattribute__( predicate_label )[ :state_references.__getattribute__( predicate_label ) ]
    # iterate over list in reverse
    for obj_var_assert in reversed( search_lst ):
        generic_this: GenericObjectVarAssertion = (obj_var_assert[ 1 ], *obj_var_assert[ 2: ])
        if generic_this == negated_generic_assertion:
            return False
        elif generic_this == generic_assertion:
            return True
    return False

# ADD universal low priority methods for advancing time and choosing next timepoint
# NEED actions will need wrapper methods to work for goals

actions = Actions()


# from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
def tga_move_block_to_table_start(
        state_references: State, temporal_network: TemporalNetwork, state_values: TemporalBlocksWorldStateValues,
        t_start: int, block: Block, start_pos: Block,
):
    object_var_assertion: ObjectVarAssertion = (t_start, "on", block, start_pos, True)
    # check assertion and constraints
    if all(
            [
                type( block ) == Block,
                type( start_pos ) == Block,
                check_object_assertion( state_references, state_values, object_var_assertion ),
            ]
    ):
        # this action is t_start and only checks constraints, return
        return state_references


# conditions at t_start are met
# [t_start] on(block) = start_pos, start_pos is a block
# check that on(block) = start_pos


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
