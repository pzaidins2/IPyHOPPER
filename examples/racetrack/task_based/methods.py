#!/usr/bin/env python
"""
File Description: Racetrack methods file. All the methods for Racetrack planning domain are defined here.
Derived from: PyHOP example of Racetrack varient domain by Dana Nau <nau@cs.umd.edu>

Each IPyHOP method is a Python function. The 1st argument is the current state (this is analogous to Python methods,
in which the first argument is the class instance). The rest of the arguments must match the arguments of the
task that the method is for. For example, the task ('get', b1) has a method "tm_get(state, b1)", as shown below.
"""
from typing import List

import numpy as np

from ipyhop import Methods
from examples.racetrack.search.racetrack import crash, intersect, goal_test
from examples.racetrack.search.racetrack import main as search
from examples.racetrack.search.sample_heuristics import h_esdist
import numpy


# ******************************************        Helper Functions        ****************************************** #

offset = []
for i in [ -1, 0, 1 ]:
    for j in [ -1, 0, 1 ]:
        offset.append( ( i, j ) )
offset = np.asarray( offset )

# give possible next loc: v pairs achievable from current state
def get_next_possible_attitude( loc, v, walls ):
    pos_next_attitude = dict()
    new_vs = np.asarray( v ) + offset
    new_locs = np.asarray( loc ) + new_vs
    # print(new_loc)
    # print(new_loc in vis_points)
    for i in range( new_locs.shape[ 0 ] ):
        new_loc = tuple( new_locs[ i ] )
        new_v = tuple( new_vs[ i ] )
        if not crash( ( loc, new_loc ), walls ):
            pos_next_attitude[ new_loc ] = new_v
    return pos_next_attitude

# ******************************************        Method Definitions        **************************************** #

# Create a IPyHOP Methods object. A Methods object stores all the methods defined for the planning domain.
methods = Methods()

def tm_finish_at(state, f_line):
    return [ ( "generate_visibility_graph", f_line ) ]
    # strategy = "gbf"
    # h = h_esdist
    # loc = state.loc
    # v = state.v
    # walls = [ *state.walls ]
    # problem = [ loc, [*f_line], walls ]
    # path_onwards = search( problem, strategy, h, v_0=v, draw=1)
    # # use first action in list until at f_line with v= (0,0)
    # if goal_test( path_onwards[ 1 ], f_line ):
    #     return [ ( "set_v", path_onwards[ 1 ][ 1 ]  ) ]
    # else:
    #     return [ ( "set_v", path_onwards[ 1 ][ 1 ]  ), ( "finish_at", f_line ) ]


methods.declare_task_methods( "finish_at", [tm_finish_at])

# generate point grid
def tm_generate_visibility_graph(state, f_line):
    # get all points in problem
    loc = state.loc
    walls = state.rigid[ "walls" ]
    wall_points = set()
    for line in walls:
        wall_points.add( line[ 0 ] )
        wall_points.add( line[ 1 ] )
    # get points on f_line
    f_line_array = np.asarray(f_line)
    x_min, y_min = np.min(f_line_array, axis=0)
    x_max, y_max = np.max(f_line_array, axis=0)
    goal_pts = set()
    for i in range(x_min, x_max + 1):
        for j in range(y_min, y_max + 1):
            pt = (i, j)
            if intersect((pt, pt), f_line):
                goal_pts.add(pt)
    state.rigid["goal_pts"] = goal_pts
    # get surrounding points for all vertices
    points = { loc, *goal_pts, *wall_points }

    points_array = np.asarray( [ *points ] )
    points_array = points_array[ :, :, np.newaxis ] + np.transpose( offset )[ np.newaxis, : , :]
    points_array = np.reshape( points_array, ( points_array.shape[ 0 ] * points_array.shape[ 2 ], points_array.shape[ 1 ] ), order="F" )

    points = { tuple( pt ) for pt in points_array }
    # points_array = []
    # for pt in points:
    #     adj_pts = np.asarray( pt ) + offset
    #     points_array += [ tuple( adj_pt ) for adj_pt in adj_pts ]
    # points = { *points_array }
    # points_array = np.asarray( points_array )

    # generate visibility graph
    vis_graph = dict()
    start_pt = loc
    unexpanded_pts = [ start_pt ]
    visited_pts = set()
    # continue expansion until all nodes reachable by start
    while unexpanded_pts != []:
        print(len(visited_pts))
        curr_pt = unexpanded_pts.pop()
        visited_pts.add( curr_pt )
        vis_graph[ curr_pt ] = set()
        # rng = np.random.default_rng()
        # N = 1
        # check each int point in bounding box for visibility
        for pt in points:
            move = ( curr_pt, pt )
            # print( move )
            # print( crash( move, walls ) )
            # visible if move would not cause crash
            if not crash( move, walls ):
                vis_graph[ curr_pt ].add( pt )
                # if pt in vis_graph.keys():
                #     vis_graph[ pt ].add( curr_pt )
                # else:
                #     vis_graph[ pt ] = { curr_pt }
                # add node to unexpanded if not previously encountered
                if pt not in visited_pts and pt not in unexpanded_pts:
                    unexpanded_pts.append( pt )
    # no path exists
    if all(  [ goal_pt not in vis_graph.keys() for goal_pt in goal_pts ] ):
        print("No GOAL PT IN VIS_GRAPH")
        print( goal_pts )
        print(vis_graph.keys())
        return
    # iterate over points in visibility graph to get minimum distance to
    # create dict of min distance to start point of finish line
    dist_dict = dict()
    # start with points directly reachable by finish line start
    unexpanded_pts = [ *goal_pts ]
    dist_dict.update( { pt: 0 for pt in goal_pts } )
    visited_pts = set()
    # continue expansion until all nodes have min cost
    while unexpanded_pts != []:
        curr_pt = unexpanded_pts.pop()
        visited_pts.add( curr_pt )
        # get visible points
        vis_points = vis_graph[ curr_pt ]
        # print("DIST_DICT CALC")
        # print(vis_points)
        # get distance to visible points
        dist_to = { pt: np.linalg.norm( np.asarray( curr_pt ) - np.asarray( pt ) )
                      for pt in vis_points }
        dist_from = dist_dict[ curr_pt ]
        # update dist_dict for all visible points
        for pt in vis_points:
            dist = dist_to[ pt ] + dist_from
            if pt in dist_dict.keys():
                dist_dict[ pt ] = min( dist_dict[ pt ], dist )
            else:
                dist_dict[ pt ] = dist
                unexpanded_pts.append( pt )
    if loc not in dist_dict.keys():
        print( "LOC NOT IN DIST_DICT")
        print( dist_dict.keys() )
        return
    state.rigid[ "vis_graph" ] = vis_graph
    state.rigid[ "dist_dict" ] = dist_dict
    return [ ("hill_climb",) ]

methods.declare_task_methods( "generate_visibility_graph", [tm_generate_visibility_graph])

def tm_hill_climb( state ):
    loc = state.loc
    v = state.v
    vis_graph = state.rigid[ "vis_graph" ]
    dist_dict = state.rigid[ "dist_dict" ]
    goal_pts = state.rigid[ "goal_pts" ]
    way_points = []
    wp = loc
    # vis_graph = state.vis_graph
    # dist_dict = state.dist_dict
    # limit distance between waypoints based on current velocity
    max_wp_dist = 15
    while True:
        # visible points
        vis_points = [ *filter( lambda x: np.linalg.norm( np.asarray( x ) - np.asarray( wp )  ) <= max_wp_dist, vis_graph[ wp ] ) ]
        # points that can be achieved given current v, loc and visibility
        vis_points.sort( key=lambda x: dist_dict[ x ] )
        wp = vis_points[ 0 ]
        print(wp)
        way_points.append( wp )
        if wp in goal_pts:
            break
    move_tasks = [ ( "move_to", point ) for point in way_points[ :-1 ] ]
    stop_task = ( "stop_at", way_points[ -1 ] )
    print("PLAN")
    print( [ *move_tasks, stop_task ] )
    return [ *move_tasks, stop_task ]


methods.declare_task_methods( "hill_climb", [tm_hill_climb] )

# from state search up to depth deep
# use state that is at target_loc with minimum speed
def move_to( state, target_loc, stop_at=False, depth=1 ):
    print("DEPTH")
    print(depth)
    loc = state.loc
    v = state.v
    walls= state.rigid[ "walls" ]
    # vis_graph = state.vis_graph
    state_chains = { ( ( loc, v ), ) }
    unique_states = { ( loc, v ) }
    # print(state_chains)
    new_state_chains = { *state_chains }
    # explore reachable states up to depth away
    for i in range( depth ):
        new_state_chains_copy = { *new_state_chains }
        new_state_chains = set()
        # only expand for frontier states
        for r_state_chain in new_state_chains_copy:
            r_state = r_state_chain[ -1 ]
            # print( r_state_chain )
            pos_next_attitudes = get_next_possible_attitude( *r_state, walls )
            # print( pos_next_attitudes )
            next_attitudes = { *filter( lambda x: x not in unique_states, pos_next_attitudes.items() ) }
            unique_states = unique_states.union( next_attitudes )
            new_r_state_chains = { ( *r_state_chain, x ) for x in next_attitudes }
            # print("R_STATE_CHAINS")
            # print( new_r_state_chains )
            new_state_chains = new_state_chains.union( new_r_state_chains )
            # print("NEW_STATE_CHAINS")
            # print( new_state_chains )
        state_chains = state_chains.union( new_state_chains )
    # filter states to only those that are at target_loc
    # print( state_chains )
    if stop_at == False:
        target_state_chains = [ *filter( lambda x: x[ -1 ][ 0 ] == target_loc, state_chains ) ]
    else:
        target_state_chains = [ *filter( lambda x: x[ -1 ][ 0 ] == target_loc and x[ -1 ][ 1 ] == ( 0, 0 ),
                                       state_chains ) ]
    # cannot reach desired state within depth
    if len( target_state_chains ) == 0:
        return
    # stable sort to prefer short paths given same speed
    target_state_chains.sort( key=lambda x: len( x ) )
    # get state with lowest speed at target loc
    target_state_chains.sort( key=lambda x: np.linalg.norm( np.asarray( x[ -1 ][ 1 ]  ) ) )
    # print( target_state_chains )
    target_chain = target_state_chains[ 0 ]
    return [ ( "set_v", x[ 1 ] ) for x in target_chain[ 1: ] ]

def move_to_1( state, loc ):
    return move_to( state, loc, depth=1 )

def move_to_2( state, loc ):
    return move_to( state, loc, depth=2 )

def move_to_3( state, loc ):
    return move_to( state, loc, depth=3 )

def move_to_4( state, loc ):
    return move_to( state, loc, depth=4 )

def move_to_5( state, loc ):
    return move_to( state, loc, depth=5 )

def move_to_6( state, loc ):
    return move_to( state, loc, depth=6 )

def move_to_7( state, loc ):
    return move_to( state, loc, depth=7 )

def move_to_8( state, loc ):
    return move_to( state, loc, depth=8 )

def move_to_9( state, loc ):
    return move_to( state, loc, depth=9 )

def move_to_10( state, loc ):
    return move_to( state, loc, depth=10 )

methods.declare_task_methods( "move_to", [ move_to_1, move_to_2, move_to_3, move_to_4, move_to_5,
    move_to_6, move_to_7, move_to_8, move_to_9, move_to_10 ] )

def stop_at( state, loc, depth=1 ):
    return move_to( state, loc, stop_at=True, depth=depth)

def stop_at_1( state, loc ):
    return stop_at( state, loc, depth=1 )

def stop_at_2( state, loc ):
    return stop_at( state, loc, depth=2 )

def stop_at_3( state, loc ):
    return stop_at( state, loc, depth=3 )

def stop_at_4( state, loc ):
    return stop_at( state, loc, depth=4 )

def stop_at_5( state, loc ):
    return stop_at( state, loc, depth=5 )

def stop_at_6( state, loc ):
    return stop_at( state, loc, depth=6 )

def stop_at_7( state, loc ):
    return stop_at( state, loc, depth=7 )

def stop_at_8( state, loc ):
    return stop_at( state, loc, depth=8 )

def stop_at_9( state, loc ):
    return stop_at( state, loc, depth=9 )

def stop_at_10( state, loc ):
    return stop_at( state, loc, depth=10 )

methods.declare_task_methods( "stop_at", [ stop_at_1, stop_at_2, stop_at_3, stop_at_4, stop_at_5,
    stop_at_6, stop_at_7, stop_at_8, stop_at_9, stop_at_10 ]  )

# # have v = (0,0) and loc = dest
# def tm_finish_at( state, f_line ):
#     f_start = f_line[ 0 ]
#     f_end = f_line[ 1 ]
#     dest = ( f_start[ 0 ] + f_end[ 0 ] // 2, f_start[ 1 ] + f_end[ 1 ] // 2)
#     state.f_line = f_line
#     return [("move_close",dest),("park_at",dest)]
#
#
# methods.declare_task_methods('finish_at', [tm_finish_at])
#
# # move car close enough to finish that there are no obstructions
# # no obstruction between loc and dest, attempt to move directly towards
# def tm_move_direct_to( state, dest ):
#     dest_x, dest_y = dest
#     loc = state.loc
#     loc_x, loc_y = loc
#     v = state.v
#     v_x, v_y = v
#     walls = state.walls
#     # prioritize velocity increase in direction of greatest difference
#     strong_axis_index = 0 if ( dest_x - loc_x ) ** 2 >= ( dest_x - loc_x ) else 1
#     weak_axis_index = 1 if strong_axis_index == 0 else 0
#     # strong axis velocity change
#     # increase velocity
#     if dest[ strong_axis_index ]- loc[ strong_axis_index ] > 0:
#         dv = 1
#     # maintain velocity
#     elif dest[ strong_axis_index ] == loc[ strong_axis_index ]:
#         dv = 0
#     # decrease velocity
#     else:
#         dv = -1
#     # crash check
#     dv_tup = [ 0, 0 ]
#     dv_tup[ strong_axis_index ] += dv
#     dv_tup = tuple( dv_tup )
#     new_loc = [ *loc ]
#     new_loc[ strong_axis_index ] += dv
#     new_loc = tuple( new_loc )
#     move = ( loc, new_loc )
#     if not ( dv == 0 or crash( move, walls ) ):
#         # enter parking phase
#         if not crash( ( new_loc, dest ), walls ):
#             return [ ( "change_v", *dv_tup) ]
#         # continue move phase
#         else:
#             return [ ( "change_v", *dv_tup ), ( "move_close", dest ) ]
#     # weak axis velocity change
#     # increase velocity
#     if dest[ weak_axis_index ] - loc[ weak_axis_index ] > 0:
#         dv = 1
#     # maintain velocity
#     elif dest[ weak_axis_index ] == loc[ weak_axis_index ]:
#         dv = 0
#     # decrease velocity
#     else:
#         dv = -1
#     # crash check
#     dv_tup = [ 0, 0 ]
#     dv_tup[ weak_axis_index ] += dv
#     dv_tup = tuple( dv_tup )
#     new_loc = [ *loc ]
#     new_loc[ weak_axis_index ] += dv
#     new_loc = tuple( new_loc )
#     move = ( loc, new_loc )
#     # NOTE that here we allow for no velocity change
#     if not crash( move, walls ):
#         # enter parking phase
#         if not crash( (new_loc, dest ), walls ):
#             return [ ( "change_v", *dv_tup ) ]
#         # continue move phase
#         else:
#             return [ ( "change_v", *dv_tup ), ( "move_close", dest ) ]
#
# # an obstacle exists between racecar and destination
# # try and set velocity parallel to wall
# def tm_follow_wall_parallel( state, dest ):
#     loc = state.loc
#     loc_x, loc_y = loc
#     v = state.v
#     v_x, v_y = v
#     walls = state.walls
#     move = ( loc, dest )
#     # iterate over walls
#     for wall in walls:
#         # follow along wall with first intersection
#         if intersect( move, wall ):
#             wall_start, wall_end = wall
#             d_wall = ( wall_end[ 0 ] - wall_start[ 0 ], wall_end[ 1 ] - wall_start[ 1 ] )
#             sub_dest = ( loc[ 0 ] + d_wall[ 0 ], loc[ 1 ] + d_wall[ 1 ] )
#             plan = tm_move_direct_to( state, sub_dest )
#             # move in direction of wall one step if possible
#             if plan is not None:
#                 return [ plan[ 0 ], ( "move_close", dest ) ]
#
# # an obstacle exists between racecar and destination
# # try and set velocity antiparallel to wall
# def tm_follow_wall_antiparallel( state, dest ):
#     loc = state.loc
#     loc_x, loc_y = loc
#     v = state.v
#     v_x, v_y = v
#     walls = state.walls
#     move = ( loc, dest )
#     # iterate over walls
#     for wall in walls:
#         # follow along wall with first intersection
#         if intersect( move, wall ):
#             wall_start, wall_end = wall
#             d_wall = ( wall_end[ 0 ] - wall_start[ 0 ], wall_end[ 1 ] - wall_start[ 1 ] )
#             sub_dest = ( loc[ 0 ] - d_wall[ 0 ], loc[ 1 ] - d_wall[ 1 ] )
#             plan = tm_move_direct_to( state, sub_dest )
#             # move in direction of wall one step if possible
#             if plan is not None:
#                 return [ plan[ 0 ], ( "move_close", dest ) ]
#
# methods.declare_task_methods( 'move_close', [ tm_move_direct_to, tm_follow_wall_parallel, tm_follow_wall_antiparallel ] )
#
# # we now have an unobstructed path to goal
# # guide racecar towards goal while slowing down to stop at goal
# def tm_park_at( state, dest ):
#     v = state.v
#     loc = state.loc
#     plan = tm_move_direct_to( state, dest )
#     # guide car towards destination, if obstruction occurs then use long distance protocal again
#     if plan is not None:
#         _, dv_x, dv_y = plan[ 0 ]
#         new_v = ( v[ 0 ] + dv_x, v[ 1 ] + dv_y )
#         new_loc = ( loc[ 0 ] + new_v[ 0 ], loc[ 1 ] + new_v[ 1 ] )
#         f_line = state.f_line
#         if goal_test( ( new_loc, new_v ), f_line ):
#             return [ plan[ 0 ] ]
#         else:
#             return [ plan[ 0 ], ( "park_at", dest ) ]
#     else:
#         return [ ( "move_close",dest ),( "park_at", dest ) ]
#
# methods.declare_task_methods( 'part_at', [ tm_park_at ] )
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Blocks World Mehthods isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""
