#!/usr/bin/env python
"""
File Description: Roversactions file. All the actions for Rovers planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/rovers/domain.pddl

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

The state is described with following properties:
- rigid = dict of properties that should not change
    - type_dict = dict with types as keys and sets of all objects of the corresponding type as values
    - equipped_for_soil_analysis = dict with rover as key and bool value
    - equipped_for_rock_analysis = dict with rover as key and bool value
    - equipped_for_imaging = dict with rover as key and bool value
    - supports = dict with camera as key and set of modes as value
    - visible = dict with waypoint as key and set of waypoints as value

    - store_of = dict with store as key and rover as value
    - has_store = dict with rover as key and store as value
    - calibration_target = dict with camera as key and objective as value
    - on_board = dict with camera as key and rover as value
    - carries = dict with rover as key and set of cameras on_board as value
    - at_lander = dict with lander as key and the location waypoint as value
    - can_traverse = dict with rover as key and set of ( waypoint, waypoint ) as value
- at = dict with rover as key and the location waypoint as value

- empty = set of empty stores
- have_rock_analysis = dict with rover as key and set of waypoints at value
- have_soil_analysis = dict with rover as key and set of waypoints at value
- full = set of full stores
- calibrated = dict with ( camera, rover ) key and bool value
- available = set of available rovers Note: doesn't appear to be used
- have_image = dict with rover as key and set of ( objective, mode ) as value
- communicated_soil_data = dict with waypoint as key and bool value
- communicated_rock_data = dict with waypoint as key and bool value
- communicated_image_data = dict with ( waypoint, mode ) as key and bool value
- at_soil_sample = dict with waypoint as key and bool value
- at_rock_sample = dict with waypoint as key and bool value
- channel_free = dict with lander as key and bool as value
- visible_from = dict with objective as key and set of waypoints as value (deviations modify this)
"""

from ipyhop import Actions
from typing import List, Dict, Set

def navigate( state, r, p_0, p_1, rigid ):
    type_dict = rigid[ "type_dict" ]
    can_traverse = rigid[ "can_traverse" ]
    available = state.available
    at = state.at
    visible = rigid[ "visible" ]
    # type check
    if type_check( [ r, p_0, p_1 ], [ "rover", "waypoint", "waypoint" ], type_dict ):
        # preconditions
        # r can traverse from p_0 to p_1
        # r is available
        # r is at p_0
        # w_1 is visible from p_0
        if r in available and at[ r ] == p_0 and p_1 in visible[ p_0 ] and (p_0, p_1) in can_traverse[ r ]:
            # effects
            # location of r is now p_1
            state.at[ r ] = p_1
            return state

def sample_soil( state, r, s, p, rigid ):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    at_soil_sample = state.at_soil_sample
    equipped_for_soil_analysis = rigid[ "equipped_for_soil_analysis" ]
    store_of = rigid[ "store_of" ]
    empty = state.empty
    # type check
    if type_check( [ r, s, p ], [ "rover", "store", "waypoint" ], type_dict ):
        # preconditions
        # r is at p
        # p is at soil sample
        # r is equipped for soil analysis
        # s is a store of r
        # s is empty
        if s in empty and equipped_for_soil_analysis[ r ] and \
                p in at_soil_sample and at[ r ] == p and store_of[ s ] == r:
            # effects
            # s is not emptu
            # s is full
            # have soil analysis ( r, p )
            # p is not at soil_sample
            state.empty.remove( s )
            state.full.add( s )
            state.have_soil_analysis[ r ].add( p )
            state.at_soil_sample.remove( p )
            return state

def sample_rock( state, r, s, p, rigid ):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    at_rock_sample = state.at_rock_sample
    equipped_for_rock_analysis = rigid[ "equipped_for_rock_analysis" ]
    store_of = rigid[ "store_of" ]
    empty = state.empty
    # type check
    if type_check( [ r, s, p ], [ "rover", "store", "waypoint" ], type_dict ):
        # preconditions
        # r is at p
        # p is at rock sample
        # r is equipped for rock analysis
        # s is a store of r
        # s is empty
        if s in empty and equipped_for_rock_analysis[ r ] and \
                p in at_rock_sample and at[ r ] == p and store_of[ s ] == r:
            # effects
            # s is not emptu
            # s is full
            # have rock analysis ( r, p )
            # p is not at rock_sample
            state.empty.remove( s )
            state.full.add( s )
            state.have_rock_analysis[ r ].add( p )
            state.at_rock_sample.remove( p )
            return state

def drop( state, r, s, rigid ):
    type_dict = rigid[ "type_dict" ]
    store_of = rigid[ "store_of" ]
    full = state.full
    # type check
    if type_check( [ r, s ], [ "rover", "store" ], type_dict ):
        # preconditions
        # s is store of r
        # s is full
        if s in full and store_of[ s ] == r:
            # effects
            # s is not full
            # s is empty
            state.full.remove( s )
            state.empty.add( s )
            return state

def calibrate( state, r, i, t, w, rigid ):
    type_dict = rigid[ "type_dict" ]
    equipped_for_imaging = rigid[ "equipped_for_imaging" ]
    calibration_target = rigid[ "calibration_target" ]
    at = state.at
    visible_from = state.visible_from
    on_board = rigid[ "on_board" ]
    # type check
    if type_check( [ r, i, t, w ], [ "rover", "camera", "objective", "waypoint" ], type_dict ):
        # preconditions
        # r is equipped for imagining
        # t is the calibration target of i
        # r is at w
        # t is visible from w
        # i is on r
        if equipped_for_imaging[ r ] and calibration_target[ i ] == t and at[ r ] == w and \
            on_board[ i ] == r and w in visible_from[ t ]:
            # effects
            # calibrate i on r
            state.calibrated[ ( i, r ) ] = True
            return state

def take_image( state, r, p, o, i, m, rigid ):
    type_dict = rigid[ "type_dict" ]
    equipped_for_imaging = rigid[ "equipped_for_imaging" ]
    at = state.at
    visible_from = state.visible_from
    on_board = rigid[ "on_board" ]
    calibrated = state.calibrated
    supports = rigid[ "supports" ]

    # type check
    if type_check( [ r, p, o, i , m ], [ "rover", "waypoint", "objective", "camera", "mode" ], type_dict ):
        # preconditions
        # i on r calibrated
        # i on r
        # i supports m
        # o visible from p
        # r at p
        if calibrated[ ( i, r ) ] and equipped_for_imaging[ r ] and on_board[ i ] == r and at[ r ] == p and \
            m in supports[ i ] and p in visible_from[ o ]:
            # effects
            # r has image ( o, m )
            # ( i, r ) no longer calibrated
            state.have_image[ r ].add( ( o, m ) )
            state.calibrated[ ( i, r ) ] = False
            return state

def communicate_soil_data( state, r, l, p_0, p_1, p_2, rigid ):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    visible= rigid[ "visible" ]
    at_lander = rigid[ "at_lander" ]
    have_soil_analysis = state.have_soil_analysis
    available = state.available
    channel_free = state.channel_free
    # type check
    if type_check( [ r, l, p_0, p_1, p_2 ], [ "rover", "lander", "waypoint", "waypoint", "waypoint" ], type_dict ):
        # preconditions
        # r at p_1
        # l at p_2
        # have soil analysis ( r, p_0 )
        # p_2 visible from p_1
        # r available
        # l has free channel
        if r in available  and at[ r ] == p_1 and at_lander[ l ] == p_2 and l in channel_free and \
                p_0 in have_soil_analysis[ r ] and p_2 in visible[ p_1 ]:
            # effects
            # soil data of p_0 has been communicated
            state.communicated_soil_data[ p_0 ] = True
            state.available.add( r )
            state.channel_free.add( l )
            return state

def communicate_rock_data( state, r, l, p_0, p_1, p_2, rigid ):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    visible= rigid[ "visible" ]
    at_lander = rigid[ "at_lander" ]
    have_rock_analysis = state.have_rock_analysis
    available = state.available
    channel_free = state.channel_free
    # type check
    if type_check( [ r, l, p_0, p_1, p_2 ], [ "rover", "lander", "waypoint", "waypoint", "waypoint" ], type_dict ):
        # preconditions
        # r at p_1
        # l at p_2
        # have rock analysis ( r, p_0 )
        # p_2 visible from p_1
        # r available
        # l has free channel
        if r in available and at[ r ] == p_1 and at_lander[ l ] == p_2 and l in channel_free and \
                p_0 in have_rock_analysis[ r ] and p_2 in visible[ p_1 ]:
            # effects
            # rock data of p_0 has been communicated
            state.communicated_rock_data[ p_0 ] = True
            state.available.add( r )
            state.channel_free.add( l )
            return state

def communicate_image_data( state, r, l, o, m, p_0, p_1, rigid ):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    visible= rigid[ "visible" ]
    at_lander = rigid[ "at_lander" ]
    have_image = state.have_image
    available = state.available
    channel_free = state.channel_free
    # type check
    if type_check( [ r, l, o, m, p_0, p_1 ],
                   [ "rover", "lander", "objective", "mode", "waypoint", "waypoint" ], type_dict ):
        # preconditions
        # r at p_0
        # l at p_1
        # have rock analysis ( r, p_0 )
        # p_2 visible from p_1
        # r available
        # l has free channel
        if r in available  and at[ r ] == p_0 and at_lander[ l ] == p_1 and l in channel_free and \
                ( o, m ) in have_image[ r ] and p_1 in visible[ p_0 ]:
            # effects
            # rock data of p_0 has been communicated
            state.communicated_image_data[ ( o, m ) ] = True
            state.available.add( r )
            state.channel_free.add( l )
            return state

# replicate !!retract macro effect without having state changes in method
def retract( state, field, key, rigid ):
    state_attr = getattr( state, field )
    state_attr[ key ] = False
    return state




# Create a IPyHOP Actions object. An Actions object stores all the actions defined for the planning domain.
actions = Actions()
actions.declare_actions( [ navigate, sample_soil, sample_rock, drop, calibrate, take_image, communicate_soil_data,
                           communicate_rock_data, communicate_image_data, retract ] )

p_fail = 1
action_probability = {
    "navigate": [ 1 - p_fail, p_fail ],
    "sample_soil": [ 1 - p_fail, p_fail ],
    "sample_rock": [ 1 - p_fail, p_fail ],
    "drop": [ 1 - p_fail, p_fail ],
    "calibrate": [ 1 - p_fail, p_fail ],
    "take_image": [ 1 - p_fail, p_fail ],
    "communicate_soil_data": [ 1 - p_fail, p_fail ],
    "communicate_rock_data": [ 1 - p_fail, p_fail ],
    "communicate_image_data": [ 1 - p_fail, p_fail ],
    "retract": [ 1 - p_fail, p_fail ]
}

action_cost = {
    "navigate": 1,
    "sample_soil": 1,
    "sample_rock": 1,
    "drop": 1,
    "calibrate": 1,
    "take_image": 1,
    "communicate_soil_data": 1,
    "communicate_rock_data": 1,
    "communicate_image_data": 1,
    "retract": 1
}

actions.declare_action_models(action_probability, action_cost)

# ******************************************    Helper Functions            ****************************************** #

# takes list of entities to be type checked, their expected types, and a dict defining the objects for each type
# returns True if all checks are good else False
def type_check( entity_list: List[ str ], type_list: List[ str ], type_dict: Dict[ str, Set[ str ] ] ) -> bool:
    return all( map( lambda x, y: True if x in type_dict[ y ] else False, entity_list, type_list ) )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Rovers Actions isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""