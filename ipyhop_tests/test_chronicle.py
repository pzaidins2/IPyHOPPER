#!/usr/bin/env python
"""
File Description: unit testing for methods of ChronicleInterface class in chronicle.py
"""
from typing import Dict, List

from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence,
    ReferenceChronicle, TemporalNetwork, \
    ValueChronicle)

CI = ChronicleInterface()


# UPDATE TO INCLUDE RIGID RELATIONS
# classes implementing chronicle protocols
class TrafficReferenceChronicle( ReferenceChronicle ):
    def __init__(
            self, changes: Dict[ str, int ], t_ordered: int, t_unordered: int,
            persistences: Dict[ str, int ],
    ):
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
    assert last_valid_index == 9
    assert lst == [ *range( 9 ) ]


# overwrite start
def test_safe_list_update_1():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 0
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 3
    assert lst == [ 6, 7, 8, 3, 4, 5 ]


# overwrite end
def test_safe_list_update_2():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 3
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 6
    assert lst == [ 0, 1, 2, 6, 7, 8 ]


# overwrite end + append
def test_safe_list_update_3():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 4
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 7
    assert lst == [ 0, 1, 2, 3, 6, 7, 8 ]


# overwrite end + append
def test_safe_list_update_4():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 5
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 8
    assert lst == [ 0, 1, 2, 3, 4, 6, 7, 8 ]


# overwrite middle
def test_safe_list_update_5():
    lst = [ 0, 1, 2, 3, 4, 5 ]
    update_index = 1
    update_element_lst = [ 6, 7, 8 ]
    last_valid_index = CI.safe_list_update( lst, update_element_lst, update_index )
    assert last_valid_index == 4
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
# safe, empty
def test_check_change_existing_changes_safe_0():
    new_change_assertion: ObjectVarChange = (0, "light_color", "green", True)
    existing_change_lst: List[ ObjectVarChange ] = [ ]
    existing_change_index: int = -1
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert CI.check_change_existing_changes_safe(
            new_change_assertion, existing_change_lst, existing_change_index, min_stn,
    )


# safe, duplicate
def test_check_change_existing_changes_safe_1():
    new_change_assertion: ObjectVarChange = (0, "light_color", "green", True)
    existing_change_lst: List[ ObjectVarChange ] = [ (0, "light_color", "green", True) ]
    existing_change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert CI.check_change_existing_changes_safe(
            new_change_assertion, existing_change_lst, existing_change_index, min_stn,
    )


# safe, negation at time point with exclusive value
def test_check_change_existing_changes_safe_2():
    new_change_assertion: ObjectVarChange = (0, "light_color", "green", True)
    existing_change_lst: List[ ObjectVarChange ] = [ (1, "light_color", "green", False) ]
    existing_change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<", 1, 0) ] )
    assert CI.check_change_existing_changes_safe(
            new_change_assertion, existing_change_lst, existing_change_index, min_stn, )
# unsafe, negation at time point
def test_check_change_existing_changes_safe_3():
    new_change_assertion: ObjectVarChange = (0, "light_color", "green", True)
    existing_change_lst: List[ ObjectVarChange ] = [ (0, "light_color", "green", False) ]
    existing_change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert not CI.check_change_existing_changes_safe(
            new_change_assertion, existing_change_lst, existing_change_index, min_stn,
    )
# unsafe, negation at nonexclusive time point
def test_check_change_existing_changes_safe_4():
    new_change_assertion: ObjectVarChange = (0, "light_color", "green", True)
    existing_change_lst: List[ ObjectVarChange ] = [ (1, "light_color", "green", False) ]
    existing_change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
    assert not CI.check_change_existing_changes_safe(
            new_change_assertion, existing_change_lst, existing_change_index, min_stn, )

# check_change_persistences_safe
# safe, empty
def test_check_change_persistences_safe_0():
    new_change_assertion: ObjectVarChange = (0, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ ]
    persistence_index: int = -1
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )


# safe, matching bool val
def test_check_change_persistences_safe_1():
    new_change_assertion: ObjectVarChange = (0, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", True) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )
    assert CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# safe, negation interval exclusive  before
def test_check_change_persistences_safe_2():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0), (1, "<", 2, 0) ] )

    assert CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# safe, negation interval exclusive after
def test_check_change_persistences_safe_3():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0), (0, ">", 2, 0) ] )

    assert CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# unsafe, at endpoint of negation interval
def test_check_change_persistences_safe_4():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0), (1, "<=", 2, 0) ] )

    assert not CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# unsafe, at startpoint of negation interval
def test_check_change_persistences_safe_5():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [
        (0, 1, "light_color", "yellow", False), (0, 1, "light_color", "green", True),
    ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0), (0, ">=", 2, 0) ] )

    assert not CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# unsafe, within negation interval
def test_check_change_persistences_safe_6():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0), (0, "<", 2, 0), (1, ">", 2, 0) ] )

    assert not CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )
# unsafe, potentially within negation interval
def test_check_change_persistences_safe_7():
    new_change_assertion: ObjectVarChange = (2, "light_color", "yellow", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (0, 1, "light_color", "yellow", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 1, 0) ] )

    assert not CI.check_change_persistences_safe(
            new_change_assertion, persistence_lst,
            persistence_index, min_stn, )

# check_persistence_changes_safe
# safe, empty
def test_persistence_changes_safe_0():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "red", True)
    change_lst: List[ ObjectVarChange ] = [ ]
    change_index: int = -1
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )

    assert CI.check_persistence_changes_safe( new_persistence, change_lst, change_index, min_stn, )


# safe, matching
def test_persistence_changes_safe_1():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "red", True)
    change_lst: List[ ObjectVarChange ] = [ (0, "light_color", "red", True) ]
    change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )

    assert CI.check_persistence_changes_safe( new_persistence, change_lst, change_index, min_stn, )
# safe, negation at time point with exclusive value
def test_persistence_changes_safe_2():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "red", True)
    change_lst: List[ ObjectVarChange ] = [ (1, "light_color", "red", True) ]
    change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (1, ">", 2, 0) ] )

    assert CI.check_persistence_changes_safe( new_persistence, change_lst, change_index, min_stn, )
# unsafe, negation at time point
def test_persistence_changes_safe_3():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "red", True)
    change_lst: List[ ObjectVarChange ] = [ (2, "light_color", "red", True) ]
    change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<", 2, 0) ] )

    assert CI.check_persistence_changes_safe( new_persistence, change_lst, change_index, min_stn, )
# unsafe, negation at nonexclusive time point
def test_persistence_changes_safe_4():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "red", True)
    change_lst: List[ ObjectVarChange ] = [ (1, "light_color", "red", False) ]
    change_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<", 2, 0) ] )
    assert not CI.check_persistence_changes_safe( new_persistence, change_lst, change_index, min_stn, )

# check_persistence_existing_persistences_safe
# safe,empty
def test_persistence_existing_persistences_safe_0():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ ]
    persistence_index: int = -1
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )


# safe, matching
def test_persistence_existing_persistences_safe_1():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", True) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    assert CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# safe, negation interval exclusive  before
def test_persistence_existing_persistences_safe_2():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", True) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 2, 0), (1, "<=", 3, 0), (3, "<", 2, 0) ] )
    assert CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# safe, negation interval exclusive after
def test_persistence_existing_persistences_safe_3():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", True) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 2, 0), (1, "<=", 3, 0), (2, "<", 1, 0) ] )
    assert CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# unsafe, start point at endpoint of negation interval
def test_persistence_existing_persistences_safe_4():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 2, 0), (1, "<=", 3, 0), (0, "==", 3, 0) ] )
    assert not CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# unsafe, end point at startpoint of negation interval
def test_persistence_existing_persistences_safe_5():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from( [ (0, "<=", 2, 0), (1, "<=", 3, 0), (2, "==", 1, 0) ] )
    assert not CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# unsafe, within negation interval
def test_persistence_existing_persistences_safe_6():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from(
            [
                (0, "<=", 2, 0), (1, "<=", 3, 0),
                (0, ">", 1, 0), (2, "<", 3, 0),
            ],
    )
    assert not CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )


# unsafe, contains negation interval
def test_persistence_existing_persistences_safe_7():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from(
            [
                (0, "<=", 2, 0), (1, "<=", 3, 0),
                (0, "<", 1, 0), (2, ">", 3, 0),
            ],
    )
    assert not CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )
# unsafe, potentially within negation interval
def test_persistence_existing_persistences_safe_8():
    new_persistence: ObjectVarPersistence = (0, 2, "light_color", "green", True)
    persistence_lst: List[ ObjectVarPersistence ] = [ (1, 3, "light_color", "green", False) ]
    persistence_index: int = 0
    min_stn: TemporalNetwork = TemporalNetwork( 0, 10 )
    min_stn.add_temporal_constraints_from(
            [
                (0, "<=", 2, 0), (1, "<=", 3, 0),
            ],
    )
    assert not CI.check_persistence_existing_persistences_safe(
            new_persistence, persistence_lst,
            persistence_index, min_stn, )


# add_changes
# safe, empty
def test_add_changes_0():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [ (0, 1, "light_color", "yellow", False) ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    change_assertion_lst = [ ]
    change_update_dict: Dict[ str, int ] = dict()
    assert CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict )

    assert value_chronicle.changes == {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    assert reference_chronicle.changes == {
        "light_color": 1,
        "can_go":      1,
    }
    assert change_update_dict == { }


# safe
def test_add_changes_1():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [ (0, 1, "light_color", "yellow", False) ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    change_assertion_lst = [
        (1, "light_color", "red", False),
        (1, "light_color", "green", True),
        (2, "light_color", "green", False),
        (2, "light_color", "yellow", True),
        (1, "can_go", True),
    ]
    change_update_dict: Dict[ str, int ] = dict()
    assert CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict )
    assert value_chronicle.changes == {
        "light_color": [
            (0, "light_color", "red", True),
            (1, "light_color", "red", False),
            (1, "light_color", "green", True),
            (2, "light_color", "green", False),
            (2, "light_color", "yellow", True),

        ],
        "can_go":      [
            (0, "can_go", False),
            (1, "can_go", True),
        ],
    }
    assert reference_chronicle.changes == {
        "light_color": 5,
        "can_go":      2,
    }
    assert change_update_dict == {
        "light_color": 1,
        "can_go":      1,
    }


# new-new contradiction
def test_add_changes_2():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [ (0, 1, "light_color", "yellow", False) ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    change_assertion_lst = [
        (1, "light_color", "red", False),
        (1, "light_color", "green", True),
        (1, "light_color", "green", False),
        (2, "light_color", "yellow", True),
        (1, "can_go", True),
    ]
    change_update_dict: Dict[ str, int ] = dict()
    assert not CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict )
    assert value_chronicle.changes == {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    assert reference_chronicle.changes == {
        "light_color": 1,
        "can_go":      1,
    }
    assert change_update_dict == { }
# new-existing changes contradiction
def test_add_changes_3():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [ (0, 1, "light_color", "yellow", False) ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    change_assertion_lst = [
        (0, "light_color", "red", False),
        (1, "light_color", "green", True),
        (2, "light_color", "green", False),
        (2, "light_color", "yellow", True),
        (1, "can_go", True),
    ]
    change_update_dict: Dict[ str, int ] = dict()
    assert not CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict )
    assert value_chronicle.changes == {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    assert reference_chronicle.changes == {
        "light_color": 1,
        "can_go":      1,
    }
    assert change_update_dict == { }
# new-existing persistences contradiction
def test_add_changes_4():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [ (0, 1, "light_color", "yellow", False) ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    change_assertion_lst = [
        (1, "light_color", "red", False),
        (1, "light_color", "green", True),
        (2, "light_color", "green", False),
        (1, "light_color", "yellow", True),
        (1, "can_go", True),
    ]
    change_update_dict: Dict[ str, int ] = dict()
    assert not CI.add_changes( reference_chronicle, value_chronicle, change_assertion_lst, change_update_dict )
    assert value_chronicle.changes == {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    assert reference_chronicle.changes == {
        "light_color": 1,
        "can_go":      1,
    }
    assert change_update_dict == { }

# add_persistences
# safe, empty
def test_add_persistences_0():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),
        ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    persistence_assertion_lst: List[ ObjectVarPersistence ] = [ ]
    persistence_update_dict: Dict[ str, int ] = dict()
    assert CI.add_persistences(
            reference_chronicle, value_chronicle, persistence_assertion_lst, persistence_update_dict,
    )

    assert value_chronicle.persistences == {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),

        ],
        "can_go":      [ ],
    }
    assert reference_chronicle.persistences == {
        "light_color": 2,
        "can_go":      0,
    }
    assert persistence_update_dict == { }
# safe
def test_add_persistences_1():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),
        ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    persistence_assertion_lst: List[ ObjectVarPersistence ] = [
        (0, 1, "light_color", "green", False), (1, 2, "light_color", "red", False),
    ]
    persistence_update_dict: Dict[ str, int ] = dict()
    assert CI.add_persistences(
            reference_chronicle, value_chronicle, persistence_assertion_lst, persistence_update_dict,
    )

    assert value_chronicle.persistences == {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),
            (0, 1, "light_color", "green", False),
            (1, 2, "light_color", "red", False),

        ],
        "can_go":      [ ],
    }
    assert reference_chronicle.persistences == {
        "light_color": 4,
        "can_go":      0,
    }
    assert persistence_update_dict == { "light_color": 2 }
# new-new contradiction
def test_add_persistences_2():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [
            (0, "light_color", "red", True),

        ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),
        ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    persistence_assertion_lst: List[ ObjectVarPersistence ] = [
        (1, 2, "light_color", "yellow", True),
        (1, 2, "light_color", "yellow", False),
    ]
    persistence_update_dict: Dict[ str, int ] = dict()
    assert not CI.add_persistences(
            reference_chronicle, value_chronicle, persistence_assertion_lst, persistence_update_dict,
    )

    assert value_chronicle.persistences == {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),

        ],
        "can_go":      [ ],
    }
    assert reference_chronicle.persistences == {
        "light_color": 2,
        "can_go":      0,
    }
    assert persistence_update_dict == { }
# new-existing changes contradiction
def test_add_persistences_3():
    changes: Dict[ str, List[ ObjectVarChange ] ] = {
        "light_color": [ ],
        "can_go":      [
            (0, "can_go", False),
        ],
    }
    t_now: int = 2
    t_ordered: List[ int ] = [ 0, 1 ]
    t_unordered: List[ int ] = [ 2 ]
    persistences: Dict[ str, List[ ObjectVarPersistence ] ] = {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),
        ],
        "can_go":      [ ],
    }
    temporal_network: TemporalNetwork = TemporalNetwork( 0, 10 )
    temporal_network.add_temporal_constraints_from(
            [
                (0, "<", 1, 0),
                (1, "<", 2, 0),
            ],
    )
    domain_objects: Dict[ str, List ] = {
        "light_color": [ "green", "yellow", "red" ],
    }

    reference_chronicle, value_chronicle = \
        CI.make_chronicle_pair(
                TrafficReferenceChronicle,
                TrafficValueChronicle,
                changes,
                t_now,
                t_ordered,
                t_unordered,
                persistences,
                temporal_network,
                domain_objects,
        )

    persistence_assertion_lst: List[ ObjectVarPersistence ] = [
        (0, 1, "light_color", "yellow", True),
    ]
    persistence_update_dict: Dict[ str, int ] = dict()
    assert not CI.add_persistences(
            reference_chronicle, value_chronicle, persistence_assertion_lst, persistence_update_dict,
    )

    assert value_chronicle.persistences == {
        "light_color": [
            (0, 1, "light_color", "yellow", False),
            (1, 2, "light_color", "red", False),

        ],
        "can_go":      [ ],
    }
    assert reference_chronicle.persistences == {
        "light_color": 2,
        "can_go":      0,
    }
    assert persistence_update_dict == { }
"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
