#!/usr/bin/env python
"""
File Description: Satellite methods file. All the methods for Satellite planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/satellite/adlSat-pure.lisp

Each IPyHOP method is a Python function. The 1st argument is the current state (this is analogous to Python methods,
in which the first argument is the class instance). The rest of the arguments must match the arguments of the
task that the method is for. For example, the task ('get', b1) has a method "tm_get(state, b1)", as shown below.
"""

from ipyhop import Methods
from examples.satellite.domain.actions import type_check

# ******************************************    Helper Functions                     ********************************* #


# ******************************************    Methods                     ****************************************** #


N = 1

# Create a IPyHOP Methods object. A Methods object stores all the methods defined for the planning domain.
methods = Methods()

def mgm_main( state, multigoal, rigid ):
    state_have_image = state.have_image
    mg_have_image = multigoal.have_image
    # get have_image goal that is not fulfilled
    for g_image in mg_have_image.keys():
        if not state_have_image[ g_image ]:
            yield [ ("have_image", g_image, True), multigoal ]

    state_pointing = state.pointing
    mg_pointing = multigoal.pointing
    # get pointing goal that is not fulfilled
    for s, mg_d in mg_pointing.items():
        state_d = state_pointing[ s ]
        if state_d != mg_d:
            yield [ ( "turn_to", s, mg_d, state_d ), multigoal ]

    # end when all pointing and have_image goals are fufilled
    if ( len( { *mg_have_image.items() } - { *state_have_image.items() } ) == 0 and
            len( { *mg_pointing.items() } - { *state_pointing.items() } ) == 0 ):
        yield [ ]


def mgm_main_0( state, multigoal, rigid ):
    # state_have_image = { *state.have_image.items() }
    # mg_have_image = { *multigoal.have_image.items() }
    # # get have_image goal that is not fulfilled
    # for g_have_image in mg_have_image - state_have_image:
    #     yield [ ( "have_image", g_have_image[ 0 ], True ), multigoal ]
    state_have_image = state.have_image
    mg_have_image = multigoal.have_image
    # get have_image goal that is not fulfilled
    for g_image in mg_have_image.keys():
        if not state_have_image[ g_image ]:
            yield [ ("have_image", g_image, True), multigoal ]

def mgm_main_1( state, multigoal, rigid ):
    # pointing = state.pointing
    # state_pointing = { *pointing.items() }
    # mg_pointing = { *multigoal.pointing.items() }
    # # get pointing goal that is not fulfilled
    # for g_pointing in mg_pointing - state_pointing:
    #     s = g_pointing[ 0 ]
    #     d_new = g_pointing[ 1 ]
    #     d_prev = pointing[ s ]
    #     yield [ ( "turn_to", s, d_new, d_prev ), multigoal ]
    state_pointing = state.pointing
    mg_pointing = multigoal.pointing
    # get pointing goal that is not fulfilled
    for s in mg_pointing.keys():
        mg_d = mg_pointing[ s ]
        state_d = state_pointing[ s ]
        if state_d != mg_d:
            yield [ ( "turn_to", s, mg_d, state_d ), multigoal ]

def mgm_main_2( state, multigoal ):
    pointing = state.pointing
    state_pointing = { *pointing.items() }
    mg_pointing = { *multigoal.pointing.items() }
    state_have_image = { *state.have_image.items() }
    mg_have_image = { *multigoal.have_image.items() }
    # end when all pointing and have_image goals are fulfilled
    if len( mg_pointing - state_pointing ) == 0 and len( mg_have_image - state_have_image ) == 0:
        yield []

methods.declare_multigoal_methods( None, N*[ mgm_main ] )

def gm_have_image( state, image, val, rigid ):
    d, m = image
    # rigid = 
    type_dict = rigid[ "type_dict" ]
    satellites = type_dict[ "satellite" ]
    on_board = rigid[ "on_board" ]
    supports = rigid[ "supports" ]
    # iterate over satellites
    for s in satellites:
        # iterate over on_board instruments
        i_on_s = on_board[ s ]
        for i in i_on_s:
            # find i on s that supports m
            if m in supports[ i ]:
                yield [ ( "t_prepare_instrument", s, i ), ( "t_take_image", s, i, d, m ) ]

methods.declare_goal_methods( "have_image", N * [ gm_have_image ] )

def tm_take_image( state, s, i, d, m, rigid ):

    pointing = state.pointing
    d_prev = pointing[ s ]
    # s pointing at d
    if (d_prev == d):
        yield [ ("take_image", s, d, i, m) ]

    # s not pointing at d
    else:
        yield [ ("turn_to", s, d, d_prev), ("take_image", s, d, i, m) ]

def tm_take_image_0( state, s, i, d, m, rigid ):
    pointing = state.pointing
    # s pointing at d
    if( pointing[ s ] == d ):
        yield [ ( "take_image", s, d, i, m ) ]

def tm_take_image_1( state, s, i, d, m, rigid ):
    pointing = state.pointing
    # s not pointing at d
    if( pointing[ s ] != d ):
        d_prev = pointing[ s ]
        yield [ ( "turn_to", s, d, d_prev ), ( "take_image", s, d, i, m ) ]

methods.declare_task_methods( "t_take_image", N*[ tm_take_image ] )

def tm_prepare_instrument( state, s, i, rigid ):
    yield [ ( "t_turn_on_instrument", s, i ), ( "t_calibrate_instrument", s, i ) ]

methods.declare_task_methods( "t_prepare_instrument", N*[ tm_prepare_instrument ] )

def tm_turn_on_instrument( state, s, i, rigid ):

    # i already has power
    power_on = state.power_on
    if power_on[ i ]:
        yield [ ]

    else:
        # s has no powered instruments
        power_avail = state.power_avail
        if power_avail[ s ]:
            yield [ ("switch_on", i, s) ]

        else:
            # s has one powered instrument that is not i
            on_board = rigid[ "on_board" ]
            for i_on_s in on_board[ s ]:
                if power_on[ i_on_s ]:
                    yield [ ("switch_off", i_on_s, s), ("switch_on", i, s) ]
                    # no point in searching after first instance
                    break

def tm_turn_on_instrument_0( state, s, i, rigid ):
    # i already has power
    power_on = state.power_on
    if power_on[ i ]:
        yield []

def tm_turn_on_instrument_1( state, s, i, rigid ):
    # s has no powered instruments
    power_avail = state.power_avail
    if power_avail[ s ]:
        yield [ ( "switch_on", i, s )]


def tm_turn_on_instrument_2( state, s, i, rigid ):
    power_on = state.power_on
    on_board = rigid[ "on_board" ]
    # s has one powered instrument that is not i
    for i_on_s in on_board[ s ]:
        if power_on[ i_on_s ] and i_on_s != i:
            yield [ ( "switch_off", i_on_s, s ), ( "switch_on", i, s ) ]

methods.declare_task_methods( "t_turn_on_instrument", N*[ tm_turn_on_instrument ] )

def tm_calibrate_instrument( state, s, i, rigid ):

    power_on = state.power_on
    calibrated = state.calibrated
    # i on and calibrated
    if power_on[ i ]:
        if calibrated[ i ]:
            yield [ ]

        # not calibrated
        else:
            pointing = state.pointing
            calibration_target = rigid[ "calibration_target" ]
            d = pointing[ s ]
            d_new = calibration_target[ i ]
            # i on and s pointing at calibration target of i
            if d_new == d:
                yield [ ("calibrate", s, i, d) ]

            else:
                # i on and s not pointing at calibration target of i
                yield [ ( "turn_to", s, d_new, d ), ( "calibrate", s, i, d_new ) ]

def tm_calibrate_instrument_0( state, s, i, rigid ):
    power_on = state.power_on
    calibrated = state.calibrated
    # i on and calibrated
    if power_on[ i ] and calibrated[ i ]:
        yield []

def tm_calibrate_instrument_1( state, s, i, rigid ):
    power_on = state.power_on
    pointing = state.pointing
    calibration_target = rigid[ "calibration_target" ]
    # i on and s pointing at calibration target of i
    d = pointing[ s ]
    if power_on[ i ] and calibration_target[ i ] == d:
        yield  [ ( "calibrate", s, i, d ) ]

def tm_calibrate_instrument_2( state, s, i, rigid ):
    power_on = state.power_on
    pointing = state.pointing
    calibration_target = rigid[ "calibration_target" ]
    # i on and s not pointing at calibration target of i
    d_prev = pointing[ s ]
    d_new = calibration_target[ i ]
    if power_on[ i ] and d_prev != d_new:
        yield [ ( "turn_to", s, d_new, d_prev ), ( "calibrate", s, i, d_new ) ]

methods.declare_task_methods( "t_calibrate_instrument", N*[ tm_calibrate_instrument ] )



"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""