#!/usr/bin/env python
"""
File Description: class and methods for manipulating temporal constraints in the form of simple temporal networks
"""

from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union, cast

from networkx import Graph

# STN typing
NetEdgeInput = Tuple[int,int,Dict[str,int]]
# edge (x,y,{"min_delta_t":a, "max_delta_t": b}) is x >= y + a and x <= y + b EQUIV b >= x-y >= a EQUIV -a <= y-x <= -b
TemporalConstraint = Tuple[int,str,int,int]
# test constraint (x,@,y,z) = x @ y + z

# type alias for tuple containing everything for temporal graph restoration
# (node_add_lst: List[ int ],
#  edge_add_lst: List[ NetEdgeInput ],
#  edge_remove_lst: List[ NetEdgeInput ], )
TemporalRestorationTuple = Tuple[ List[ int ], List[ NetEdgeInput ], List[ NetEdgeInput ] ]
# keyword TOC followed by time point label
TOCSpecTuple = Tuple[ str, int ]


# class for representing and manipulating temporal networks
class TemporalNetwork:
    # initialize empty minimal temporal network, a node -1 and -2 are generated corresponding to the first and last
    # time points respectively
    # t_min: the earliest time a time point may instantiate to
    # t_max: the latest time a time point may instantiate to
    def __init__( self, t_min: int, t_max: int ):
        # edges in graphs must only be in lexicographical order
        # minimal STN
        self.min_stn = Graph()
        if t_min >= t_max:
            raise ValueError("Maximum time point value must be greater than minimum time point value")
        self.t_min = t_min
        self.t_max = t_max
        self.last_time_point_label = -1

    # create a dictionary where every time point label has a key with a corresponding value that
    # respects the network
    def assign_values_to_time_points(self) -> Dict[ int, int ]:
        value_dict: Dict[ int, int ] = { }
        value_dict[ 0 ] = self.t_min
        # iterate over all possible edges
        # if an edge exists from a node in the dictionary the value is the negation of the min_delta_t
        # if an edge does not exist
        for u in self.min_stn.nodes:
            u = cast( int, u )
            if u not in value_dict.keys():
                value_dict[ u ] = self.t_min
            for v in self.min_stn.nodes:
                v = cast( int, v )
                if u != v and v not in value_dict.keys():
                    edge_uv: Optional[ NetEdgeInput ] = self.find_edge( u, v )
                    if edge_uv is not None:
                        value_dict[ v ] = -edge_uv[ 2 ][ "min_delta_t" ] if edge_uv[ 0 ] == u else edge_uv[ 2 ][
                            "max_delta_t" ]
        offset = min( value_dict.values() ) - self.t_min
        for k, v in value_dict.items():
            value_dict[ k ] = v + offset
        print( value_dict )
        return value_dict

    # returns True if tp_0 cannot be greater than or equal to tp_1
    def is_strictly_less_than(self, tp_0: int, tp_1: int) -> bool:
        if tp_0 == tp_1:
            return False
        edge_01 = self.find_edge( tp_0, tp_1 )
        if edge_01 is None:
            return False
        if edge_01[ 2 ][ "max_delta_t" ] < 0:
            return True
        else:
            return False

    # returns True if tp_0 cannot be greater than tp_1
    def is_strictly_less_than_or_equal(self, tp_0: int, tp_1: int) -> bool:
        if tp_0 == tp_1:
            return True
        edge_01 = self.find_edge( tp_0, tp_1 )
        if edge_01 is None:
            return False
        if edge_01[ 2 ][ "max_delta_t" ] <= 0:
            return True
        else:
            return False

    # returns True if tp_0 must be equal to tp_1
    def is_strictly_equal(self, tp_0: int, tp_1: int) -> bool:
        # if <= but not <, must be =
        return self.is_strictly_less_than_or_equal( tp_0, tp_1 ) and not (self.is_strictly_less_than( tp_0, tp_1 ))

    # returns list of time points that may be the next time point
    def get_potential_next_time_points( self, unordered_time_point_lst: List[int] ) -> List[int]:
        # refs
        find_edge = self.find_edge
        t_range = self.t_max - self.t_min
        # there cannot exist an outgoing minimum delta t greater than 0
        max_min_delta_t_dict: Dict[int,int] = { k: -t_range for k in unordered_time_point_lst}
        # iterate over every edge between unordered time points
        for node_i in unordered_time_point_lst:
            for node_j in unordered_time_point_lst:
                if node_i != node_j:
                    edge_ij = find_edge( node_i, node_j )
                    # only care about existing edges
                    if edge_ij is None:
                        continue
                    # if any m
                    max_min_delta_t_dict[ node_i ] = max(
                            max_min_delta_t_dict[ node_i ], edge_ij[ 2 ][ "min_delta_t" ],
                    )
        candidate_time_point_lst = [*filter(lambda x: max_min_delta_t_dict[x] <= 0, unordered_time_point_lst)]
        candidate_time_point_lst.sort( key=lambda x: max_min_delta_t_dict[ x ] )
        return candidate_time_point_lst




    # takes list of temporal constraints (TIPyHOPPER format) and attempts to sequential apply them
    # if a failure occurs for any constraint, restores minimal STN to state prior
    # to operations
    # returns tuple (success_flag, node_add_lst, edge_add_lst, edge_remove_lst)
    def add_temporal_constraints_from(self, new_edge_lst: List[TemporalConstraint]
                                      ) -> Tuple[bool,List[int],List[NetEdgeInput],List[NetEdgeInput]]:
        # local refs
        add_temporal_constraint = self.add_temporal_constraint
        get_formatted_edge = self.get_formatted_edge
        # initialize lists
        lst_node_add_lst: List[int] = []
        lst_edge_add_lst: List[NetEdgeInput] = []
        lst_edge_remove_lst: List[NetEdgeInput] = []
        # iterate over constraints
        for new_edge in map(get_formatted_edge, new_edge_lst):
            if new_edge[ 0 ] == new_edge[ 1 ]:
                print( new_edge )
                raise ValueError( "Cannot have loops in STN" )
            # apply constraint
            success_flag, node_add_lst, edge_add_lst, edge_remove_lst = add_temporal_constraint( new_edge )
            # path consistent, accumulate lists
            lst_node_add_lst += node_add_lst
            lst_edge_add_lst += edge_add_lst
            lst_edge_remove_lst += edge_remove_lst
            # path inconsistent, restore graph and return
            if not success_flag:
                self.restore_graph(lst_node_add_lst, lst_edge_add_lst, lst_edge_remove_lst)
                return (False, [], [], [])
        return (True, lst_node_add_lst, lst_edge_add_lst, lst_edge_remove_lst)

    # update minimal STN with edge
    # returns tuple (success_flag, node_add_lst, edge_add_lst, edge_remove_lst)
    def add_temporal_constraint( self, new_edge: NetEdgeInput
                                 ) -> Tuple[bool,List[int],List[NetEdgeInput],List[NetEdgeInput]]:
        # make local refs
        min_stn: Graph = self.min_stn
        path_consistency = self.path_consistency
        # initialize lists
        node_add_lst: List[int] = []

        # add nodes if new
        edge_nodes = new_edge[:2]
        # check both nodes in edge
        for v_edge in edge_nodes:
            # only care if nodes are not already in graph
            if v_edge not in min_stn.nodes:
                # track nodes and bound them by min and max times
                node_add_lst.append(v_edge)
        # add edge with path consistency
        success_flag, edge_add_lst, edge_remove_lst = path_consistency(new_edge)
        # if failure undo changes and return empty lists
        if not success_flag:
            self.restore_graph(node_add_lst,edge_add_lst,edge_remove_lst)
            return (success_flag, [], [], [])
        return (success_flag, node_add_lst, edge_add_lst, edge_remove_lst)


    # restore graph given added nodes, added edges, and removed edges
    def restore_graph( self, node_add_lst: List[int], edge_add_lst: List[NetEdgeInput],
                       edge_remove_lst: List[NetEdgeInput] ):
        graph: Graph = self.min_stn
        # add removed edges
        graph.add_edges_from( reversed( edge_remove_lst ) )
        # remove added edges
        graph.remove_edges_from( reversed( edge_add_lst ) )
        # remove added nodes
        graph.remove_nodes_from( node_add_lst )
        return



    # performs path consistency algorithm on minimal STN after adding single edge
    # returns tuple (success_flag, edge_add_lst, edge_remove_lst)
    # success is achieved if no inconsistent edge triple is found
    # edge_add_lst: all edges that were added before return
    # edge_remove_lst: all edges that were removed before return
    def path_consistency( self, new_edge: NetEdgeInput
                          ) -> Tuple[ bool, List[ NetEdgeInput ], List[ NetEdgeInput ] ]:
        intersect_edges = self.intersect_edges
        find_edge = self.find_edge
        consistency_check = self.consistency_check
        standardize_edge = self.standardize_edge
        min_stn = self.min_stn
        edge_add_lst: List[ NetEdgeInput ] = [ ]
        edge_remove_lst: List[ NetEdgeInput ] = [ ]
        # if there is an existing edge parallel to new_edge terminate early with success
        # if new_edge is no stricter than the existing edge
        # check for edge in minimal STN, may need to get reverse edge and flip it
        existing_edge = find_edge( *new_edge[ :2 ] )
        if existing_edge is not None:
            updated_edge = intersect_edges( new_edge, existing_edge )
            # edge does not increase constraints
            if updated_edge == existing_edge:
                return (True, [], [])
            # edge is unsatisfiable
            if updated_edge is None:
                return (False, [], [])
            # existing edge and mark in remove list
            min_stn.remove_edge( *updated_edge[ :2 ] )
            edge_remove_lst.append( existing_edge )
        else:
            updated_edge = new_edge
        # add updated_edge and mark in add list
        min_stn.add_edges_from( [updated_edge] )
        edge_add_lst.append( updated_edge )
        # iterate over all node triplets (i,j,k) such that i < k, i != j, j != k
        nodes: List[ int ] = [ *min_stn.nodes ]
        for j in sorted( nodes ):
            for i in sorted( filter( lambda x: x != j, nodes ) ):
                for k in sorted( filter( lambda x: x > i and x != j, nodes ) ):
                    # get each edge
                    # tail - tail, composing
                    edge_ij = find_edge( i, j )
                    # head - head, composing
                    edge_jk = find_edge( j, k )
                    # tail - head, intersecting
                    edge_ik = find_edge( i, k )
                    # if either composing edge is missing skip triplet
                    if edge_ij is None or edge_jk is None:
                        continue
                    # perform consistency check on triplet
                    updated_edge_ik = consistency_check( edge_ij, edge_jk, edge_ik )
                    # edge is inconsistent, terminate with failure
                    t_range = abs(self.t_max - self.t_min)
                    if updated_edge_ik is None or abs(updated_edge_ik[2]["min_delta_t"]) > t_range:
                        return (False, edge_add_lst, edge_remove_lst)
                    # edge does not constrict, do nothing
                    elif updated_edge_ik == edge_ik:
                        continue
                    # edge has constricted, add old edge to remove list, and new edge list to add list
                    else:
                        updated_edge_ik: NetEdgeInput
                        standardized_updated_edge_ik = standardize_edge(updated_edge_ik)
                        if edge_ik is not None:
                            standardized_edge_ik = standardize_edge(edge_ik)
                            edge_remove_lst.append( standardized_edge_ik )
                        min_stn.add_edges_from([standardized_updated_edge_ik])
                        edge_add_lst.append(standardized_updated_edge_ik)
        return (True, edge_add_lst, edge_remove_lst)

    # return edge if one exists between node_0 and node_1
    # interval is oriented node_0 -> node_1
    def find_edge( self, node_0: int, node_1: int ) -> Union[NetEdgeInput,None]:
        min_stn = self.min_stn
        # see if edge exists
        if min_stn.has_edge( node_0, node_1 ):
            # flip edge if node_0 and node_1 not in lexicographic order
            edge_dict_old = min_stn.get_edge_data( node_0, node_1 )
            if node_1 < node_0:
                edge_dict_new = {
                    "min_delta_t": -edge_dict_old["max_delta_t"],
                    "max_delta_t": -edge_dict_old["min_delta_t"]
                }
            else:
                edge_dict_new = deepcopy(edge_dict_old)
        else:
            return None
        return (node_0, node_1, edge_dict_new)

    # edge_ij, edge_jk, and edge_ik consistency check
    # returns  intersect( compose( edge_ij, edge_jk ), edge_ik ) if result is not empty else None
    # the intersection is empty if the resulting edge has max_delta_t < min_delta_t
    def consistency_check( self, edge_ij: NetEdgeInput, edge_jk: NetEdgeInput, edge_ik: Union[NetEdgeInput,None]
                           ) -> Union[None,NetEdgeInput]:
        composed_edge = self.compose_edges(edge_ij,edge_jk)
        # if third edge exists, return intersection, else return composed edge
        if edge_ik is not None:
            intersected_edge = self.intersect_edges(composed_edge,edge_ik)
        else:
            intersected_edge = composed_edge
        return intersected_edge

    # given edge (i,j) and edge (j,k) gives composed edge (i,k)
    # adds minimum and maximum delta t's
    def compose_edges( self, edge_ij: NetEdgeInput, edge_jk: NetEdgeInput ) -> NetEdgeInput:
        t_range = self.t_max - self.t_min
        # can only compose edges if they are connected as such
        if edge_ij[ 1 ] != edge_jk[ 0 ]:
            raise ValueError(str(edge_ij) + " and " + str(edge_jk) + "do not share middle vertex")
        edge_ik_dict = {
            "min_delta_t": max(edge_ij[ 2 ][ "min_delta_t" ] + edge_jk[ 2 ][ "min_delta_t" ], -t_range),
            "max_delta_t": min(edge_ij[ 2 ][ "max_delta_t" ] + edge_jk[ 2 ][ "max_delta_t" ], t_range),
        }
        return (edge_ij[ 0 ], edge_jk[ 1 ], edge_ik_dict)

    # given 2 parallel edges get intersection
    # edge_ij intersect edge_ij' has max min_delta_t and the min max_delta_t
    # raises error if edges are not parallel
    # returns none if edges are parallel without overlap
    def intersect_edges( self, edge: NetEdgeInput, edge_prime: NetEdgeInput ) -> Union[NetEdgeInput,None]:
        # can only intersect edges between the same nodes
        if edge[ 0 ] != edge_prime[ 0 ]:
            raise ValueError(str(edge[:2]) + " and " + str(edge_prime[:2]) + " must be equal")
        edge_dict = {
            "min_delta_t": max( edge[ 2 ][ "min_delta_t" ], edge_prime[ 2 ][ "min_delta_t" ] ),
            "max_delta_t": min( edge[ 2 ][ "max_delta_t" ], edge_prime[ 2 ][ "max_delta_t" ] ),
        }
        if edge_dict["max_delta_t"] < edge_dict["min_delta_t"]:
            return None
        return (edge[ 0 ], edge[ 1 ], edge_dict)

    # convert TIPyHOPPPER edge into form readable by networkx
    def get_formatted_edge( self, t_con: TemporalConstraint ) -> NetEdgeInput:
        tp_0, t_op, tp_1, val = t_con
        # deal with exclusive bounds (shift by 1 in direction of operator)
        if "=" not in t_op:
            if t_op == "<":
                val -= 1
            elif t_op == ">":
                val += 1
            else:
                raise ValueError( str( t_op ) + " is not a valid time point comparison operator" )
            t_op = t_op + "="
        # use range as place holder for inf
        t_min = self.t_min
        t_max = self.t_max
        t_range = t_max - t_min
        if abs(val) > abs(t_range):
            raise ValueError( str(t_con) + " is always larger than range")
        edge_dict = dict()
        if t_op == "<=":
            edge_dict.update( { "min_delta_t": -t_range, "max_delta_t": val } )
        elif t_op == "==":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": val } )
        elif t_op == ">=":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": t_range } )
        # lexicographically order edge
        return self.standardize_edge( ( tp_0, tp_1, edge_dict ) )

    # orients edge lexicographically
    def standardize_edge( self, edge: NetEdgeInput ):
        node_0, node_1, edge_dict = edge
        if node_0 < node_1:
            return edge
        else:
            edge_dict = {
                "min_delta_t": -edge_dict[ "max_delta_t" ],
                "max_delta_t": -edge_dict[ "min_delta_t" ]
            }
            return (node_1, node_0, edge_dict)

    # get n time point labels that have not been used
    def get_n_new_time_point_labels(self, n: int) -> List[ int ]:
        last_time_point_label = self.last_time_point_label + n + 1
        new_time_point_label_lst = [
            *range(
                    self.last_time_point_label + 1,
                    last_time_point_label,
            ),
        ]
        self.last_time_point_label = last_time_point_label
        return new_time_point_label_lst
"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
