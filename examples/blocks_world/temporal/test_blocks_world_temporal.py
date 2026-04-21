# content of test_approx.py

from examples.blocks_world.temporal.blocks_world_temporal_actions import safe_list_update

def test_safe_list_update_0():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 6
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 8
    assert lst == [*range(9)]

def test_safe_list_update_1():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 0
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 2
    assert lst == [6, 7, 8, 3, 4, 5]

def test_safe_list_update_2():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 3
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 5
    assert lst == [0, 1, 2, 6, 7, 8]

def test_safe_list_update_3():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 4
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 6
    assert lst == [0, 1, 2, 3, 6, 7, 8]

def test_safe_list_update_4():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 5
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 7
    assert lst == [0, 1, 2, 3, 4, 6, 7, 8]


def test_safe_list_update_5():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 1
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 3
    assert lst == [0, 6, 7, 8, 4, 5]
