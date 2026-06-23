#!/usr/bin/env python
"""
File Description: Satellite actions file. All the actions for Satellite planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/satellite/adlSat-pure.lisp

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

The state is described with following properties:
- rigid = dict of properties that should not change
    - type_dict = dict with types as keys and sets of all objects of the corresponding type as values
    - on_board = dict with satellites as keys and set of on board instrument as values
    - calibration_target = dict with instrument as key and direction for calibration as value
    - supports = dict with instrument as key and set of supported modes as value
- pointing = dict with satellite as key and direction pointing as value
- power_avail = dict with satellite as key and bool indicating whether power is available as value
- power_on = dict with instrument as key and bool indicating whether instrument is turn on
- calibrated = dict with instrument as key and bool indicating whether instrument is calibrated
- have_image = dict with ( direction, mode ) as key and bool representing whether image has been taken as value

"""

from ipyhop import Actions
from typing import List, Dict, Set

def turn_to( state, s, d_new, d_prev, rigid ):
    type_dict = rigid[ "type_dict" ]
    pointing = state.pointing
    # type check
    if type_check(
            [ s, d_new, d_prev ],
            [ "satellite", "direction", "direction" ],
            type_dict ):
        # precondtions
        # s pointing at d_prev
        # d_new not d_prev
        if pointing[ s ] == d_prev and d_new != d_prev:
            # effects
            # s now pointing at _new
            state.pointing[ s ] = d_new
            return state

def switch_on( state, i, s, rigid ):
    type_dict = rigid[ "type_dict" ]
    on_board = rigid[ "on_board" ]
    power_avail = state.power_avail
    # type check
    if type_check(
        [ i, s ],
        [ "instrument", "satellite" ],
        type_dict
    ):
        # preconditions
        # i on s
        # s has power available
        if i in on_board[ s ] and power_avail[ s ]:
            # effects
            # i is powered on
            state.power_on[ i ] = True
            # i in uncalibrated
            state.calibrated[ i ] = False
            # s has no power available
            state.power_avail[ s ] = False
            return state

def switch_off( state, i, s, rigid ):
    type_dict = rigid[ "type_dict" ]
    on_board = rigid[ "on_board" ]
    power_on = state.power_on
    # type check
    if type_check(
        [ i, s ],
        [ "instrument", "satellite" ],
        type_dict
    ):
        # preconditions
        # i on s
        # i is powered on
        if i in on_board[ s ] and power_on[ i ]:
            # effects
            # i is powered off
            state.power_on[ i ] = False
            # s has power available
            state.power_avail[ s ] = True
            return state

def calibrate( state, s, i, d, rigid ):
    type_dict = rigid[ "type_dict" ]
    on_board = rigid[ "on_board" ]
    power_on = state.power_on
    calibration_target = rigid[ "calibration_target" ]
    pointing = state.pointing
    # type check
    if type_check(
        [ s, i, d ],
        [ "satellite", "instrument", "direction" ],
        type_dict
    ):
        # preconditions
        # i is on s
        # d is calibration target for i
        # s is pointing at d
        # i has power_on
        if all( [
            i in on_board[ s ],
            calibration_target[ i ] == d,
            pointing[ s ] == d,
            power_on[ i ]
        ] ):
            # effects
            # i is calibrated
            state.calibrated[ i ] = True
            return state

def take_image( state, s, d, i, m, rigid ):
    type_dict = rigid[ "type_dict" ]
    on_board = rigid[ "on_board" ]
    calibrated = state.calibrated
    power_on = state.power_on
    supports = rigid[ "supports" ]
    pointing = state.pointing
    # type check
    if type_check(
            [ s, d, i, m ],
            [ "satellite", "direction", "instrument", "mode" ],
            type_dict
    ):
        # preconditions
        # i calibrated
        # i on s
        # i supports m
        # i is powered on
        # s pointing at d
        if all( [
            calibrated[ i ],
            i in on_board[ s ],
            m in supports[ i ],
            power_on[ i ],
            pointing[ s ] == d
        ] ):
            # effects
            # have image ( d, m )
            image = ( d, m )
            state.have_image[ image ] = True
            return state


# Create a IPyHOP Actions object. An Actions object stores all the actions defined for the planning domain.
actions = Actions()
actions.declare_actions( [ turn_to, switch_on, switch_off, calibrate, take_image ] )

p_fail = 1
action_probability = {
    "turn_to": [ 1 - p_fail, p_fail ],
    "switch_on": [ 1 - p_fail, p_fail ],
    "switch_off": [ 1 - p_fail, p_fail ],
    "calibrate": [ 1 - p_fail, p_fail ],
    "take_image": [ 1 - p_fail, p_fail ]
}

action_cost = {
    "turn_to": 1,
    "switch_on": 1,
    "switch_off": 1,
    "calibrate": 1,
    "take_image": 1
}

actions.declare_action_models(action_probability, action_cost)

# ******************************************    Helper Functions            ****************************************** #

# takes list of entities to be type checked, their expected types, and a dict defining the objects for each type
# returns True if all checks are good else False
def type_check( entity_list: List[ str ], type_list: List[ str ], type_dict: Dict[ str, Set[ str ] ] ) -> bool:
    return all( map( lambda x, y: True if x in type_dict[ y ] else False, entity_list, type_list ) )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Satellites Actions isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""