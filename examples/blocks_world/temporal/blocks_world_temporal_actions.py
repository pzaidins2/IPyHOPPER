#!/usr/bin/env python
"""
File Description: temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""

from ipyhop import Actions
from typing import NewType, List, Tuple, Union, Dict, TypeAlias
from ipyhop import State
from networkx import MultiDiGraph, DiGraph

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
    # initialize empty full and corresponding minimal temporal network
    # t_min: the earliest time a time point may instantiate to
    # t_max: the latest time a time point may instantiate to
    def __init__( self, t_min: int, t_max: int ):
        # full temporal network as directed graph allowing parallel edges
        self.full = MultiDiGraph()
        # minimal representaion of above as simple directed graph
        self.minimal = DiGraph()
        self.t_min = t_min
        self.t_max = t_max
        # virtual time points for fixed integer positions -1 is t_min and -2 is t_max
        # negative numbers are used here to avoid name clashes with planner
        virtual_tps = [ -1, -2 ]
        self.full.add_nodes_from( virtual_tps )
        self.minimal.add_nodes_from( virtual_tps )

    # update full and minimal STN with edge in TIPyHOPPER format: (t_0, op, t_1, int)
    # returns tuple (success_flag, node_add_lst, full_add_lst, minimal_add_lst, minimal_remove_lst)
    def _add_constraint( self, new_edge: NetEdgeInput ):
        # make local refs
        full: MultiDiGraph = self.full
        minimal: DiGraph= self.minimal
        get_bounding_edges = self.get_bounding_edges
        # initialize lists
        node_add_lst: List[int] = []
        full_edge_add_lst: List[NetEdgeInput] = []
        minimal_edge_add_lst: List[NetEdgeInput] = []
        minimal_edge_remove_lst: List[NetEdgeInput] = []
        bounding_edge_lst: List[NetEdgeInput] = []

        # add nodes if new
        edge_nodes: Tuple[int,int] = new_edge[0]
        # check both nodes in edge
        for v in edge_nodes:
            # only care if nodes are not already in graph
            if v not in minimal.nodes:
                # track nodes and bound them by min and max times
                node_add_lst.append(v)
                v_bounding_edges = get_bounding_edges(v)
                bounding_edge_lst += v_bounding_edges

    # performs path consistency algorithm on minimal STN after adding single edge
    # returns tuple (success_flag, minimal_edge_add_lst, minimal_edge_remove_lst)
    # success is achieved if no inconsistent edge triple is found
    # minimal_edge_add_lst: all edges that were added before return
    # minimal_edge_remove_lst: all edges that were removed before return
    def path_consistency( self, min_stn: DiGraph, new_edge: NetEdgeInput
                          ) -> Tuple[bool, List[NetEdgeInput], List[NetEdgeInput]]:
        intersect_edges = self.intersect_edges
        find_edge = self.find_edge
        minimal_edge_add_lst: List[NetEdgeInput] = []
        minimal_edge_remove_lst: List[NetEdgeInput] = []
        # if there is an existing edge parallel to new_edge terminate early with success
        # if new_edge is no stricter than the existing edge
        # check for edge in minimal STN, may need to get reverse edge and flip it
        existing_edge = find_edge(min_stn,*new_edge[0])
        intersected_edge = new_edge
        if existing_edge is not None:
            intersected_edge = intersect_edges(new_edge,existing_edge)
            if intersected_edge == existing_edge:
                return (True,minimal_edge_add_lst,minimal_edge_remove_lst)
            # remove existing edge

        # add intersected_edge

        pass

    # return edge if one exists between node_0 and node_1
    # if edge (node_0, node_1) does not exist will return edge (node_1, node_0)
    # in the later case will return flipped edge
    # if none of these are true will return None
    # CURRENTLY WRONG
    # NEED TO UPDATE TO PROPERLY FLIP AND INDICATE IT
    def find_edge( self, graph, node_0: int, node_1: int ) -> NetEdgeInput:
        edge = (node_0,node_1)
        if (node_0,node_1) in graph.edges:
            edge_dict = graph.get_edge_data(node_0,node_1)
        elif (node_1,node_0) in graph.edges:
            edge_dict = graph.get_edge_data( node_1, node_0 )
        else:
            return None
        return (edge, edge_dict)

    # given edge (i,j) and edge (j,k) gives composed edge (i,k)
    # adds minimum and maximum delta t's
    def compose_edges( self, edge_ij: NetEdgeInput, edge_jk: NetEdgeInput ) -> NetEdgeInput:
        edge_ik = ( edge_ij[0][0], edge_jk[0][1] )
        edge_ik_dict = {
            "min_delta_t": edge_ij[1]["min_delta_t"] + edge_jk[1]["min_delta_t"],
            "max_delta_t": edge_ij[ 1 ][ "max_delta_t" ] + edge_jk[ 1 ][ "max_delta_t" ],
        }
        return (edge_ik,edge_ik_dict)

    # given 2 parallel edges get intersection
    # edge_ij intersect edge_ij' has max min_delta_t and the min max_delta_t
    def intersect_edges( self, edge: NetEdgeInput, edge_prime: NetEdgeInput ) -> NetEdgeInput:
        if edge[0] != edge[1]:
            raise "cannot intersect two edges that are not parallel"
        edge_ik_dict = {
            "min_delta_t": max( edge[1]["min_delta_t"], edge_prime[1]["min_delta_t"] ),
            "max_delta_t": min( edge[ 1 ][ "max_delta_t" ], edge_prime[ 1 ][ "max_delta_t" ] ),
        }
        return (edge[0],edge_ik_dict)

    # edge_ij, edge_jk, and edge_ik consistency check
    # returns  intersect( compose( edge_ij, edge_jk ), edge_ik ) if result is not empty else None
    # the intersection is empty if the resulting edge has max_delta_t < min_delta_t
    def consistency_check( self, edge_ij: NetEdgeInput, edge_jk: NetEdgeInput, edge_ik: NetEdgeInput
                           ) -> Union[None,NetEdgeInput]:
        composed_edge = self.compose_edges(edge_ij,edge_jk)
        intersected_edge = self.intersect_edges(composed_edge,edge_ik)
        if intersected_edge[1]["max_delta_t"] < intersected_edge[1]["min_delta_t"]:
            return intersected_edge
        else:
            return None

    # returns minimal and maximal bound edges for a node as 2 entry list
    # 0: minimal edge, 1: maximal edge
    def get_bounding_edges( self, node: int ) -> List[NetEdgeInput,NetEdgeInput]:
        t_min = self.t_min
        t_max = self.t_max
        min_bound_edge = self.get_formatted_edge( (-1, "<=", v, t_min) )
        max_bound_edge = self.get_formatted_edge( (-2, ">=", v, t_max) )
        return [min_bound_edge, max_bound_edge]

    # add temporal constraints to full and minimal networks
    # if inconsistency found, restore networks to before call
    # returns bool indicating success of operations
    def update_temporal_constraints( self, t_con_lst: List[TemporalConstraint] ) -> bool:

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
