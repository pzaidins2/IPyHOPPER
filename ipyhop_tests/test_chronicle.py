#!/usr/bin/env python
"""
File Description: unit testing for methods of ChronicleInterface class in chronicle.py
"""
from typing import Dict, List

from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence,
    ReferenceChronicle, TemporalNetwork, \
    ValueChronicle)

CI = ChronicleInterface()


# classes implementing chronicle protocols
class TrafficReferenceChronicle( ReferenceChronicle ):
    def __init__(
            self, changes: Dict[ str, int ], t_ordered: int, t_unordered: int,
            persistences: Dict[ str, int ],
    ):
        self.changes = changes
        self.t_ordered = t_ordered
        self.t_unordered = t_unordered
        self.persistences = persistences
        super().__init__(
                changes,
                t_ordered,
                t_unordered,
                persistences,
        )


class TrafficValueChronicle( ValueChronicle ):
    def __init__(
            self, changes: Dict[ str, List[ ObjectVarChange ] ],
            t_now: int,
            t_ordered: List[ int ],
            t_unordered: List[ int ],
            persistences: Dict[ str, List[ ObjectVarPersistence ] ],
            temporal_network: TemporalNetwork,
            domain_objects: Dict[ str, List ],
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


# safe_list_update
# appending
def test_safe_list_update_0():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 6
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 8
    assert lst == [ *range( 9 ) ]


# overwrite start
def test_safe_list_update_1():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 0
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 2
    assert lst == [ 6, 7, 8, 3, 4, 5 ]


# overwrite end
def test_safe_list_update_2():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 3
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 5
    assert lst == [ 0, 1, 2, 6, 7, 8 ]


# overwrite end + append
def test_safe_list_update_3():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 4
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 6
    assert lst == [ 0, 1, 2, 3, 6, 7, 8 ]


# overwrite end + append
def test_safe_list_update_4():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 5
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 7
    assert lst == [ 0, 1, 2, 3, 4, 6, 7, 8 ]


# overwrite middle
def test_safe_list_update_5():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 1
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 3
    assert lst == [ 0, 6, 7, 8, 4, 5 ]


# # verify_object_assertion
# # only match
# def test_verify_object_assertion_0():
#     test_change_assertion = (1, "light_color", "green", True)
#     changes: Dict[ str, List[ ObjectVarChange ] ] = {
#         "light_color": [ test_change_assertion, ],
#         "can_go":      [ (0, "can_go", True), ],
#     }
#     t_now: int = 0
#     t_ordered: List[ int ] = [ 0, 1 ]
#     t_unordered: List[ int ] = [ ]
#     persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
#         "light_color": [ ],
#         "can_go":      [ ],
#     }
#     temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
#     temporal_network.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
#     domain_objects: Dict[ str, List ] = { "color": [ "red", "yellow", "green" ] }
#     reference_chronicle, value_chronicle = CI.make_chronicle_pair(
#             TrafficReferenceChronicle, TrafficValueChronicle, changes, t_now, t_ordered,
#             t_unordered, persistences, temporal_network, domain_objects,
#     )
#     assert CI.verify_object_assertion(
#             reference_chronicle, value_chronicle,
#             test_change_assertion, t_ordered,
#     )
#
#
# def test_verify_object_assertion_1():
#     # only negation
#     test_change_assertion = (0, "light_color", "green", True)
#     changes: Dict[ str, List[ ObjectVarChange ] ] = {
#         "light_color": [ (0, "light_color", "green", False), (0, "light_color", "yellow", True) ],
#         "can_go":      [ (0, "can_go", True), ],
#     }
#     t_now: int = 0
#     t_ordered: List[ int ] = [ 0, 1 ]
#     t_unordered: List[ int ] = [ ]
#     persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
#         "light_color": [ ],
#         "can_go":      [ ],
#     }
#     temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
#     temporal_network.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
#     domain_objects: Dict[ str, List ] = { "color": [ "red", "yellow", "green" ] }
#     reference_chronicle, value_chronicle = CI.make_chronicle_pair(
#             TrafficReferenceChronicle, TrafficValueChronicle, changes, t_now, t_ordered,
#             t_unordered, persistences, temporal_network, domain_objects,
#     )
#     assert not (CI.verify_object_assertion(
#             reference_chronicle, value_chronicle,
#             test_change_assertion, t_ordered,
#     ))
#
#
# # later match
# def test_verify_object_assertion_2():
#     test_change_assertion = (1, "light_color", "green", True)
#     changes: Dict[ str, List[ ObjectVarChange ] ] = {
#         "light_color": [ (0, "light_color", "green", True), ],
#         "can_go":      [ (0, "can_go", True), ],
#     }
#     t_now: int = 0
#     t_ordered: List[ int ] = [ 0, 1 ]
#     t_unordered: List[ int ] = [ ]
#     persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
#         "light_color": [ ],
#         "can_go":      [ ],
#     }
#     temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
#     temporal_network.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
#     domain_objects: Dict[ str, List ] = { "color": [ "red", "yellow", "green" ] }
#     reference_chronicle, value_chronicle = CI.make_chronicle_pair(
#             TrafficReferenceChronicle, TrafficValueChronicle, changes, t_now, t_ordered,
#             t_unordered, persistences, temporal_network, domain_objects,
#     )
#     assert CI.verify_object_assertion(
#             reference_chronicle, value_chronicle,
#             test_change_assertion, t_ordered,
#     )
# # later negation
# def test_verify_object_assertion_3():
#     test_change_assertion = (0, "light_color", "green", True)
#     changes: Dict[ str, List[ ObjectVarChange ] ] = {
#         "light_color": [ (0, "light_color", "green", True), (1, "light_color", "green", False), ],
#         "can_go":      [ (0, "can_go", True), ],
#     }
#     t_now: int = 0
#     t_ordered: List[ int ] = [ 0, 1 ]
#     t_unordered: List[ int ] = [ ]
#     persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
#         "light_color": [ ],
#         "can_go":      [ ],
#     }
#     temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
#     temporal_network.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
#     domain_objects: Dict[ str, List ] = { "color": [ "red", "yellow", "green" ] }
#     reference_chronicle, value_chronicle = CI.make_chronicle_pair(
#             TrafficReferenceChronicle, TrafficValueChronicle, changes, t_now, t_ordered,
#             t_unordered, persistences, temporal_network, domain_objects,
#     )
#     assert CI.verify_object_assertion(
#             reference_chronicle, value_chronicle,
#             test_change_assertion, t_ordered,
#     )
# # absent True
# # absent False

# check_change_existing_changes_safe
# safe
# safe, negation at time point with exclusive value
# unsafe, negation at time point
# unsafe, negation at nonexclusive time point

# check_change_persistences_safe
# safe
# safe, negation interval exclusive  before
# safe, negation interval exclusive after
# unsafe, at endpoint of negation interval
# unsafe, at startpoint of negation interval
# unsafe, within negation interval
# unsafe, potentially within negation interval

# check_persistence_changes_safe
# safe
# safe, negation at time point with exclusive value
# unsafe, negation at time point
# unsafe, negation at nonexclusive time point

# check_persistence_existing_persistences_safe
# safe
# safe, negation interval exclusive  before
# safe, negation interval exclusive after
# unsafe, start point at endpoint of negation interval
# unsafe, end point at startpoint of negation interval
# unsafe, within negation interval
# unsafe, potentially within negation interval

# add_changes
# safe
# new-new contradiction
# new-existing changes contradiction
# new-existing persistences contradiction

# add_persistences
# safe
# new-new contradiction
# new-existing changes contradiction
# new-existing persistences contradiction
"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
