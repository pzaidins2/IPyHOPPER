#!/usr/bin/env python
"""
File Description: Rovers deviations file. All the deviations for Rovers planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/rovers/deviation-operators.lisp

"""

from typing import List, Dict, Set
from examples.satellite.domain.actions import type_check
import random
from functools import partial
from itertools import product
from examples.openstacks.domain.deviations import shopfixer_deviation_handler
from copy import deepcopy

# rovers deviation handler
class deviation_handler( shopfixer_deviation_handler ):

    def __init__( self, actions, planner, rigid ):
        super().__init__( actions, planner, rigid )
        self.deviation_operators = [
            d_lost_soil_analysis,
            d_lost_rock_analysis,
            d_lost_image,
            d_decalibration,
            d_cannot_see_to_calibrate,
            d_cannot_see_to_take_image
        ]
        self.deviation_operators = [ partial( d_operator, rigid=self.rigid ) for d_operator in
                                     self.deviation_operators ]

def d_lost_soil_analysis( act_tuple, state, rigid ):
    soil_analysis = [ *state.have_soil_analysis.items() ]
    random.shuffle( soil_analysis )
    have_soil_analysis = state.have_soil_analysis
    communicated_soil_data = state.communicated_soil_data
    # lose random soil sample
    for r, wp_set in soil_analysis:
        wp_list = [ *wp_set ]
        # random.shuffle( wp_list )
        for wp in wp_list:
            if not( communicated_soil_data[ wp ] ) and wp in have_soil_analysis[ r ]:
                new_state = state.copy()
                new_state.have_soil_analysis[ r ].remove( wp )
                new_state.at_soil_sample.add( wp )
                yield new_state

def d_lost_rock_analysis( act_tuple, state, rigid ):
    rock_analysis = [ *state.have_rock_analysis.items() ]
    random.shuffle( rock_analysis )
    have_rock_analysis = state.have_rock_analysis
    communicated_rock_data = state.communicated_rock_data
    # lose random rock sample
    for r, wp_set in rock_analysis:
        wp_list = [ *wp_set ]
        # random.shuffle( wp_list )
        for wp in wp_list:
            if not( communicated_rock_data[ wp ] ) and wp in have_rock_analysis[ r ]:
                new_state = state.copy()
                new_state.have_rock_analysis[ r ].remove( wp )
                new_state.at_rock_sample.add( wp )
                yield new_state

def d_lost_image( act_tuple, state, rigid ):
    type_dict = rigid[ "type_dict"]
    rovers = type_dict[ "rover" ]
    objectives = type_dict[ "objective" ]
    modes = type_dict[ "mode" ]
    cameras = type_dict[ "camera" ]
    have_image = state.have_image
    on_board = rigid[ "on_board" ]
    communicated_image_data = state.communicated_image_data
    rovers_list = [ *rovers ]
    # random.shuffle( rovers_list )
    objectives_list = [ *objectives ]
    # random.shuffle( objectives_list )
    modes_list = [ *modes ]
    # random.shuffle( modes_list )
    cameras_list = [ *cameras ]
    # random.shuffle( cameras_list )

    quad_tuples = product( rovers_list, objectives_list, modes_list, cameras_list )
    # lose random image
    for r, o, m, i in quad_tuples:
        image = ( o, m )
        if on_board[ i ] == r and image in have_image[ r ] and not communicated_image_data[ image ]:
            new_state = state.copy()
            new_state.have_image[ r ].remove( image )
            new_state.calibrated[ ( i, r ) ] = False
            yield new_state

def d_decalibration( act_tuple, state, rigid ):
    calibrated = state.calibrated
    # decalibrate randomly
    calibrated_pairs = [ *filter( lambda x: calibrated[ x ], calibrated.keys() ) ]
    for calibrated_pair in calibrated_pairs:
        # calibrated_pair = random.choice( calibrated_pairs )
        new_state = state.copy()
        new_state.calibrated[ calibrated_pair ] = False
        yield new_state

def d_cannot_see_to_calibrate( act_tuple, state, rigid ):
    act_name =  act_tuple[ 0 ]
    act_args = act_tuple[ 1: ]
    type_dict = rigid[ "type_dict" ]
    rovers = type_dict[ "rover" ]
    modes = type_dict[ "mode" ]
    visible_from = state.visible_from
    on_board = rigid[ "on_board" ]
    calibration_target = rigid[ "calibration_target" ]
    calibrated = state.calibrated
    have_image = state.have_image
    at = state.at
    # complications arise from KB abuse translation
    # this condition is an approximation of searching KB for current goal
    # (communicate_image_data ?target ?m)
    if act_name == "calibrate":
        r, i, o, w = act_args
        visible_from_o = visible_from[ o ]
        at_r = at[ r ]
        calibration_target_i = calibration_target[ i ]
        # simple validity checks (may be unneeded)
        if at_r == w and on_board[ i ] == r and calibration_target_i == o and not( calibrated[ ( i, r ) ]) and \
            w in visible_from_o:
            # avoid making objective unreachable
            if len( visible_from_o ) > 1:
                # no rover has image
                # overly conservative because mode unspecified
                r_i_m = product( rovers, { o }, modes )
                have_image_check = map( lambda x: ( x[ 1 ], x[ 2 ] ) in have_image[ x[ 0 ] ], r_i_m )
                if not any( have_image_check ):
                    new_state = state.copy()
                    new_state.visible_from[ o ].remove( w )
                    yield new_state

def d_cannot_see_to_take_image( act_tuple, state, rigid ):
    act_name =  act_tuple[ 0 ]
    act_args = act_tuple[ 1: ]
    type_dict = rigid[ "type_dict" ]
    rovers = type_dict[ "rover" ]
    modes = type_dict[ "mode" ]
    visible_from = state.visible_from
    on_board = rigid[ "on_board" ]
    calibration_target = rigid[ "calibration_target" ]
    equipped_for_imaging = rigid[ "equipped_for_imaging" ]
    calibrated = state.calibrated
    have_image = state.have_image
    at = state.at
    # complications arise from KB abuse translation
    # this condition is an approximation of searching KB for current goal
    # (communicate_image_data ?target ?m)
    if act_name == "take_image":
        r, w, o, i, m = act_args
        visible_from_o = visible_from[ o ]
        at_r = at[ r ]
        image = ( o, m )
        # simple validity checks (may be unneeded)
        if equipped_for_imaging[ r ] and at_r == w and on_board[ i ] == r and calibrated[ ( i, r ) ] and \
            w in visible_from_o and image not in have_image[ r ]:
            # avoid making objective unreachable
            if len( visible_from_o ) > 1:
                new_state = state.copy()
                new_state.visible_from[ o ].remove( w )
                yield new_state


# ******************************************    Helper Functions            ****************************************** #

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Satellites Deviations isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""