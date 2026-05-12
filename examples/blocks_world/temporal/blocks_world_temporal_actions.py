#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from itertools import groupby
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
    persistences: Dict[ str, List[ ObjectVarPersistence ] ]
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


# add list of change assertions to the state values and update indices as needed
# terminate without altering state values if any change assertion would fail
# returns True on success and False on failure
def add_object_var_changes(
        state_references: TemporalBlocksWorldStateReferences,
        state_values: TemporalBlocksWorldStateValues,
        min_stn: TemporalNetwork, object_var_assertion_lst: List[ ObjectVarAssertion ],
        change_update_dict: Dict[ str, int ],
) -> bool:
    # get dictionaries
    change_value_dict: Dict[ str, List[ ObjectVarAssertion ] ] = state_values.object_var
    persistence_value_dict: Dict[ str, List[ ObjectVarPersistence ] ] = state_values.persistences
    change_reference_dict: Dict[ str, int ] = state_references.object_var
    persistence_reference_dict: Dict[ str, int ] = state_references.persistences

    # check for contradictions in list
    # every member against every other with order not mattering
    # pairwise operations allow separate testing on new additions
    for i in range( len( object_var_assertion_lst ) - 1 ):
        # current assertion
        object_var_assertion: ObjectVarAssertion = object_var_assertion_lst[ i ]
        # don't need reverse of pairs
        new_change_lst: List[ ObjectVarAssertion ] = object_var_assertion_lst[ i + 1: ]
        new_change_index: int = len( new_change_lst )
        safe_flag = check_change_existing_changes_safe( object_var_assertion, new_change_lst, new_change_index )
        if not safe_flag:
            return False
    # iterate over new change assertions for existing change and persistence assertions
    for obj_var_assertion in object_var_assertion_lst:
        # change vs change
        predicate_label: str = obj_var_assertion[ 1 ]
        change_value_lst: List[ ObjectVarAssertion ] = change_value_dict[ predicate_label ]
        change_index: int = change_reference_dict[ predicate_label ]
        safe_flag = check_change_existing_changes_safe( obj_var_assertion, change_value_lst, change_index )
        if not safe_flag:
            return False
        # change vs persistence
        persistence_value_lst: List[ ObjectVarPersistence ] = persistence_value_dict[ predicate_label ]
        persistence_index: int = persistence_reference_dict[ predicate_label ]
        safe_flag = check_change_persistences_safe(
                obj_var_assertion, persistence_value_lst, persistence_index,
                min_stn,
        )
        if not safe_flag:
            return False
    # add new changes to chronicle
    # alter change_update_dict for new object variable changes
    # group changes by predicate label and insert/update as appropriate
    for k, g in groupby( object_var_assertion_lst, key=lambda x: x[ 2 ] ):
        change_value_lst: List[ ObjectVarAssertion ] = change_value_dict[ k ]
        change_index: int = change_reference_dict[ k ]
        # extends (in place) the list with new changes and gives value of updated index
        updated_index: int = safe_list_update( change_value_lst, object_var_assertion_lst, change_index )
        # store only the oldest value (allows rollback if failure occurs later in action if multiple calls)
        if k not in change_update_dict.keys():
            change_update_dict[ k ] = updated_index
    return True


# add list of persistence assertions to the state values and update indices as needed
# terminate without altering state values if any persistence assertion would fail
# updates reference dictionary and state values if successful, no alterations if failed
# on success returns True
# persistence_update_dict: stores original indices before additions
def add_object_var_persistences(
        state_references: TemporalBlocksWorldStateReferences,
        state_values: TemporalBlocksWorldStateValues,
        min_stn: TemporalNetwork, persistence_assertion_lst: List[ ObjectVarPersistence ],
        persistence_update_dict: Dict[ str, int ],
) -> bool:
    # get dictionaries
    change_value_dict: Dict[ str, List[ ObjectVarAssertion ] ] = state_values.object_var
    persistence_value_dict: Dict[ str, List[ ObjectVarPersistence ] ] = state_values.persistences
    change_reference_dict: Dict[ str, int ] = state_references.object_var
    persistence_reference_dict: Dict[ str, int ] = state_references.persistences

    # check for contradictions in list
    # every member against every other with order not mattering
    # pairwise operations allow separate testing on new additions
    for i in range( len( persistence_assertion_lst ) - 1 ):
        # current assertion
        persistence_assertion: ObjectVarPersistence = persistence_assertion_lst[ i ]
        # don't need reverse of pairs
        new_persistence_lst: List[ ObjectVarPersistence ] = persistence_assertion_lst[ i + 1: ]
        new_persistence_index: int = len( new_persistence_lst )
        safe_flag = check_persistence_existing_persistences_safe(
                persistence_assertion, new_persistence_lst, new_persistence_index, min_stn,
        )
        if not safe_flag:
            return False
    # iterate over new persistence assertions for existing persistence and persistence assertions
    for persistence_assertion in persistence_assertion_lst:
        # persistence vs change
        predicate_label: str = persistence_assertion[ 2 ]
        change_value_lst: List[ ObjectVarAssertion ] = change_value_dict[ predicate_label ]
        change_index: int = change_reference_dict[ predicate_label ]
        safe_flag: bool = check_persistence_changes_safe(
                persistence_assertion, change_value_lst, change_index, min_stn,
        )
        if not safe_flag:
            return False
        # persistence vs persistence
        persistence_value_lst: List[ ObjectVarPersistence ] = persistence_value_dict[ predicate_label ]
        persistence_index: int = persistence_reference_dict[ predicate_label ]
        safe_flag: bool = check_persistence_existing_persistences_safe(
                persistence_assertion, persistence_value_lst, persistence_index,
                min_stn,
        )
        if not safe_flag:
            return False
    # add new persistences to chronicle
    # alter persistence_update_dict for new object variable persistences
    # group persistences by predicate label and insert/update as appropriate
    for k, g in groupby( persistence_assertion_lst, key=lambda x: x[ 2 ] ):
        persistence_value_lst: List[ ObjectVarPersistence ] = persistence_value_dict[ k ]
        persistence_index: int = persistence_reference_dict[ k ]
        # extends the list with new persistences and gives value of updated index
        updated_index: int = safe_list_update( persistence_value_lst, persistence_assertion_lst, persistence_index )
        # store only the oldest value (allows rollback if failure occurs later in action if multiple calls)
        if k not in persistence_update_dict.keys():
            persistence_update_dict[ k ] = updated_index
    return True


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
def check_change_existing_changes_safe(
        new_change_assertion: ObjectVarAssertion,
        existing_change_lst: List[ ObjectVarAssertion ],
        existing_change_index: int, min_stn: TemporalNetwork,
) -> bool:
    # only search elements below index
    search_lst: List[ ObjectVarAssertion ] = existing_change_lst[ :existing_change_index + 1 ]
    # remove label and before as they are redundant
    new_generic_change_assertion: GenericObjectVarAssertion = new_change_assertion[ 2: ]
    t_change: int = new_change_assertion[ 0 ]
    negated_new_generic_assertion: GenericObjectVarAssertion = \
        (*new_generic_change_assertion[ :-1 ], not (new_generic_change_assertion[ -1 ]))
    # go through the list
    for obj_var_assert in search_lst:
        generic_change_assertion: GenericObjectVarAssertion = obj_var_assert[ 2: ]
        # check if assertion potentially relevant based on predicate label and args
        if generic_change_assertion == negated_new_generic_assertion:
            t_obj_var_assertion: int = obj_var_assert[ 0 ]
            # if time points can be equal return false
            if not (min_stn.is_strictly_less_than( t_obj_var_assertion, t_change ) or
                    min_stn.is_strictly_less_than( t_change, t_obj_var_assertion )):
                return False
    return True


# returns True if no conflicting persistence exists for the specified change assertion, else False
# conflict exists if t_now >= t_peristence_start and t_now <= t_persistence_end and bool_val contradicts
def check_change_persistences_safe(
        new_change_assertion: ObjectVarAssertion, persistence_lst: List[ ObjectVarPersistence ],
        persistence_index: int, min_stn: TemporalNetwork,
) -> bool:
    # get values for determining relevance
    t_change: int = new_change_assertion[ 0 ]
    new_generic_change_assertion: GenericObjectVarAssertion = new_change_assertion[ 2: ]
    is_strictly_less_than = min_stn.is_strictly_less_than
    # only search elements below index
    search_lst: List[ ObjectVarPersistence ] = persistence_lst[ :persistence_index + 1 ]
    # only persistences for the same predicate label, args, and negated boolean value can conflict
    filtered_search_lst = filter( lambda x: (*x[ 2:-1 ], not (x[ -1 ])) == new_generic_change_assertion, search_lst )
    # ensure that t_change is excluded from being between start and end time points for each remainging persistance
    for persistence in filtered_search_lst:
        t_start: int = persistence[ 0 ]
        t_end: int = persistence[ 1 ]
        # if t_change of the assertion cannot occur in the interval [t_start,t_end]
        # no valid assignment of t_change, t_start, t_end can conflict
        if is_strictly_less_than( t_change, t_start ) or is_strictly_less_than( t_end, t_change ):
            continue
        # there exists 1+ persistence assertions that for some valid assignments of t_change, t_start, t_end
        # would conflict with the new change assertion
        else:
            return False
    return True


# returns true if new persistence assertion would not violate any existing change assertions
def check_persistence_changes_safe(
        new_persistence: ObjectVarPersistence, change_lst: List[ ObjectVarAssertion ],
        change_index: int, min_stn: TemporalNetwork,
) -> bool:
    # get values for determining relevance
    t_start: int = new_persistence[ 0 ]
    t_end: int = new_persistence[ 1 ]
    new_generic_persistence: GenericObjectVarAssertion = new_persistence[ 3: ]
    is_strictly_less_than = min_stn.is_strictly_less_than
    # only search elements below index
    search_lst: List[ ObjectVarAssertion ] = change_lst[ :change_index + 1 ]
    # only change assertions that share a predicate label, args and negated boolean value can clash
    filtered_search_lst = filter( lambda x: (*x[ 1:-1 ], not (x[ -1 ])) == new_generic_persistence, search_lst )
    # ensure that t_change is excluded from being between start and end time points for each remainging persistance
    for change_assert in filtered_search_lst:
        t_change: int = change_assert[ 0 ]
        # if t_change of the assertion cannot occur in the interval [t_start,t_end]
        # no valid assignment of t_change, t_start, t_end can conflict
        if is_strictly_less_than( t_change, t_start ) or is_strictly_less_than( t_end, t_change ):
            continue
        # there exists 1+ change assertions that for some valid assignments of t_change, t_start, t_end
        # would conflict with the new persistence assertion
        else:
            return False
    return True


def check_persistence_existing_persistences_safe(
        new_persistence: ObjectVarPersistence, persistence_lst: List[ ObjectVarPersistence ],
        persistence_index: int, min_stn: TemporalNetwork,
) -> bool:
    # get values for determining relevance
    predicate_label: str = new_persistence[ 2 ]
    t_start_0: int = new_persistence[ 0 ]
    t_end_0: int = new_persistence[ 1 ]
    new_generic_persistence: GenericObjectVarAssertion = new_persistence[ 3: ]
    is_strictly_less_than = min_stn.is_strictly_less_than
    # only search elements below index
    search_lst: List[ ObjectVarPersistence ] = persistence_lst[ :persistence_index + 1 ]
    # only change assertions that share a predicate label, args and negated boolean value can clash
    filtered_search_lst = filter( lambda x: (*x[ 1:-1 ], not (x[ -1 ])) == new_generic_persistence, search_lst )
    # ensure that t_change is excluded from being between start and end time points for each remaining persistence
    for existing_persistence in filtered_search_lst:
        t_start_1: int = existing_persistence[ 0 ]
        t_end_1: int = existing_persistence[ 1 ]
        # forbid intervals that might overlap
        if is_strictly_less_than( t_end_1, t_start_0 ) or is_strictly_less_than( t_end_0, t_start_1 ):
            continue
        # there exists 1+ existing persistence assertions that for some valid assignments of
        # the 4 time points would conflict with the new persistence assertion
        else:
            return False
    return True


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
            ],
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
