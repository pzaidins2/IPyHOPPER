#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from typing import Any, Dict, List, NewType, Protocol, Tuple

from ipyhop import Actions, State, TemporalNetwork

# domain typing
Surface = NewType( "Surface", str )
Block = NewType( "Block", Surface )
Table = NewType( "Table", Surface )

type ObjectVarAssertion = Tuple[ int, str, *Tuple[ Any, ... ], bool ]
type GenericObjectVarAssertion = Tuple[ *Tuple[ Any, ... ], bool ]
type ObjectVarPersistence = Tuple[ int, int, str, *Tuple[ Any, ... ], bool ]

class TemporalBlocksWorldDomainObjects( Protocol ):
    blocks: List[ Block ]
    table: Table
    surfaces: List[ Surface ]

class TemporalBlocksWorldStateValues( Protocol ):
    object_var: Dict[ str, List[ ObjectVarAssertion ] ]
    # t_now: int
    t_ordered: List[ int ]
    t_unordered: List[ int ]
    persistences: List[ ObjectVarPersistence ]
    domain_objects: TemporalBlocksWorldDomainObjects


class TemporalBlocksWorldStateReferences( Protocol ):
    object_var: Dict[ str, int ]
    t_now: int
    t_ordered: int
    t_unordered: int
    persistences: Dict[ str, int ]

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
temporal_network: TemporalNetwork class object instance that tracks temporal constraints for consistency. 
    Successful insertions
    of new constraints returns list of nodes added, edges added, and edges removed for when rollback is needed. 
    Failed insertions:
    return the network prior to last batch of added constraints. (this is curried in action/method functions)
state_values: contains lists corresponding to indices in state_references (this is curried in action/method functions)
Note: rollbacks of values in State object are automatically handled by IPyHOP but involve deep copying. Additional 
mechanisms
must be added to roll back everything else.
'''
'''
should attempt the following in order
1) resolve goal -> 
pre: action achieves goal at t_now
effect: removes goal and add persistence condition from t_now to t_goal
2) decompose goal -> 
pre: method for goal exists and would not add persistence condition contradiction
effect: removes goal, add new goals (with preexisting or new timepoints), add method persistence conditions
3) place new timepoint in ordering -> 
pre: time point that could be after last time point in ordering exists and no time
point not in ordering must be before the candidate time point, no goal for last ordered time point can be open
effect: candidate time point appended to ordering, adds t_candidate <= t_i for t_i in t_unordered
4) advance t_now ->
pre: time point that could be after last time point in ordering exists and no time
point not in ordering must be before the candidate time point, no goal for last ordered time point can be open, and
goal for candidate time point exists
effect: candidate time point appended to ordering, t_last < t_candidate added as temporal constraint,
t_now set equal to candidate time point, adds t_candidate <= t_i for t_i in t_unordered

each of these choices is a decision point
if deadend is reached, backtrack to previous decision point
if deadend is reached and not previous decision point exists there is no solution

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
    i = 0
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
# ASSUMPTION: assertions inserted in same order as t_ordered
def verify_object_assertion(
        state_references: TemporalBlocksWorldStateReferences, state_values: TemporalBlocksWorldStateValues,
        object_var_assertion: ObjectVarAssertion,
):
    # object variable assertion without time
    generic_assertion: GenericObjectVarAssertion = object_var_assertion[ 2:-1 ]
    # object variable assertion negated
    negated_generic_assertion: GenericObjectVarAssertion = (*generic_assertion[ :-1 ], not (generic_assertion[ -1 ]))
    # predicate to search
    predicate_label: str = object_var_assertion[ 1 ]
    # list to be searched (cutoff based on reference index)
    # assertions are placed in order of t_ordered
    search_lst: List[ ObjectVarAssertion ] = \
        state_values.object_var[ predicate_label ][ :state_references.object_var[ predicate_label ] ]
    # iterate over list in reverse
    for obj_var_assert in reversed( search_lst ):
        generic_this: GenericObjectVarAssertion = (obj_var_assert[ 1 ], *obj_var_assert[ 2: ])
        if generic_this == negated_generic_assertion:
            return False
        elif generic_this == generic_assertion:
            return True
    return False


# add change assertions to state values of object_var and update state reference indices
def add_object_var_changes():
    # safe_list_add()
    pass


# add persistence assertions to state values of persistences and update persistence reference indices
def add_object_var_persistences():
    # safe_list_add()
    pass


# returns true if the negation of the given object var assertion does not exist else False
# if [t_now] (foo, bar, True) is the new assertion THEN
# if [t_now] (foo, bar, True) is in the existing changes then True
# if [t_i] (foo, bar, True) is in the existing changes AND [t_j] (foo, bar, False) is not where t_i<=t_j<=t_now then
# True

# if [t_now] (foo,bar, False) is the new assertion
# if [t_now] (foo, bar, False) is in the existing changes then True
# if [t_i] (foo, bar, False) is in the existing changes AND [t_j] (foo, bar, True) is not where t_i<=t_j<=t_now then
# True
# additionally the absence of (foo, bar, _) is the same as [t_start] (foo, bar, False)
# assumes the first instance of (_,predicate_label,*new_change_args[:-1],_ is the relevant one
def check_change_existing_changes_safe(
        new_change_assertion: ObjectVarAssertion,
        existing_change_dict: Dict[ str, List[ ObjectVarAssertion ] ], existing_change_index_dict: Dict[ str, int ],
) -> bool:
    # get list of relevant assertion by predicate label
    predicate_label: str = new_change_assertion[ 1 ]
    search_lst: List[ ObjectVarAssertion ] = existing_change_dict[ predicate_label ][
        :existing_change_index_dict[ predicate_label ] ]
    # remove label and before as they are redundant
    new_generic_change_assertion: GenericObjectVarAssertion = new_change_assertion[ 2: ]
    negated_new_generic_assertion: GenericObjectVarAssertion = \
        (*new_generic_change_assertion[ :-1 ], not (new_generic_change_assertion[ -1 ]))
    # go through the list in reverse
    for obj_var_assert in reversed( search_lst ):
        generic_change_assertion: GenericObjectVarAssertion = obj_var_assert[ 2: ]
        # first match is the same as new assertion return True
        if generic_change_assertion == new_generic_change_assertion:
            return True
        # first match is the negation of the new assertion return False
        elif generic_change_assertion == negated_new_generic_assertion:
            return False
    # if no matches then default value is False
    if new_change_assertion[ -1 ] == False:
        return True
    else:
        return False


# returns True if no conflicting persistence exists for the specified change assertion, else False
# conflict exists if t_now >= t_peristence_start and t_now <= t_persistence_end and bool_val contradicts
def check_change_persistences_safe(
        new_change_assertion: ObjectVarAssertion, persistences_dict: Dict[ str, List[ ObjectVarPersistence ] ],
        persistences_index_dict: Dict[ str, int ], min_stn: TemporalNetwork
) -> bool:
    # get values for determining relevance
    predicate_label: str = new_change_assertion[ 1 ]
    t_change: int = new_change_assertion[ 0 ]
    new_generic_change_assertion: GenericObjectVarAssertion = new_change_assertion[ 2: ]
    # get list of relevant persistences by predicate label
    search_lst: List[ ObjectVarPersistence ] = persistences_dict[ predicate_label ][
        :persistences_index_dict[ predicate_label ] ]
    # returns True if potential conflict based on label and args
    filtered_search_lst = filter( lambda x: (*x[ 2:-1 ], not (x[ -1 ])) == new_generic_change_assertion, search_lst )
    # ensure that t_change is excluded from being between start and end time points for each remainging persistance
    for persistence in filtered_search_lst:
        t_start: int = persistence[ 0 ]
        t_end: int = persistence[ 1 ]


def check_persistence_assertions_safe():
    pass


def check_persistence_existing_persistences_safe():
    pass


# NEED universal low priority methods for advancing time and choosing next timepoint
# NEED actions will need wrapper methods to work for goals
# NEED pseudoactions that are essentially methods that can't be split during repair

actions = Actions()


# from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
# corresponds to pseudoaction move_block_to_table
# tga_move_block_to_table_start checks conditions at t_start
# tga_move_block_to_table_end check
def tga_move_block_to_table_start(
        state_references: State, temporal_network: TemporalNetwork, state_values: TemporalBlocksWorldStateValues,
        t_start: int, block: Block, start_pos: Block,
):
    object_var_assertion: ObjectVarAssertion = (t_start, "on", block, start_pos, True)
    # check assertion and constraints
    # conditions at t_start are met
    # [t_start] on(block) = start_pos, start_pos is a block
    # check that on(block) = start_pos
    if all(
            [
                type( block ) == Block,
                type( start_pos ) == Block,
                verify_object_assertion( state_references, state_values, object_var_assertion ),
            ]
    ):
        # this action is t_start and only checks constraints, return
        return state_references


# NEED temporal extension of actions
actions.declare_actions( [ tga_move_block_to_table_start, ] )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError( "Test run / Demo routine for Temporal Blocks World not implemented." )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
