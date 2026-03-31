#!/usr/bin/env python
"""
File Description: class and methods for manipulating temporal constraints in the form of simple temporal networks
"""

from networkx import Graph
from typing import NewType, List, Tuple, Union, Dict

# STN typing
NetEdgeInput = Tuple[Tuple[int,int],Dict[str,int]]
TemporalConstraint = Tuple[int,str,int,int]

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
        self.t_min = t_min
        self.t_max = t_max
        # # virtual time points for fixed integer positions -1 is t_min and -2 is t_max
        # # negative numbers are used here to avoid name clashes with planner
        # virtual_tps = [ -1, -2 ]
        # self.virtual_tps = virtual_tps
        # self.minimal.add_nodes_from( virtual_tps )
        # bounding_edge = self.get_formatted_edge( (-2,-1,"==",t_max-t_min) )
        # self.minimal.add_edge(bounding_edge)

    # takes list of temporal constraints (TIPyHOPPER format) and attempts to sequential apply them
    # if a failure occurs for any constraint, restores minimal STN to state prior
    # to operations
    # returns tuple (success_flag, node_add_lst, edge_add_lst, edge_remove_lst)
    def add_temporal_constraints_from(self, new_edge_lst: List[TemporalConstraint]):
        # local refs
        add_temporal_constraint = self.add_temporal_constraint
        get_formatted_edge = self.get_formatted_edge
        # initialize lists
        lst_node_add_lst: List[int] = []
        lst_edge_add_lst: List[NetEdgeInput] = []
        lst_edge_remove_lst: List[NetEdgeInput] = []
        # iterate over constraints
        for new_edge in map(get_formatted_edge, new_edge_lst):
            # apply constraint
            success_flag, node_add_lst, edge_add_lst, edge_remove_lst = add_temporal_constraint( new_edge )
            # path consistent, accumulate lists
            if success_flag:
                lst_node_add_lst += node_add_lst
                lst_edge_add_lst += edge_add_lst
                lst_edge_remove_lst += edge_remove_lst
            # path inconsistent, restore graph and return
            else:
                self.restore_graph(node_add_lst, edge_add_lst, edge_remove_lst)
                return (False, [], [], [])
        return (True, lst_node_add_lst, lst_edge_add_lst, lst_edge_remove_lst)

    # update minimal STN with edge
    # returns tuple (success_flag, node_add_lst, edge_add_lst, edge_remove_lst)
    def add_temporal_constraint( self, new_edge: NetEdgeInput ):
        # make local refs
        min_stn: Graph = self.min_stn
        path_consistency = self.path_consistency
        # initialize lists
        node_add_lst: List[int] = []

        # add nodes if new
        edge_nodes: Tuple[int,int] = new_edge[0]
        # check both nodes in edge
        for v in edge_nodes:
            # only care if nodes are not already in graph
            if v not in min_stn.nodes:
                # track nodes and bound them by min and max times
                node_add_lst.append(v)
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
        # remove added nodes
        graph.remove_nodes_from(node_add_lst)
        # remove added edges
        graph.remove_edges_from(edge_add_lst)
        # add removed edges
        graph.add_edges_from(edge_remove_lst)
        return

    # # performs path consistency algorithm on minimal STN after adding single edge
    # # returns tuple (success_flag, edge_add_lst, edge_remove_lst)
    # # success is achieved if no inconsistent edge triple is found
    # # edge_add_lst: all edges that were added before return
    # # edge_remove_lst: all edges that were removed before return
    # def quadratic_path_consistency( self, min_stn: Graph, new_edge: NetEdgeInput
    #                       ) -> Tuple[bool, List[NetEdgeInput], List[NetEdgeInput]]:
    #     intersect_edges = self.intersect_edges
    #     find_edge = self.find_edge
    #     consistency_check = self.consistency_check
    #     edge_add_lst: List[NetEdgeInput] = []
    #     edge_remove_lst: List[NetEdgeInput] = []
    #     # if there is an existing edge parallel to new_edge terminate early with success
    #     # if new_edge is no stricter than the existing edge
    #     # check for edge in minimal STN, may need to get reverse edge and flip it
    #     existing_edge = find_edge(min_stn,*new_edge[0])
    #     if existing_edge is not None:
    #         updated_edge = intersect_edges(new_edge,existing_edge)
    #         if updated_edge == existing_edge:
    #             return (True,edge_add_lst,edge_remove_lst)
    #         # existing edge and mark in remove list
    #         min_stn.remove_edge(*updated_edge[0])
    #         edge_remove_lst.append(existing_edge)
    #     # add updated_edge and mark in add list
    #     min_stn.add_edge(*updated_edge[0])
    #     edge_add_lst.append(updated_edge)
    #     # check consistency of all triplets that have the updated edge as a side
    #     # track removed and added edges
    #     # if any inconsitent triplet found, end then and signal failure
    #     edge_jk = updated_edge
    #     node_j = updated_edge[0][1]
    #     # iterate over 1st node in triplet
    #     for node_i in sorted(filter(lambda x: x != min_stn.nodes)):
    #         # every node must be unique
    #         if node_i == node_j:
    #             continue
    #         # get edge between node_i and node_j, if it does not exist skip
    #         edge_ij = find_edge(min_stn, node_i, node_j)
    #         # iterate over 3rd node in triplet, must be unique and avoid double triplet counting
    #         for node_k in sorted(filter(lambda x: x > node_i and x != node_j, min_stn.nodes)):
    #             # get edge between node_i and node_k, if it does not exist skip
    #             edge_ik = find_edge(min_stn, node_i, node_k)
    #             # consistency check, if consistent and has tighter bound, replace edge_ik in graph with new one
    #             # update add and remove lists
    #             # terminate if inconsistent
    #             consistent_edge = consistency_check(edge_ij, edge_jk, edge_ik)
    #             if consistent_edge is None:
    #                 return (False,edge_add_lst,edge_remove_lst)
    #             elif consistent_edge == edge_ik:
    #                 continue
    #             else:
    #                 min_stn.add_edge(consistent_edge)
    #                 edge_add_lst.append(consistent_edge)
    #                 edge_remove_lst.append(edge_ik)
    #         # all edges consistent and updated, successful termination
    #     return (True,edge_add_lst,edge_remove_lst)
    #
    #     # performs path consistency algorithm on minimal STN after adding single edge
    #     # returns tuple (success_flag, edge_add_lst, edge_remove_lst)
    #     # success is achieved if no inconsistent edge triple is found
    #     # edge_add_lst: all edges that were added before return
    #     # edge_remove_lst: all edges that were removed before return

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
        existing_edge = find_edge( min_stn, *new_edge[ 0 ] )
        if existing_edge is not None:
            updated_edge = intersect_edges( new_edge, existing_edge )
            if updated_edge == existing_edge:
                return (True, edge_add_lst, edge_remove_lst)
            # existing edge and mark in remove list
            min_stn.remove_edge( *updated_edge[ 0 ] )
            edge_remove_lst.append( existing_edge )
        else:
            updated_edge = existing_edge
        # add updated_edge and mark in add list
        min_stn.add_edges_from( [updated_edge] )
        edge_add_lst.append( updated_edge )
        # iterate over all node triplets (i,j,k) such that i < k, i != j, j != k
        for j in sorted( min_stn.nodes ):
            for i in sorted( filter( lambda x: x != j, min_stn.nodes ) ):
                for k in sorted( filter( lambda x: x > i and x != j, min_stn.nodes) ):
                    # get each edge
                    # tail - tail, composing
                    edge_ij = find_edge( min_stn, i, j )
                    # head - head, composing
                    edge_jk = find_edge( min_stn, j, k )
                    # tail - head, intersecting
                    edge_ik = find_edge( min_stn, i, k )
                    # if either composing edge is missing skip triplet
                    if edge_ij is None or edge_jk is None:
                        continue
                    # perform consistency check on triplet
                    updated_edge_ik = consistency_check( edge_ij, edge_jk, edge_ik )
                    # edge is inconsistent, terminate with failure
                    if updated_edge_ik is None:
                        return (False, edge_add_lst, edge_remove_lst)
                    # edge does not constrict, do nothing
                    elif updated_edge_ik == edge_ik:
                        continue
                    # edge has constricted, add old edge to remove list, and new edge list to add list
                    else:
                        standardized_updated_edge_ik = standardize_edge(updated_edge_ik)
                        standardized_edge_ik = standardize_edge(edge_ik)
                        min_stn.add_edges_from([standardized_updated_edge_ik])
                        edge_add_lst.append(standardized_updated_edge_ik)
                        edge_remove_lst.append(standardized_edge_ik)
        return (True, edge_add_lst, edge_remove_lst)

    # return edge if one exists between node_0 and node_1
    # interval is oriented node_0 -> node_1
    def find_edge( self, graph: Graph, node_0: int, node_1: int ) -> NetEdgeInput:
        # see if edge exists
        edge = (node_0,node_1)
        if graph.has_edge( node_0, node_1 ):
            # flip edge if node_0 and node_1 not in lexicographical order
            edge_dict = graph.get_edge_data( node_0, node_1 )
            if node_1 < node_0:
                edge_dict = {
                    "min_delta_t": -edge_dict["max_delta_t"],
                    "max_delta_t": -edge_dict["min_delta_t"]
                }
        else:
            return None
        return (edge, edge_dict)

    # orients edge lexicographically
    def standardize_edge( self, edge: NetEdgeInput ):
        edge_label = edge[0]
        if edge_label[0] < edge_label[1]:
            return edge
        else:

            edge_label = (edge_label[1],edge_label[0])
            edge_dict = edge[1]
            edge_dict = {
                "min_delta_t": -edge_dict["max_delta_t"],
                "max_delta_t": -edge_dict["min_delta_t"]
            }
            return ( edge_label, edge_dict )

    # given edge (i,j) and edge (j,k) gives composed edge (i,k)
    # adds minimum and maximum delta t's
    def compose_edges( self, edge_ij: NetEdgeInput, edge_jk: NetEdgeInput ) -> NetEdgeInput:
        # can only compose edges if they are connected as such
        assert edge_ij[0][1] == edge_jk[0][0]
        edge_ik = ( edge_ij[0][0], edge_jk[0][1] )
        edge_ik_dict = {
            "min_delta_t": edge_ij[1]["min_delta_t"] + edge_jk[1]["min_delta_t"],
            "max_delta_t": edge_ij[ 1 ][ "max_delta_t" ] + edge_jk[ 1 ][ "max_delta_t" ],
        }
        return (edge_ik,edge_ik_dict)

    # given 2 parallel edges get intersection
    # edge_ij intersect edge_ij' has max min_delta_t and the min max_delta_t
    def intersect_edges( self, edge: NetEdgeInput, edge_prime: NetEdgeInput ) -> NetEdgeInput:
        # can only intersect edges between the same nodes
        assert edge[0] == edge_prime[0]
        edge_ik_dict = {
            "min_delta_t": max( edge[1]["min_delta_t"], edge_prime[1]["min_delta_t"] ),
            "max_delta_t": min( edge[ 1 ][ "max_delta_t" ], edge_prime[ 1 ][ "max_delta_t" ] ),
        }
        return (edge[0],edge_ik_dict)

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
        if intersected_edge[1]["max_delta_t"] >= intersected_edge[1]["min_delta_t"]:
            return intersected_edge
        else:
            return None

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
        # always order edge lexicographically, flip sign correctly
        # the graph is treated as an unordered graph, but delta_t values must be corrected when operating against order
        if tp_0 > tp_1:
            tp_0, tp_1 = tp_1, tp_0
            if "<" in t_op:
                t_op.replace("<",">")
            else:
                t_op.replace( ">", "<" )
            val = -val
        # transform in to edge tuple for networkx
        t_min = self.t_min
        t_max = self.t_max
        t_range = t_max - t_min
        edge_label = ( tp_0, tp_1 )
        edge_dict = dict()
        if t_op == "<=":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": t_range } )
        elif t_op == "==":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": val } )
        elif t_op == ">=":
            edge_dict.update( { "min_delta_t": -t_range, "max_delta_t": -val } )
        return ( edge_label, edge_dict )

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
