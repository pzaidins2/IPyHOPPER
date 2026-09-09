#!/usr/bin/env python
"""
File Description: gives protocol for references and values in chronicles and functions
for interfacing with them
"""
from copy import deepcopy
from itertools import groupby
from typing import Any, Collection, Dict, List, Optional, Protocol, Tuple, Type, Union

from ipyhop.temporal import TemporalConstraint, TemporalNetwork, TemporalRestorationTuple

# type aliases for object variable change and persistence assertions
ObjectVarChange = Tuple[ int, str, *Tuple[ Any, ... ], bool ]
GenericObjectVarChange = Tuple[ *Tuple[ Any, ... ], bool ]
ObjectVarPersistence = Tuple[ int, int, str, *Tuple[ Any, ... ], bool ]


# skeletons for reference and value chronicles
class ReferenceChronicle( Protocol ):
    changes: Dict[ str, int ]
    # t_now: int
    t_ordered: List[ int ]
    t_unordered: List[ int ]
    persistences: Dict[ str, int ]

    def __init__(
            self, changes: Dict[ str, int ],
            # t_now: int,
            t_ordered: List[ int ], t_unordered: List[ int ],
            persistences: Dict[ str, int ],
    ):
        self.changes = changes
        # self.t_now = t_now
        self.t_ordered = t_ordered
        self.t_unordered = t_unordered
        self.persistences = persistences

    def copy(self):
        return deepcopy( self )


class ValueChronicle( Protocol ):
    changes: Dict[ str, List[ ObjectVarChange ] ]
    # t_now: int
    # t_ordered: List[ int ]
    # t_unordered: List[ int ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ]
    temporal_network: TemporalNetwork
    domain_objects: Dict[ str, Collection ]

    def __init__(
            self, changes: Dict[ str, List[ ObjectVarChange ] ],
            # t_now: int,
            # t_ordered: List[ int ],
            # t_unordered: List[ int ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, Collection ],
    ):
        self.changes = changes
        # self.t_now = t_now
        # self.t_ordered = t_ordered
        # self.t_unordered = t_unordered
        self.persistences = persistences
        self.temporal_network = temporal_network
        self.domain_objects = domain_objects


# given the reference chronicle and the temporal restoration tuple of the previous node visited, rollback is possible
RestorationTuple = Tuple[ ReferenceChronicle, TemporalRestorationTuple ]
'''
note: we handle time points by integer label rather than temporal value
state description
value_chronicle: contains lists corresponding to indices in state_references (this is curried in action/method 
functions)
    changes: consists of lists of object variable temporal assignments
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
reference_chronicle: everything but time points are by reference (this is passed through State object)
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


# class for manipulating and querying chronicle reference/value pairs
class ChronicleInterface():

    def __init__(self):
        return

    # given a time point and separation condition, removes the time point from unordered time points
    # adds the time point to ordered time points, and updates the temporal network based
    # on separation condition (== or <)
    # returns a tuple where index 0 is a bool indicating success and index 1 is the temporal restoration tuple
    # needed to undo stn changes (empty if fails)
    def order_time_point(
            self, reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle, time_point: int,
            separation_condition: str,
    ) -> Tuple[ bool, TemporalRestorationTuple ]:

        # localize variables
        t_ordered: List[ int ] = reference_chronicle.t_ordered
        t_unordered: List[ int ] = reference_chronicle.t_unordered
        t_ordered_last: int = t_ordered[ -1 ]
        # if len( set( t_unordered ) & set( t_ordered ) ) != 0:
        #     print( "TIME POINT ODDITY" )
        #     print( set( t_unordered ) & set( t_ordered ) )
        #     return (False, ([ ], [ ], [ ]))

        stn: TemporalNetwork = value_chronicle.temporal_network
        # add temporal constraints, end if any fail
        # time point relation to end time point in t_ordered
        anchor_temporal_constraint: TemporalConstraint = (t_ordered_last, separation_condition, time_point, 0)
        # time point must be no later than any time point remaining in t_unordered
        temporal_constraint_lst: List[ TemporalConstraint ] = [ anchor_temporal_constraint, ]
        for unordered_time_point in t_unordered:
            if unordered_time_point != time_point:
                temporal_constraint_lst.append( (time_point, "<=", unordered_time_point, 0) )
        success_flag, node_add_lst, edge_add_lst, edge_remove_lst = stn.add_temporal_constraints_from(
                temporal_constraint_lst,
        )
        # print( "TEMPORAL CONSTRAINT LIST" )
        # print( temporal_constraint_lst )
        # new time points can appear if time points are created unconstrained
        # assert node_add_lst == [ ]
        # at least one contradiction occurs from the new constraints, fail
        if success_flag:
            # add time point to t_ordered
            t_ordered.append( time_point )
            # remove time point from t_unordered
            t_unordered.remove( time_point )

        return (success_flag, (node_add_lst, edge_add_lst, edge_remove_lst))

    # function that initializes a reference-value chronicle pair given the starting values of a chronicle
    # must additionally be given the classes that implement the chronicle protocols
    def make_chronicle_pair(
            self, ReferenceChronicleClass: Type[ ReferenceChronicle ], ValueChronicleClass: Type[ ValueChronicle ],
            t_ordered: List[ int ], t_unordered: List[ int ], changes: Dict[ str, List[ ObjectVarChange ] ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ], temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, Collection ], rigid_relations=None
    ):
        if rigid_relations is None:
            value_chronicle: ValueChronicle = ValueChronicleClass(
                    changes,
                    # t_now, t_ordered, t_unordered,
                    persistences, temporal_network, domain_objects,
            )
        else:
            value_chronicle: ValueChronicle = ValueChronicleClass(
                    changes,
                    # t_now, t_ordered, t_unordered,
                    persistences, temporal_network, domain_objects, rigid_relations,
            )
        changes_len_dict: Dict[ str, int ] = { k: len( v ) for k, v in changes.items() }
        persistences_len_dict: Dict[ str, int ] = { k: len( v ) for k, v in persistences.items() }
        reference_chronicle: ReferenceChronicle = ReferenceChronicleClass(
                changes_len_dict,
                # t_now,
                t_ordered, t_unordered,
                persistences_len_dict,
        )
        return reference_chronicle, value_chronicle

    # call verify_object_assertion on every member of input list
    # end if any fail
    def verify_object_assertion_list(
            self, reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
            change_assertion_list: List[ ObjectVarChange ], offset: int = 0,
    ):
        verify_object_assertion = self.verify_object_assertion
        return all(
                map(
                        lambda x: verify_object_assertion( reference_chronicle, value_chronicle, x, offset=offset ),
                        change_assertion_list,
                ),
        )

    # when all of the following are present the change assertion in question evaluates True
    VerficationConditional = Tuple[ ObjectVarPersistence, ObjectVarChange, List[ TemporalConstraint ] ]

    # Given a pair of reference and value chronicles determine whether the given change assertion must
    # hold given the current facts
    # offset is the time point value from the time point of the given fact to evaluate at
    # a positive offset indicates the fact must hold that many time units in advance of the input change assertion
    # a negative offset indicates the fact must hold that many time units before
    # DOES NOT RETURN TRUE IF ADDITIONAL SEPERATION CONDITIONS WOULD BE REQUIRED, POTENTIAL IMRPOVEMENT
    def verify_object_assertion(
            self, reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
            query_assertion: ObjectVarChange, offset: int = 0,
    ) -> bool:
        # print( "VERIFY START" )
        # print( "QUERY" )
        # print( query_assertion )
        t_query: int = query_assertion[ 0 ]
        predicate_label: str = query_assertion[ 1 ]
        predicate_args: Tuple = query_assertion[ 2:-1 ]
        query_bool: bool = query_assertion[ -1 ]
        min_stn: TemporalNetwork = value_chronicle.temporal_network
        # collect all change assertions that are relevant (same label and args )
        change_assertion_reference_idx: int = reference_chronicle.changes[ predicate_label ]
        change_assertion_lst: List[ ObjectVarChange ] = value_chronicle.changes[ predicate_label ][
            :(change_assertion_reference_idx + 1) ]
        # account for default False
        t_s = reference_chronicle.t_ordered[ 0 ]
        if (t_s, predicate_label, *predicate_args, True) not in change_assertion_lst:
            change_assertion_lst.append( (t_s, predicate_label, *predicate_args, False) )
        # print( "CHANGE ASSERTION LIST" )
        # print( change_assertion_lst )
        # positive or negative exact match, no conditionals needed
        for change_assertion in change_assertion_lst:
            t_i: int = change_assertion[ 0 ]
            # same excluding bool
            offset_bounds = min_stn.get_offset_bounds( t_query, t_i )
            if offset_bounds is not None and offset_bounds[ 0 ] == offset_bounds[ 1 ] and offset_bounds[
                1 ] == offset and change_assertion[
                2:-1 ] == query_assertion[
                2:-1 ]:
                # print( "PRINT EARLY VERIFY END" )
                # exact match
                if query_bool == change_assertion[ -1 ]:
                    # print( True )
                    return True
                # exact negation
                else:
                    # print( False )
                    return False

        # matching predicate args
        matching_change_assertion_lst: List[ ObjectVarChange ] = [
            *filter( lambda x: x[ 2:-1 ] == predicate_args, change_assertion_lst ),
        ]
        offset_bounds_lst: List[ Tuple[ int, int ] ] = [
            *map( lambda x: min_stn.get_offset_bounds( t_query, x ), matching_change_assertion_lst ),
        ]
        # print( "MATCHING CHANGE ASSERTION LIST" )
        # print( matching_change_assertion_lst )
        # exclude every change assertion that must be later than change assertion to be verified
        on_time_assertion_lst: List[ ObjectVarChange ] = [ ]
        for i in range( len( matching_change_assertion_lst ) ):
            change_assertion: ObjectVarChange = matching_change_assertion_lst[ i ]
            offset_bounds: Tuple[ int, int ] = offset_bounds_lst[ i ]
            # only keep change assertions that could potentially occur before query assertion
            if offset_bounds is None or offset_bounds[ 0 ] >= offset:
                on_time_assertion_lst.append( change_assertion )

        # print( "ON TIME ASSERTION LIST" )
        # print( on_time_assertion_lst )

        # filter positive and negative lists to remove cases where duplicate time points that are necessarily
        # equal in value
        unique_value_time_point_lst: List[ int ] = min_stn.unique_value_time_points(
                [ x[ 0 ] for x in on_time_assertion_lst ],
        )
        unique_change_lst: List[ ObjectVarChange ] = [
            *filter( lambda x: x[ 0 ] in unique_value_time_point_lst, list( dict.fromkeys( on_time_assertion_lst ) ) ),
        ]
        # print( "UNIQUE VALUE TIME POINT LIST" )
        # print( unique_value_time_point_lst )
        # print( "UNIQUE CHANGE ASSERTION LIST" )
        # print( unique_change_lst )
        # remove changes that must occur before any other change (across both lists) where that later change
        # cant be later than the query assertion
        relevant_change_lst: List[ ObjectVarChange ] = [ ]
        # each change its time point cant be strictly less than the time point of any change or the second time point
        # is not strictly less than the query
        for i in range( len( unique_change_lst ) ):
            change_assertion_i = unique_change_lst[ i ]
            t_i: int = change_assertion_i[ 0 ]
            keep_assertion = True
            for j in range( len( unique_change_lst ) ):
                if i != j:
                    change_assertion_j = unique_change_lst[ j ]
                    t_j: int = change_assertion_j[ 0 ]
                    offset_bounds_ij: Optional[ Tuple[ int, int ] ] = min_stn.get_offset_bounds( t_i, t_j )
                    if offset_bounds_ij is not None and offset_bounds_ij[ 1 ] < offset:
                        offset_bounds_jq: Optional[ Tuple[ int, int ] ] = min_stn.get_offset_bounds( t_j, t_query )
                        if offset_bounds_jq is not None and offset_bounds_jq[ 1 ] < offset:
                            keep_assertion = False
                            break
            if keep_assertion:
                relevant_change_lst.append( change_assertion_i )
        # print( "RELEVANT CHANGE ASSERTION LIST" )
        # print( relevant_change_lst )
        # at this point all remaining assertion could be the last such change assertion before the
        # query change, if all remaining assertions match the query bool return True else False
        # print( "VERIFY END" )
        if all( x[ -1 ] == query_bool for x in relevant_change_lst ):
            # print( True )
            return True
        else:
            # print( False )
            return False

    # combine add_changes, add_persistences, and add_temporal_constraints_from into single function call
    # defaults to empty change and persistence dicts and temporal restoration tuple
    # if non-empty will restore all built up changes in these
    # if all changes succeed will have updated restoration data structures and returns True
    # if any change fails will rollback everything (including preexisting changes in restoration data structures)
    def update_chronicle(
            self,
            reference_chronicle: ReferenceChronicle,
            value_chronicle: ValueChronicle,
            change_assertion_lst: List[ ObjectVarChange ],
            persistence_assertion_lst: List[ ObjectVarPersistence ],
            temporal_constraint_lst: List[ TemporalConstraint ],
            change_update_dict: Union[ Dict[ str, int ], None ] = None,
            persistence_update_dict: Union[ Dict[ str, int ], None ] = None,
            temporal_restoration_tup: Union[ TemporalRestorationTuple, None ] = None,
    ) -> bool:
        # handle optional args
        change_update_dict: Dict[ str, int ] = { } if change_update_dict is None else change_update_dict
        persistence_update_dict: Dict[ str, int ] = { } if persistence_update_dict is None else persistence_update_dict
        temporal_restoration_tup: TemporalRestorationTuple = (
            [ ], [ ], [ ],
        ) if temporal_restoration_tup is None else temporal_restoration_tup
        # add temporal constraints
        # intervals on new persistences imply,temporal constraints so add those
        # # get unique members, should be order preserving for Python 3.7+
        # unique_interval_tup_lst: List[ Tuple[ int, int ] ] = [ (x[ 0 ], x[ 1 ]) for x in persistence_assertion_lst ]
        # unique_interval_tup_lst = list( dict.fromkeys( unique_interval_tup_lst ) )
        persistence_temporal_constraint_lst: List[ TemporalConstraint ] = [
            (x[ 0 ], "<=", x[ 1 ], 0) for x in filter( lambda y: y[ 0 ] != y[ 1 ], persistence_assertion_lst )
        ]
        min_stn: TemporalNetwork = value_chronicle.temporal_network
        # add temporal constraints included those from implied intervals
        # print( "BEFORE TEMPORAL 0" )
        # print( reference_chronicle )
        temporal_success_0, *current_temporal_restoration_tup = min_stn.add_temporal_constraints_from(
                temporal_constraint_lst + persistence_temporal_constraint_lst,
        )
        min_stn: TemporalNetwork = value_chronicle.temporal_network

        if temporal_success_0:
            # add to restoration tuple
            for i in range( 3 ):
                temporal_restoration_tup[ i ].extend( current_temporal_restoration_tup[ i ] )
            # ensure all new time points are now earlier than t_now
            t_now = reference_chronicle.t_ordered[ -1 ]
            time_point_add_lst: List[ int ] = [ *temporal_restoration_tup[ 0 ] ]
            t_ordered_temporal_constraint_lst: List[ TemporalConstraint ] = [
                (t_now, "<=", x, 0) for x in time_point_add_lst
            ]
            # print( "BEFORE TEMPORAL 1" )
            # print( reference_chronicle )
            temporal_success_1, *current_temporal_restoration_tup = min_stn.add_temporal_constraints_from(
                    t_ordered_temporal_constraint_lst,
            )

            if temporal_success_1:
                # add to restoration tuple
                for i in range( 3 ):
                    temporal_restoration_tup[ i ].extend( current_temporal_restoration_tup[ i ] )
                # add persistence assertions
                # print( "BEFORE PERSISTENCES" )
                # print( reference_chronicle )
                if self.add_persistences(
                        reference_chronicle, value_chronicle,
                        persistence_assertion_lst, persistence_update_dict,
                ):
                    # add change assertions
                    # print( "BEFORE CHANGES" )
                    # print( reference_chronicle )
                    if self.add_changes(
                            reference_chronicle, value_chronicle,
                            change_assertion_lst, change_update_dict,
                    ):
                        # print( "AT RETURN" )
                        # print( reference_chronicle )
                        return True
        # if any alterations fail, rollback everything
        self.restore_chronicle(
                reference_chronicle, value_chronicle, change_update_dict, persistence_update_dict,
                temporal_restoration_tup,
        )
        return False

    # add list of change assertions to the state values and update indices as needed
    # terminate without altering state values if any change assertion would fail
    # returns True on success and False on failure
    def add_changes(
            self,
            reference_chronicle: ReferenceChronicle,
            value_chronicle: ValueChronicle,
            change_assertion_lst: List[ ObjectVarChange ],
            change_update_dict: Dict[ str, int ],
    ) -> bool:
        # localize variables
        min_stn: TemporalNetwork = value_chronicle.temporal_network
        check_change_existing_changes_safe = self.check_change_existing_changes_safe
        check_change_persistences_safe = self.check_change_persistences_safe
        safe_list_update = self.safe_list_update
        # get dictionaries
        change_value_dict: Dict[ str, List[ ObjectVarChange ] ] = value_chronicle.changes
        persistence_value_dict: Dict[ str, List[ ObjectVarPersistence ] ] = value_chronicle.persistences
        change_reference_dict: Dict[ str, int ] = reference_chronicle.changes
        persistence_reference_dict: Dict[ str, int ] = reference_chronicle.persistences

        # check for contradictions in list
        # every member against every other with order not mattering
        # pairwise operations allow separate testing on new additions
        for i in range( len( change_assertion_lst ) - 1 ):
            # current assertion
            change_assertion: ObjectVarChange = change_assertion_lst[ i ]
            # don't need reverse of pairs
            new_change_lst: List[ ObjectVarChange ] = change_assertion_lst[ (i + 1): ]
            new_change_index: int = len( new_change_lst )
            safe_flag = check_change_existing_changes_safe(
                    change_assertion, new_change_lst, new_change_index, min_stn,
            )
            if not safe_flag:
                return False
        # iterate over new change assertions for existing change and persistence assertions
        for obj_var_assertion in change_assertion_lst:
            # change vs change
            predicate_label: str = obj_var_assertion[ 1 ]
            change_value_lst: List[ ObjectVarChange ] = change_value_dict[ predicate_label ]
            change_index: int = change_reference_dict[ predicate_label ]
            safe_flag = check_change_existing_changes_safe( obj_var_assertion, change_value_lst, change_index, min_stn )
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
        for k, v in groupby( change_assertion_lst, key=lambda x: x[ 1 ] ):
            change_value_lst: List[ ObjectVarChange ] = change_value_dict[ k ]
            change_index: int = change_reference_dict[ k ]
            # extends (in place) the list with new changes and gives value of updated index
            updated_index: int = safe_list_update( change_value_lst, [ *v ], change_index )
            # store original index for rollback, passes forward accumulating and tracking the original
            # index before all passes
            if k not in change_update_dict.keys():
                change_update_dict[ k ] = change_index
            # update index in referencer chronicle
            change_reference_dict[ k ] = updated_index
        return True

    # add list of persistence assertions to the state values and update indices as needed
    # terminate without altering state values if any persistence assertion would fail
    # updates reference dictionary and state values if successful, no alterations if failed
    # on success returns True
    # persistence_update_dict: stores original indices before additions
    def add_persistences(
            self,
            reference_chronicle: ReferenceChronicle,
            value_chronicle: ValueChronicle,
            persistence_assertion_lst: List[ ObjectVarPersistence ],
            persistence_update_dict: Dict[ str, int ],
    ) -> bool:
        # localize variables
        min_stn: TemporalNetwork = value_chronicle.temporal_network
        check_persistence_existing_persistences_safe = self.check_persistence_existing_persistences_safe
        check_persistence_changes_safe = self.check_persistence_changes_safe
        safe_list_update = self.safe_list_update
        # get dictionaries
        change_value_dict: Dict[ str, List[ ObjectVarChange ] ] = value_chronicle.changes
        persistence_value_dict: Dict[ str, List[ ObjectVarPersistence ] ] = value_chronicle.persistences
        change_reference_dict: Dict[ str, int ] = reference_chronicle.changes
        persistence_reference_dict: Dict[ str, int ] = reference_chronicle.persistences

        # check for contradictions in list
        # every member against every other with order not mattering
        # pairwise operations allow separate testing on new additions
        for i in range( len( persistence_assertion_lst ) - 1 ):
            # current assertion
            persistence_assertion: ObjectVarPersistence = persistence_assertion_lst[ i ]
            # don't need reverse of pairs
            new_persistence_lst: List[ ObjectVarPersistence ] = persistence_assertion_lst[ (i + 1): ]
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
            change_value_lst: List[ ObjectVarChange ] = change_value_dict[ predicate_label ]
            change_index: int = change_reference_dict[ predicate_label ]
            safe_flag: bool = check_persistence_changes_safe(
                    persistence_assertion, change_value_lst, change_index, min_stn,
            )

            if not safe_flag:
                # print( "PERSISTENCE CHANGES UNSAFE" )
                # print( persistence_assertion )
                # print( change_value_lst )

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
        for k, v in groupby( persistence_assertion_lst, key=lambda x: x[ 2 ] ):
            persistence_value_lst: List[ ObjectVarPersistence ] = persistence_value_dict[ k ]
            persistence_index: int = persistence_reference_dict[ k ]
            # extends the list with new persistences and gives value of updated index
            updated_index: int = safe_list_update( persistence_value_lst, [ *v ], persistence_index )
            # store only the oldest value (allows rollback if failure occurs later in action if multiple calls)
            if k not in persistence_update_dict.keys():
                persistence_update_dict[ k ] = persistence_index
            # update with new values
            persistence_reference_dict[ k ] = updated_index
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
            self,
            new_change_assertion: ObjectVarChange,
            existing_change_lst: List[ ObjectVarChange ],
            existing_change_index: int, min_stn: TemporalNetwork,
    ) -> bool:
        # only search elements below index
        search_lst: List[ ObjectVarChange ] = existing_change_lst[ :existing_change_index + 1 ]
        # remove label and before as they are redundant
        new_generic_change_assertion: GenericObjectVarChange = new_change_assertion[ 2: ]
        t_change: int = new_change_assertion[ 0 ]
        negated_new_generic_assertion: GenericObjectVarChange = \
            (*new_generic_change_assertion[ :-1 ], not (new_generic_change_assertion[ -1 ]))
        # go through the list
        for obj_var_assert in search_lst:
            generic_change_assertion: GenericObjectVarChange = obj_var_assert[ 2: ]
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
            self,
            new_change_assertion: ObjectVarChange, persistence_lst: List[ ObjectVarPersistence ],
            persistence_index: int, min_stn: TemporalNetwork,
    ) -> bool:
        # get values for determining relevance
        t_change: int = new_change_assertion[ 0 ]
        new_generic_change_assertion: GenericObjectVarChange = new_change_assertion[ 2: ]
        is_strictly_less_than = min_stn.is_strictly_less_than
        # only search elements below index
        search_lst: List[ ObjectVarPersistence ] = persistence_lst[ :(persistence_index + 1) ]
        # only persistences for the same predicate label, args, and negated boolean value can conflict
        filtered_search_lst = filter(
                lambda x: (*x[ 3:-1 ], not (x[ -1 ])) == new_generic_change_assertion, search_lst
        )

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
            self,
            new_persistence: ObjectVarPersistence, change_lst: List[ ObjectVarChange ],
            change_index: int, min_stn: TemporalNetwork,
    ) -> bool:
        # get values for determining relevance
        t_start: int = new_persistence[ 0 ]
        t_end: int = new_persistence[ 1 ]
        new_generic_persistence: GenericObjectVarChange = new_persistence[ 3: ]
        is_strictly_less_than = min_stn.is_strictly_less_than
        # only search elements below index
        search_lst: List[ ObjectVarChange ] = change_lst[ :change_index + 1 ]
        # only change assertions that share a predicate label, args and negated boolean value can clash
        filtered_search_lst = [
            *filter( lambda x: (*x[ 2:-1 ], not (x[ -1 ])) == new_generic_persistence, search_lst ),
        ]
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
            self,
            new_persistence: ObjectVarPersistence, persistence_lst: List[ ObjectVarPersistence ],
            persistence_index: int, min_stn: TemporalNetwork,
    ) -> bool:
        # get values for determining relevance
        t_start_0: int = new_persistence[ 0 ]
        t_end_0: int = new_persistence[ 1 ]
        new_generic_persistence: GenericObjectVarChange = new_persistence[ 3: ]
        is_strictly_less_than = min_stn.is_strictly_less_than
        # only search elements below index
        search_lst: List[ ObjectVarPersistence ] = persistence_lst[ :persistence_index + 1 ]
        # only change assertions that share a predicate label, args and negated boolean value can clash
        filtered_search_lst = filter( lambda x: (*x[ 3:-1 ], not (x[ -1 ])) == new_generic_persistence, search_lst )
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

    # bulk insert elements into list overwriting and appending as needed

    # this return the new last_valid_index
    def safe_list_update(self, lst: List, update_element_lst: List, update_start_index: int):
        # size of original list (including garbage)
        lst_size = len( lst )
        assert update_start_index <= len( lst ) and update_start_index >= 0
        # size of update
        update_size = len( update_element_lst )
        # new last valid index
        last_valid_index = update_start_index + update_size
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
            lst.extend( update_element_lst[ i: ] )
        return last_valid_index

    # uses the chronicle update dicts to undo changes by resetting reference chronicle indices and
    # uses the lists of added nodes, added edges, and removed edges to restore temporal network
    def restore_chronicle(
            self,
            reference_chronicle: ReferenceChronicle,
            value_chronicle: ValueChronicle,
            change_update_dict: Dict[ str, int ],
            persistence_update_dict: Dict[ str, int ],
            temporal_rest_tuple: TemporalRestorationTuple,
    ):
        # localize variables
        min_stn: TemporalNetwork = value_chronicle.temporal_network
        # restore temporal graph
        min_stn.restore_graph( *temporal_rest_tuple )
        # restore changes
        reference_chronicle.changes.update( change_update_dict )
        # restore persistences
        reference_chronicle.persistences.update( persistence_update_dict )
        return

    # # pass through to temporal module to add temporal constraints
    # def add_temporal_constraints_from(
    #         self, value_chronicle: ValueChronicle, new_edge_lst: List[ TemporalConstraint ],
    # ) -> Tuple[ bool, List[ int ], List[ NetEdgeInput ], List[ NetEdgeInput ] ]:
    #     return value_chronicle.temporal_network.add_temporal_constraints_from( new_edge_lst )

    # pass through to temporal module to get time point labels
    def get_n_new_time_point_labels(self, value_chronicle: ValueChronicle, n: int) -> List[ int ]:
        return value_chronicle.temporal_network.get_n_new_time_point_labels( n )


# NEED universal low priority methods for advancing time and choosing next timepoint
# NEED actions will need wrapper methods to work for goals
# NEED pseudoactions that are essentially methods that can't be split during repair
"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
