#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""

from ipyhop import Actions
from typing import NewType, List, Tuple, Union, Dict, TypeAlias
from ipyhop import State
from networkx import MultiDiGraph, DiGraph, Graph
from itertools import permutations

# domain typing
Surface = NewType("Surface", str)
Block = NewType("Block", Surface)
Table = NewType("Table", Surface)



'''
note: we handle time points by integer label rather than temporal value
state description
state: contains only indices to be used in reference to lists
    object_var: list of tuples (time_point, predicate_name, *predicate_arg, value) where
        predicate_name( predicate_arg ) equals value at time_point 
    temporal_con: list of tuples (time_point_0, comp_op, time_point_1, int_offset) where each tuple corresponds
        to a realtive temporal constraint of the form time_point_0 comp_op time_point_1 + int_offset where
        comp_op = {<, <=, ==, >, >=}, time_point_1 can be None in the case where time_point_0 is given an absolute 
        constraint   
    t_now: latest time point for which all incoming effects have been resolved
    t_ordered: list of time points such that for all timepoints in the list, no later (in the list)
        time point is earlier (temporal relation) t_ordered[i] <= t_ordered[j] for all i<=j
    t_unordered: unordered list of time points yet to be placed into total ordering
    t_all: unordered list of all time points (t_0 has the label found at t_all[0])
    persistences: list of tuples (t_start, t_end, desired_bool, predicate_name, predicate_arg)
        where for all time points between t_start and t_end predicate_name( predicate_args) must not contradict value
    domain_objects: fixed typing of all domain objects
        blocks: list of all objects of type Blocks
        table: singular table object (type Table)
        surfaces: list of all objects of type Surface 
reference: contains lists corresponding to indices in state
'''

# helper functions
# bulk insert elements into list overwriting and appending as needed
# this return the new last_valid_index
def safe_list_update( lst: List, update_element_lst: List,  update_start_index: int):
    # size of original list (including garbage)
    lst_size = len(lst)
    # size of update
    update_size = len(update_element_lst)
    # new last valid index
    last_valid_index = update_start_index + update_size - 1
    # if list exists at index replace else extend
    for i in range(update_size):
        current_index = update_start_index + i
        # out of bounds add remainder via extend
        if current_index >= lst_size:
            break
        # in bounds insert into existing spot
        lst[current_index] = update_element_lst[i]
    if current_index >= lst_size:
        print(update_element_lst[i:])
        lst.extend(update_element_lst[i:])
    return last_valid_index

# returns generator that yields potentially relevant variable assignments
# given a list of tuples, the last valid index, and a predicate and list of predicate values return
# the first match going in reverse order of indices
# given (t_0, on, A, B), (t_0, on, B, C), (t_1, on, A, T), (t_1, clear, A)
# the input (on,) would give (t_1, on, A, T) and input (on,B) would
# give (t_0,on,B,C)
# if no pattern match returns empty generator else returns generator for matching pattern
def object_variable_lookup_generator( object_var_lst: List[Tuple], last_valid_index: int, pred_pat: Tuple, t_ordered: List[int],
                                      t_now: int):
    # cycle through list in reverse
    for i in reversed(range(last_valid_index+1)):
        current_tuple = object_var_lst[i]
        for j in range(len(pred_pat)):
            # break out of inner loop on mismatch
            if current_tuple[j+1] != pred_pat[j]:
                break
            # match found if every arg in pred_pat matched
            if j == len(pred_pat)-1:
                # make sure the time point is before t_now in the ordering
                t_then = current_tuple[0]
                now_index = t_ordered.index(t_now)
                then_index = t_ordered.index(t_then)
                if now_index >= then_index:
                    match = current_tuple
                    yield match

# returns generator which yields potentially relevant temporal constraints
# the following are considered relevant
def temporal_constraint_lookup_generator( temporal_con_lst: List[Tuple], last_valid_index: int, temporal_pat: Tuple,
                                          t_ordered: List[int], t_now: int ):
    # # cycle through list in reverse starting at last valid index
    # for temporal_con in reversed(temporal_con_lst[:last_valid_index+1]):
    #     t_con_0, t_op, t_con_1 = temporal_con
    pass

# STN typing
NetEdgeInput: TypeAlias = Tuple[Tuple[int,int],Dict[str,int]]
TemporalConstraint: TypeAlias = Tuple[int,str,int,int]

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
            edge_label = reversed(edge_label)
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
            if t_op is "<":
                val -= 1
            elif t_op is ">":
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
        # transform in to edge tuple for networkx
        t_min = self.t_min
        t_max = self.t_max
        t_range = t_max - t_min
        edge = ( tp_0, tp_1 )
        edge_dict = dict()
        if t_op == "<=":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": t_range } )
        elif t_op == "==":
            edge_dict.update( { "min_delta_t": val, "max_delta_t": val } )
        elif t_op == ">=":
            edge_dict.update( { "min_delta_t": -t_range, "max_delta_t": -val } )
        return ( edge, edge_dict )





# check for evaluated predicate contradicting any member of the persistent conditions
# a contradiction requires the current time point to be within the bound of a persistence condition starting and
# ending times with the predicate and predicate arguements matching and the values being different
# only persistence conditions at indices smaller than last valid index count
def persistence_check( pers_con_lst: List[Tuple], pers_con_last_val_idx: int,
                       eval_pred: Tuple, t_ordered: List[int], t_now: int ):
    # iterate in reverse over persistences within last valid index
    for pers_con in reversed(pers_con_lst[:pers_con_last_val_idx+1]):
        # check if t_now is within persistence condition bound
        t_start = pers_con[ 0 ]
        t_end = pers_con[ 1 ]
        t_now_idx = t_ordered.index(t_now)
        t_start_idx = t_ordered.index(t_start)
        t_end_idx = t_ordered.index( t_end )
        if t_now_idx >= t_start_idx and t_now_idx <= t_end_idx:
            # check if predicate name and args match
            if eval_pred[1:-1] == pers_con[2:-1]:
                # check if value contradicts
                if eval_pred[-1] != pers_con[-1]:
                    return False
    return True


# return true if no contradiction in state would be created by adding new tuple
# object variable 
def contradiction_check( lst_type: str, lst: List[Tuple], eval_pred: Tuple, t_ordered: List[int], t_now: int ):
    if lst_type == "object":
        return object_contradiction_check()
    elif lst_type == "temporal":
        return temporal_contradiction_check()
    else:
        raise ValueError(lst_type + "is not a supported value for the type of list")

# if an assignment at the time of the predicate exists already, returns False if the value is different else
# returns True
def object_contradiction_check(object_var_lst: List[Tuple], last_valid_index: int, pred_pat: Tuple,
                               t_ordered: List[int], t_now: int):
    # find any assignment at t_now for the predicate
    rel_obj_gen = object_variable_lookup_generator( object_var_lst, last_valid_index, pred_pat[:-1], t_ordered, t_now)
    for rel_obj_var in rel_obj_gen:
        # check if value is different
        if rel_obj_var[-1] != pred_pat[-1]:
            return False
    return True

def temporal_contradiction_check():
    pass

# return true if tuple can be added without contradiction or persistence condition violation
def can_add_assertion():
    if contradiction_check() and persistence_check():
        return True
# given list of assertions check to see if they can all be added without issue
def can_add_all_assertions():

    pass


# get all time points that are plausible candidates for next time point to add to ordering
# find all timepoints that have no timepoint not in t_ordered that must precede them
def next_timepoint_generator():
    pass

# ADD universal low priority methods for advancing time and choosing next timepoint

#
# actions = Actions()
#
# # from t_start to t_end=t_start+1 move block from being on start_pos to being on the table
# def move_block_to_table( state: State, t_start: int, block: Block, start_pos: Block):
#     # type checking
#     if all([
#         t_start is int,
#         block is Block,
#         start_pos is Block,
#     ]):
#         pass





# actions.declare_actions( [move_block_to_table, ])

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Temporal Blocks World not implemented.")

"""
Author(s): Paul Zzaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
