#!/usr/bin/env python
"""
File Description: unit testing for methods of TemporalNetwork class of temporal.py
"""
import itertools

import pytest
from ipyhop.temporal import TemporalNetwork, TemporalConstraint, NetEdgeInput
from typing import List
from copy import deepcopy

# tests for standardize_edge method of TemporalNetwork class
#  standardize_edge should not change standardized edge
def test_standardize_edge_0():
    t_min = 0
    t_max = 10
    node_0 = 0
    node_1 = 1
    min_delta_t = 2
    max_delta_t = 5
    test_stn = TemporalNetwork( t_min, t_max )
    input_edge = ( node_0, node_1, {"min_delta_t": min_delta_t, "max_delta_t": max_delta_t })
    test_edge = test_stn.standardize_edge(input_edge)
    eval_edge = input_edge
    assert test_edge == eval_edge

# correctly reverse STN arrows
def test_standardize_edge_1():
    t_min = 0
    t_max = 10
    node_0 = 5
    node_1 = 3
    min_delta_t = 2
    max_delta_t = 5
    test_stn = TemporalNetwork( t_min, t_max )
    input_edge = ( node_0, node_1, {"min_delta_t": min_delta_t, "max_delta_t": max_delta_t })
    test_edge = test_stn.standardize_edge(input_edge)
    eval_edge = ( node_1, node_0, {"min_delta_t": -max_delta_t, "max_delta_t": -min_delta_t })
    assert test_edge == eval_edge

# tests for get_formatted_edge_method
# base case <=
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
    eval_edge: NetEdgeInput = ( node_0, node_1, { "min_delta_t": -t_range, "max_delta_t": offset } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# base case ==
def test_get_formatted_edge_1():
    node_0 = 3
    node_1 = 5
    t_min = 1
    t_max = 12
    offset = 6
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_3 == t_5 + 6
    test_constraint: TemporalConstraint = (node_0,"==",node_1,offset)
    eval_edge: NetEdgeInput = ( node_0, node_1, { "min_delta_t": offset, "max_delta_t": offset } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# base case >=
def test_get_formatted_edge_2():
    node_0 = 4
    node_1 = 7
    t_min = 3
    t_max = 10
    offset = 2
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_4 >= t_7 + 2
    test_constraint: TemporalConstraint = (node_0,">=",node_1,offset)
    eval_edge: NetEdgeInput = ( node_0, node_1, { "min_delta_t": offset, "max_delta_t": t_range } )
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# <= out of order
def test_get_formatted_edge_3():
    node_0 = 5
    node_1 = 3
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_3 >= t_5 - 5
    eval_constraint: TemporalConstraint = (node_1,">=",node_0,-offset)
    # t_5 <= t_3 + 5
    test_constraint: TemporalConstraint = (node_0,"<=",node_1,offset)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# == out of order
def test_get_formatted_edge_4():
    node_0 = 5
    node_1 = 3
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_3 <= t_5 - 5
    eval_constraint: TemporalConstraint = (node_1,"==",node_0,-offset)
    # t_5 >= t_3 + 5
    test_constraint: TemporalConstraint = (node_0,"==",node_1,offset)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# >= out of order
def test_get_formatted_edge_5():
    node_0 = 5
    node_1 = 3
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_3 <= t_5 - 5
    eval_constraint: TemporalConstraint = (node_1,"<=",node_0,-offset)
    # t_5 >= t_3 + 5
    test_constraint: TemporalConstraint = (node_0,">=",node_1,offset)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# <
def test_get_formatted_edge_6():
    node_0 = 0
    node_1 = 1
    t_min = 0
    t_max = 10
    offset = 5
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_0 < t_1 + 5
    test_constraint: TemporalConstraint = (node_0,"<",node_1,offset)
    eval_edge: NetEdgeInput = ( node_0, node_1, { "min_delta_t": -t_range, "max_delta_t": offset-1 } )
    test_edge = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# >
def test_get_formatted_edge_7():
    node_0 = 4
    node_1 = 7
    t_min = 3
    t_max = 10
    offset = 2
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_4 > t_7 + 2
    test_constraint: TemporalConstraint = (node_0,">",node_1,offset)

    eval_edge: NetEdgeInput = ( node_0, node_1, { "min_delta_t": offset+1, "max_delta_t": t_range } )
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# equivalence of > and >= +1
def test_get_formatted_edge_8():
    node_0 = 4
    node_1 = 7
    t_min = 3
    t_max = 10
    offset = 2
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_4 > t_7 + 2
    test_constraint: TemporalConstraint = (node_0,">",node_1,offset)
    # t_4 >= t_7 + 3
    eval_constraint: TemporalConstraint = (node_0,">=",node_1,offset+1)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# equivalence of < and <= -1
def test_get_formatted_edge_8():
    node_0 = 4
    node_1 = 7
    t_min = 3
    t_max = 10
    offset = 2
    t_range = t_max-t_min
    test_stn = TemporalNetwork(t_min,t_max)
    # t_4 < t_7 + 2
    test_constraint: TemporalConstraint = (node_0,">",node_1,offset)
    # t_4 >= t_7 + 3
    eval_constraint: TemporalConstraint = (node_0,">=",node_1,offset+1)
    eval_edge: NetEdgeInput = test_stn.get_formatted_edge(eval_constraint)
    test_edge: NetEdgeInput = test_stn.get_formatted_edge(test_constraint)
    assert eval_edge == test_edge

# tests for intersect_edges
# edge order invariant
def test_intersect_edges_0():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_constraint_0 = (0,"<",1,5)
    test_constraint_1 = (0,">",1,1)
    test_edge_0 = test_stn.get_formatted_edge(test_constraint_0)
    test_edge_1 = test_stn.get_formatted_edge(test_constraint_1)
    intersected_edge_0 = test_stn.intersect_edges(test_edge_0,test_edge_1)
    intersected_edge_1 = test_stn.intersect_edges(test_edge_1,test_edge_0)
    assert intersected_edge_0 == intersected_edge_1

# parallel edges only
def test_intersect_edges_1():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )

    test_edge_0: NetEdgeInput = ( 2, 5, { "min_delta_t": -5, "max_delta_t": 5 })
    test_edge_1: NetEdgeInput = ( 5, 2, { "min_delta_t": -5, "max_delta_t": 5 })
    try:
        test_stn.intersect_edges( test_edge_0, test_edge_1 )
        assert False
    except ValueError:
        assert True

# partial overlap
def test_intersect_edges_2():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 3, 7, { "min_delta_t": -5, "max_delta_t": 2 })
    test_edge_1: NetEdgeInput = ( 3, 7, { "min_delta_t": -2, "max_delta_t": 5 })
    eval_edge: NetEdgeInput = ( 3, 7, { "min_delta_t": -2, "max_delta_t": 2 })
    intersected_edge = test_stn.intersect_edges(test_edge_0,test_edge_1)
    assert eval_edge == intersected_edge
# complete overlap
def test_intersect_edges_3():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 3, 7, { "min_delta_t": -3, "max_delta_t": 3 })
    test_edge_1: NetEdgeInput = ( 3, 7 , { "min_delta_t": -5, "max_delta_t": 5 })
    intersected_edge = test_stn.intersect_edges(test_edge_0,test_edge_1)
    assert intersected_edge == test_edge_0
# intersection does not exist
def test_intersect_edges_4():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 3, 7, { "min_delta_t": 0, "max_delta_t": 3 })
    test_edge_1: NetEdgeInput = ( 3, 7, { "min_delta_t": 5, "max_delta_t": 8 })
    intersected_edge = test_stn.intersect_edges(test_edge_0,test_edge_1)
    assert intersected_edge is None
# single point intersection
def test_intersect_edges_5():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 2, 6, { "min_delta_t": 0, "max_delta_t": 3 })
    test_edge_1: NetEdgeInput = ( 2, 6 , { "min_delta_t": 3, "max_delta_t": 8 })
    intersected_edge = test_stn.intersect_edges(test_edge_0,test_edge_1)
    eval_edge: NetEdgeInput = ( 2, 6, { "min_delta_t": 3, "max_delta_t": 3 })
    assert eval_edge == intersected_edge

# tests for compose_edges
# random simple case
def test_compose_edges_0():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 4, 9, { "min_delta_t": 1, "max_delta_t": 2 })
    test_edge_1: NetEdgeInput = ( 9, 12, { "min_delta_t": 3, "max_delta_t": 5 })
    eval_edge: NetEdgeInput = ( 4, 12, { "min_delta_t": 4, "max_delta_t": 7 })
    composed_edge: NetEdgeInput = test_stn.compose_edges(test_edge_0,test_edge_1)
    assert eval_edge == composed_edge

# raise error if edges cannot be composed
def test_compose_edges_1():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_0: NetEdgeInput = ( 1, 2, { "min_delta_t": 1, "max_delta_t": 2 })
    test_edge_1: NetEdgeInput = ( 3, 5, { "min_delta_t": 3, "max_delta_t": 5 })
    try:
        test_stn.compose_edges(test_edge_0,test_edge_1)
        assert False
    except ValueError:
        assert True

# tests for consistency_check
# consistent
def test_consistency_check_0():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_ij: NetEdgeInput = ( 1, 2, { "min_delta_t": 1, "max_delta_t": 3 })
    test_edge_jk: NetEdgeInput = ( 2, 5, { "min_delta_t": 2, "max_delta_t": 5 })
    test_edge_ik: NetEdgeInput = ( 1, 5, {"min_delta_t": -5, "max_delta_t": 5} )
    eval_edge_ik: NetEdgeInput = ( 1, 5, {"min_delta_t": 3, "max_delta_t": 5} )
    assert eval_edge_ik == test_stn.consistency_check( test_edge_ij, test_edge_jk, test_edge_ik )

# inconsistent
def test_consistency_check_1():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_ij: NetEdgeInput = ( 1, 2, { "min_delta_t": 1, "max_delta_t": 3 })
    test_edge_jk: NetEdgeInput = ( 2, 5, { "min_delta_t": 2, "max_delta_t": 5 })
    test_edge_ik: NetEdgeInput = ( 1, 5, {"min_delta_t": -5, "max_delta_t": 2} )
    assert None is test_stn.consistency_check( test_edge_ij, test_edge_jk, test_edge_ik )

# when edge_ik is None
def test_consistency_check_2():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edge_ij: NetEdgeInput = ( 1, 2, { "min_delta_t": 1, "max_delta_t": 3 })
    test_edge_jk: NetEdgeInput = ( 2, 5, { "min_delta_t": 2, "max_delta_t": 5 })
    assert test_stn.compose_edges(test_edge_ij,test_edge_jk) == test_stn.consistency_check( test_edge_ij, test_edge_jk, None)

# tests for find_edge
# edge present
def test_find_edge_0():
    t_min = 0
    t_max = 10
    test_stn = TemporalNetwork( t_min, t_max )
    test_edges = [
        ( 0, 1, { "min_delta_t": -3, "max_delta_t": 3 } ),
        ( 1, 2, { "min_delta_t": -5, "max_delta_t": 5 }),
        ( 0, 2, { "min_delta_t": -7, "max_delta_t": 7 })
    ]
    test_stn.min_stn.add_edges_from(test_edges)
    assert test_stn.find_edge(0, 1) == ( 0, 1, { "min_delta_t": -3, "max_delta_t": 3 } )
# edge reverse
def test_find_edge_1():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    test_edges = [
        ( 0, 1, { "min_delta_t": -3, "max_delta_t": 5 } ),
        ( 1, 2, { "min_delta_t": -5, "max_delta_t": 7 }),
        ( 0, 2, { "min_delta_t": -7, "max_delta_t": 11 })
    ]
    test_stn.min_stn.add_edges_from(test_edges)
    assert test_stn.find_edge(1, 0) == ( 1, 0, { "min_delta_t": -5, "max_delta_t": 3 } )

# edge missing
def test_find_edge_2():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    test_edges = [
        ( 0, 1, { "min_delta_t": -3, "max_delta_t": 5 } ),
        ( 1, 2, { "min_delta_t": -5, "max_delta_t": 7 }),
        ( 0, 2, { "min_delta_t": -7, "max_delta_t": 11 })
    ]
    test_stn.min_stn.add_edges_from(test_edges)
    assert test_stn.find_edge(3, 4) is None

# tests for restore_graph
# vertices added
def test_restore_graph_0():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    nodes_to_add = [0, 1, 2, 3, 4]
    nodes_to_remove = [ 2, 3, 4 ]
    nodes_after_restore = [ 0, 1 ]
    test_stn.min_stn.add_nodes_from(nodes_to_add)
    test_stn.restore_graph(nodes_to_remove,[],[])
    assert [*test_stn.min_stn.nodes] == nodes_after_restore
# edges added
def test_restore_graph_1():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    initial_edges: List[NetEdgeInput] = [
        ( 0, 1, {"min_delta_t": 2, "max_delta_t": 3} ),
        (0, 3, { "min_delta_t": 11, "max_delta_t": 13 }),
        (2, 3, { "min_delta_t": 5, "max_delta_t": 7 }),

    ]
    added_edges: List[NetEdgeInput] = [
        (5, 7, { "min_delta_t": 15, "max_delta_t": 17 }),
        (2, 7, { "min_delta_t": 19, "max_delta_t": 21 })
    ]
    test_stn.min_stn.add_edges_from(initial_edges)
    test_stn.min_stn.add_edges_from(added_edges)
    test_stn.restore_graph([5, 7], added_edges, [])
    assert [0,1,3,2] == [*test_stn.min_stn.nodes]
    assert [*initial_edges] == [*map(lambda x: (min(x[0],x[1]),max(x[0],x[1]),x[2]), test_stn.min_stn.edges.data())]
# edges removed
def test_restore_graph_2():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    initial_edges: List[NetEdgeInput] = [
        ( 0, 1, {"min_delta_t": 2, "max_delta_t": 3} ),
        (0, 3, { "min_delta_t": 11, "max_delta_t": 13 }),
        (2, 3, { "min_delta_t": 5, "max_delta_t": 7 }),
        (5, 7, { "min_delta_t": 15, "max_delta_t": 17 }),
    ]
    removed_edges: List[NetEdgeInput] = [
        (5, 7, { "min_delta_t": 15, "max_delta_t": 17 }),
        (2, 3, { "min_delta_t": 5, "max_delta_t": 7 }),
    ]
    test_stn.min_stn.add_edges_from(initial_edges)
    test_stn.min_stn.remove_edges_from(removed_edges)
    test_stn.restore_graph([], [], removed_edges)
    assert [0,1,3,2,5,7] == [*test_stn.min_stn.nodes]
    assert [*initial_edges] == [*map(lambda x: (min(x[0],x[1]),max(x[0],x[1]),x[2]), test_stn.min_stn.edges.data())]

# tests for path_consistency
# adding first edge
def test_path_consistency_0():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 2, "max_delta_t": 3 }),
    ]
    success_flag, edge_add_lst, edge_remove_lst = test_stn.path_consistency(*input_edges)
    assert success_flag
    assert edge_add_lst == input_edges
    assert edge_remove_lst == []
    assert [*test_stn.min_stn.edges.data()] == input_edges
# replacing edge
def test_path_consistency_1():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 7 }),
        (0, 1, { "min_delta_t": 2, "max_delta_t": 9 }),
    ]
    for i in range(len(input_edges)):
        edge = input_edges[i]
        success_flag, edge_add_lst, edge_remove_lst = test_stn.path_consistency(edge)
        assert success_flag
        if i == 0:
            assert edge_add_lst == [ (0, 1, { "min_delta_t": 1, "max_delta_t": 7 }) ]
            assert edge_remove_lst == []
        if i == 1:
            assert edge_add_lst == [ (0, 1, { "min_delta_t": 2, "max_delta_t": 7 }) ]
            assert edge_remove_lst == [ (0, 1, { "min_delta_t": 1, "max_delta_t": 7 }) ]
    assert [*test_stn.min_stn.edges.data()] == [(0, 1, { "min_delta_t": 2, "max_delta_t": 7 })]
# adding second edge
def test_path_consistency_2():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
    ]
    output_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (0, 2, { "min_delta_t": 4, "max_delta_t": 7 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
    ]
    for i in range( len( input_edges ) ):
        edge = input_edges[ i ]
        success_flag, edge_add_lst, edge_remove_lst = test_stn.path_consistency(edge)
        assert success_flag
        if i == 0:
            assert edge_add_lst == [ output_edges[0] ]
            assert edge_remove_lst == []
        if i == 1:
            assert edge_add_lst == [ output_edges[2], output_edges[1] ]
            assert edge_remove_lst == []
    assert [*test_stn.min_stn.edges.data()] == output_edges
# consistent
def test_path_consistency_3():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
        (0, 2, { "min_delta_t": 4, "max_delta_t": 5 }),
    ]
    output_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (0, 2, { "min_delta_t": 4, "max_delta_t": 5 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 4 }),
    ]
    for i in range( len( input_edges ) ):
        edge = input_edges[ i ]
        success_flag, edge_add_lst, edge_remove_lst = test_stn.path_consistency(edge)
        assert success_flag
        if i == 0:
            assert edge_add_lst == [ (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }) ]
            assert edge_remove_lst == []
        if i == 1:
            assert edge_add_lst == [ (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
                                     (0, 2, { "min_delta_t": 4, "max_delta_t": 7 }) ]
            assert edge_remove_lst == []
        if i == 2:
            assert edge_add_lst == [ (0, 2, { "min_delta_t": 4, "max_delta_t": 5 }),
                                     (1, 2, { "min_delta_t": 3, "max_delta_t": 4 }) ]
            assert edge_remove_lst == [ (0, 2, { "min_delta_t": 4, "max_delta_t": 7 }),
                                        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 })]

    assert [*test_stn.min_stn.edges.data()] == output_edges
# inconsistent
def test_path_consistency_4():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
        (0, 2, { "min_delta_t": 1, "max_delta_t": 2 }),
    ]
    for i in range( len( input_edges ) ):
        edge = input_edges[ i ]
        success_flag, edge_add_lst, edge_remove_lst = test_stn.path_consistency(edge)

        if i == 0:
            assert success_flag
            assert edge_add_lst == [ (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }) ]
            assert edge_remove_lst == []
        if i == 1:
            assert success_flag
            assert edge_add_lst == [ (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
                                     (0, 2, { "min_delta_t": 4, "max_delta_t": 7 }) ]
            assert edge_remove_lst == []
        if i == 2:
            assert not success_flag
            assert edge_add_lst == []
            assert edge_remove_lst == []
    assert [*test_stn.min_stn.edges.data()] == [
        (0, 1, { "min_delta_t": 1, "max_delta_t": 2 }),
        (0, 2, { "min_delta_t": 4, "max_delta_t": 7 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
    ]

# tests for add_temporal_constraint
# first edge
def test_add_temporal_constraint_0():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edge: NetEdgeInput = (0, 1, { "min_delta_t": 5, "max_delta_t": 11 })
    success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraint(input_edge)
    assert success_flag
    assert node_add_lst == [0, 1]
    assert edge_add_lst == [input_edge]
    assert edge_remove_lst == []
    assert [*test_stn.min_stn.edges.data()] == [input_edge]
# new nodes
def test_add_temporal_constraint_1():
    t_min = 0
    t_max = 30
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[NetEdgeInput] = [
        (0, 1, { "min_delta_t": 5, "max_delta_t": 11 }),
        (2, 3, { "min_delta_t": 7, "max_delta_t": 13 })
    ]
    for i in range(len(input_edges)):
        edge = input_edges[i]
        success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraint(edge)
        assert success_flag
        if i == 0:
            assert node_add_lst == [0,1]
            assert edge_add_lst == [ input_edges[0] ]
            assert edge_remove_lst == []
        if i == 1:
            assert node_add_lst == [2,3]
            assert edge_add_lst == [ input_edges[1] ]
            assert edge_remove_lst == []
    assert [*test_stn.min_stn.edges.data()] == input_edges

# failure
def test_add_temporal_constraint_2():
    t_min = 0
    t_max = 30
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ NetEdgeInput ] = [
        (0, 1, { "min_delta_t": 5, "max_delta_t": 11 }),
        (1, 2, { "min_delta_t": 26, "max_delta_t": 30 })
    ]
    for i in range(len(input_edges)):
        edge = input_edges[i]
        success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraint(edge)
        if i == 0:
            assert success_flag
            assert node_add_lst == [0,1]
            assert edge_add_lst == [ input_edges[0] ]
            assert edge_remove_lst == []
        if i == 1:
            print(test_stn.min_stn.edges.data())
            assert not success_flag
            assert node_add_lst == []
            assert edge_add_lst == []
            assert edge_remove_lst == []
    assert [ *test_stn.min_stn.edges.data() ] == [ input_edges[0] ]

# tests for add_temporal_constraints_from
# finite single edge
def test_add_temporal_constraints_from_0():
    t_min = 0
    t_max = 20
    t_range = abs(t_max-t_min)
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,7),
        (0,">=",1,2)
    ]
    success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraints_from(input_edges)
    assert success_flag
    assert [0,1] == node_add_lst
    assert edge_add_lst == [
        (0,1,{"min_delta_t": -t_range, "max_delta_t": 7}),
        (0, 1, { "min_delta_t": 2, "max_delta_t": 7 }),
    ]
    assert edge_remove_lst == [(0,1,{"min_delta_t": -t_range, "max_delta_t": 7})]
    assert [ *test_stn.min_stn.edges.data() ] == [ (0,1,{"min_delta_t": 2, "max_delta_t": 7}) ]

# conected edges
def test_add_temporal_constraints_from_1():
    t_min = 0
    t_max = 20
    t_range = abs(t_max-t_min)
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,7),
        (0,">=",1,2),
        (1,"<=",2,5),
        (1,">=",2,3)
    ]
    success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraints_from(input_edges)
    assert success_flag
    assert [0,1,2] == node_add_lst
    assert edge_add_lst == [
        (0,1,{"min_delta_t": -t_range, "max_delta_t": 7}),
        (0, 1, { "min_delta_t": 2, "max_delta_t": 7 }),
        (1, 2, { "min_delta_t": -t_range, "max_delta_t": 5 }),
        (0, 2, { "min_delta_t": 2-t_range, "max_delta_t": 12 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
        (0, 2, { "min_delta_t": 5, "max_delta_t": 12 }),
    ]
    assert edge_remove_lst == [
        (0,1,{"min_delta_t": -t_range, "max_delta_t": 7}),
        (1, 2, { "min_delta_t": -t_range, "max_delta_t": 5 }),
        (0, 2, { "min_delta_t": 2-t_range, "max_delta_t": 12 }),
    ]
    assert [ *test_stn.min_stn.edges.data() ] == [
        (0,1,{"min_delta_t": 2, "max_delta_t": 7}),
        (0, 2, { "min_delta_t": 5, "max_delta_t": 12 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
    ]

# inconsistent
def test_add_temporal_constraints_from_2():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    initial_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,7),
        (0,">=",1,2),
        (1,"<=",2,5),
        (1,">=",2,3)
    ]
    test_stn.add_temporal_constraints_from(initial_edges)
    inconsistent_edges: List[ TemporalConstraint ] = [
        (2,"<",3,0),
        (0, ">", 1, 7),
    ]
    success_flag, node_add_lst, edge_add_lst, edge_remove_lst = test_stn.add_temporal_constraints_from(inconsistent_edges)
    assert not success_flag
    assert [] == node_add_lst
    assert edge_add_lst == []
    assert edge_remove_lst == []
    assert [ *test_stn.min_stn.edges.data() ] == [
        (0,1,{"min_delta_t": 2, "max_delta_t": 7}),
        (0, 2, { "min_delta_t": 5, "max_delta_t": 12 }),
        (1, 2, { "min_delta_t": 3, "max_delta_t": 5 }),
    ]

# tests for get_potential_next_time_points
# all could be next
def test_get_potential_next_time_points_0():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    input_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,0),
        (0,"<=",2,0)
    ]
    unordered_tps = [0,1,2]
    test_stn.add_temporal_constraints_from(input_edges)
    time_point_lst = test_stn.get_potential_next_time_points(unordered_tps)
    # for u, v in itertools.product(unordered_tps,unordered_tps):
    #     print(test_stn.find_edge(u,v))
    assert time_point_lst == [0,1,2]
# single canidate time point
def test_get_potential_next_time_points_1():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    unordered_tps = [0,1,2,3]
    input_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,0),
        (0,"<=",2,0),
        (3,"<",0,0)
    ]
    test_stn.add_temporal_constraints_from(input_edges)
    time_point_lst = test_stn.get_potential_next_time_points(unordered_tps)
    for u, v in itertools.product(unordered_tps,unordered_tps):
        print(test_stn.find_edge(u,v))
    assert time_point_lst == [3]
# multiple candidate time point, excluding some
def test_get_potential_next_time_points_2():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    unordered_tps = [0,1,2]
    input_edges: List[ TemporalConstraint ] = [
        (0,"<=",1,0),
        (0,"<=",2,0),
        (3,"<",0,0)
    ]
    test_stn.add_temporal_constraints_from(input_edges)
    time_point_lst = test_stn.get_potential_next_time_points(unordered_tps)
    for u, v in itertools.product(unordered_tps,unordered_tps):
        print(test_stn.find_edge(u,v))
    assert time_point_lst == [0,1,2]

# empty net
def test_get_potential_next_time_points_3():
    t_min = 0
    t_max = 20
    test_stn = TemporalNetwork( t_min, t_max )
    time_point_lst = test_stn.get_potential_next_time_points( [] )
    assert time_point_lst == []

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
