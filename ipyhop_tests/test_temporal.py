#!/usr/bin/env python
"""
File Description: unit testing for temporal.py
"""

import pytest
from ipyhop.temporal import TemporalNetwork, TemporalConstraint, NetEdgeInput
from typing import List
from copy import deepcopy

# satndardize edge should not change standardized edge
def test_standardized_edge_0():
    t_min = 0
    t_max = 10
    node_0 = 0
    node_1 = 1
    min_delta_t = 2
    max_delta_t = 5
    test_stn = TemporalNetwork( t_min, t_max )
    input_edge = ( ( node_0, node_1 ), {"min_delta_t": min_delta_t, "max_delta_t": max_delta_t })
    test_edge = test_stn.standardize_edge(input_edge)
    eval_edge = input_edge
    assert test_edge == eval_edge

def test_standardized_edge_1():
    t_min = 0
    t_max = 10
    node_0 = 5
    node_1 = 3
    min_delta_t = 2
    max_delta_t = 5
    test_stn = TemporalNetwork( t_min, t_max )
    input_edge = ( ( node_0, node_1 ), {"min_delta_t": min_delta_t, "max_delta_t": max_delta_t })
    test_edge = test_stn.standardize_edge(input_edge)
    eval_edge = ( ( node_1, node_0 ), {"min_delta_t": -max_delta_t, "max_delta_t": -min_delta_t })
    assert test_edge == eval_edge

def test_get_formatted_edge_0():
    node_0 = 0
    node_1 = 1
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_0 <= t_1 + 5
    test_constraint: TemporalConstraint = (node_0,"<=",node_1,offset)
    eval_edge: NetEdgeInput = ( ( node_0, node_1 ), { "min_delta_t": offset, "max_delta_t": t_range } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

def test_get_formatted_edge_1():
    node_0 = 3
    node_1 = 5
    t_min = 1
    t_max = 12
    offset = 6
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_0 == t_1 + 5
    test_constraint: TemporalConstraint = (node_0,"==",node_1,offset)
    eval_edge: NetEdgeInput = ( ( node_0, node_1 ), { "min_delta_t": offset, "max_delta_t": offset } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

def test_get_formatted_edge_2():
    node_0 = 4
    node_1 = 7
    t_min = 3
    t_max = 10
    offset = 2
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_0 >= t_1 + 5
    test_constraint: TemporalConstraint = (node_0,">=",node_1,offset)
    eval_edge: NetEdgeInput = ( ( node_0, node_1 ), { "min_delta_t": -t_range, "max_delta_t": -offset } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

def test_get_formatted_edge_3():
    node_0 = 5
    node_1 = 3
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_3 >= t_5 - 5
    eval_constraint = (node_1,">=",node_0,-offset)
    # t_5 <= t_3 + 5
    test_constraint: TemporalConstraint = (node_0,"<=",node_1,offset)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge = test_stn.get_formatted_edge(test_constraint)
    print(eval_edge)
    print(test_edge)
    assert eval_edge == test_edge

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
