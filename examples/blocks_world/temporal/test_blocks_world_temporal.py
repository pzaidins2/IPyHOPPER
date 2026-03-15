# content of test_approx.py
import pytest

from examples.blocks_world.temporal.blocks_world_temporal_actions import safe_list_update

def test_safe_list_update_0():
    lst = [0, 1, 2, 3, 4, 5]
    update_index = 6
    update_element_lst= [6, 7, 8]
    last_valid_index = safe_list_update(lst,update_element_lst,update_index)
    assert last_valid_index == 8
    assert lst == [*range(9)]



