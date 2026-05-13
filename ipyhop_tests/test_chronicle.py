#!/usr/bin/env python
"""
File Description: unit testing for methods of ChronicleInterface class in chronicle.py
"""
from ipyhop import ChronicleInterface

CI = ChronicleInterface()


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


# verify_object_assertion
# only match
# only negation
# later match
# later negation
# absent True
# absent False

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
