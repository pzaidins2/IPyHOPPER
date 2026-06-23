#!/usr/bin/env python
"""
File Description: Rovers example file. Run this file to solve the Openstacks planning problem.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from examples.rovers.domain.actions import actions
from examples.rovers.domain.methods import methods
from examples.rovers.domain.deviations import deviation_handler
from ipyhop import IPyHOP, State
from ipyhop.mulitgoal import MultiGoal
from ipyhop.actor import Actor
from ipyhop.mc_executor import MonteCarloExecutor
import re
import os
from functools import partial


# ******************************************        Helper Functions        ****************************************** #

# create sat pyhop problem
def init_rovers( pddl_str, actions, methods ):
    # create intial state
    state_0 = State("state_0")
    # create multigoal
    goal_a = MultiGoal("goal_a")
    # define object types
    object_re = re.compile(r"(\w.+\w)\W*- (\w+)")
    rigid = dict()
    rigid[ "type_dict" ] = dict()
    type_dict = rigid[ "type_dict" ]
    object_re_matches = object_re.findall( pddl_str )
    for obj_list, obj_type in object_re_matches:
        type_dict[ obj_type.lower() ] = { *obj_list.split( " " ) }
    # uniary relations
    unary_re = re.compile(
        "(at_soil_sample|at_rock_sample|communicated_soil_data|communicated_rock_data|channel_free|available|empty|" +
        "equipped_for_soil_analysis|equipped_for_rock_analysis|equipped_for_imaging) (\w+)" )
    state_0.at_soil_sample = set()
    state_0.at_rock_sample = set()
    state_0.channel_free = set()
    state_0.available = set()
    state_0.empty = set()
    state_0.full = { *type_dict[ "store" ] }
    rigid[ "equipped_for_soil_analysis" ] = { r: False for r in type_dict[ "rover" ] }
    rigid[ "equipped_for_rock_analysis" ] = { r: False for r in type_dict[ "rover" ] }
    rigid[ "equipped_for_imaging" ] = { r: False for r in type_dict[ "rover" ] }
    goal_a.communicated_soil_data = dict()
    state_0.communicated_soil_data = dict()
    goal_a.communicated_rock_data = dict()
    state_0.communicated_rock_data = dict()
    unary_re_matches = unary_re.findall( pddl_str )
    for var, val in unary_re_matches:
        if var in { "at_soil_sample", "at_rock_sample", "channel_free", "available", "empty" }:
            getattr( state_0, var ).add( val )
            if var == "empty":
                state_0.full.remove( val )
        elif var in { "equipped_for_soil_analysis", "equipped_for_rock_analysis", "equipped_for_imaging" }:
            rigid[ var ][ val ] = True
        elif var in{ "communicated_soil_data", "communicated_rock_data" }:
            getattr( goal_a, var )[ val ] = True
            getattr( state_0, var )[ val ] = False
    # binary relations
    rigid[ "visible" ] = { wp: set() for wp in type_dict[ "waypoint" ] }
    rigid[ "at_lander" ] = dict()
    state_0.at = dict()
    rigid[ "store_of" ] = dict()
    rigid[ "has_store" ] = dict()
    rigid[ "on_board" ] = dict()
    rigid[ "carries" ] = { r: set() for r in type_dict[ "rover" ] }
    rigid[ "calibration_target" ] = dict()
    rigid[ "supports" ] = { i: set() for i in type_dict[ "camera" ] }
    state_0.visible_from = { o: set() for o in type_dict[ "objective" ] }
    state_0.communicated_image_data = dict()
    goal_a.communicated_image_data = dict()
    binary_re = re.compile( r"(visible|at_lander|at|store_of|on_board|calibration_target|supports|visible_from|" +
                            "communicated_image_data) (\w+) (\w+)" )
    binary_re_matches = binary_re.findall( pddl_str )
    for var, val_0, val_1 in binary_re_matches:
        if var in { "visible", "supports" }:
            rigid[ var ][ val_0 ].add( val_1 )
        elif var in { "at_lander", "store_of", "on_board", "calibration_target" }:
            rigid[ var ][ val_0 ] = val_1
            if var == "store_of":
                rigid[ "has_store" ][ val_1 ] = val_0
            elif var == "on_board":
                rigid[ "carries" ][ val_1 ].add( val_0 )
        elif var in { "at" }:
            getattr( state_0, var )[ val_0 ] = val_1
        elif var in { "visible_from" }:
            getattr( state_0, var )[ val_0 ].add( val_1 )
        elif var in { "communicated_image_data" }:
            getattr( goal_a, var )[ ( val_0, val_1 ) ] = True
            getattr( state_0, var )[ (val_0, val_1) ] = False
    # trinary relations
    rigid[ "can_traverse" ] = { r: set() for r in type_dict[ "rover" ] }
    trinary_re = re.compile( r"(can_traverse) (\w+) (\w+) (\w+)" )
    trinary_re_matches = trinary_re.findall( pddl_str )
    for var, val_0, val_1, val_2 in trinary_re_matches:
        if var in { "can_traverse" }:
            rigid[ var ][ val_0 ].add( ( val_1, val_2 ) )

    # set default values
    state_0.have_soil_analysis = { r: set() for r in type_dict[ "rover" ] }
    state_0.have_rock_analysis = { r: set() for r in type_dict[ "rover" ] }
    state_0.have_image = { r: set() for r in type_dict[ "rover" ] }
    state_0.calibrated = dict()
    for r in type_dict[ "rover" ]:
        for c in rigid[ "carries" ][ r ]:
            state_0.calibrated[ ( c, r ) ] = False

    # rigid never needs to be copied so avoid this by partial evaluation of actions, methods, and deviation_handler that take rigid
    methods.goal_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.goal_method_dict.items() } )
    methods.task_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.task_method_dict.items() } )
    methods.multigoal_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.multigoal_method_dict.items() } )
    actions.action_dict.update( { l: partial( a, rigid=rigid ) for l, a in actions.action_dict.items() } )

    return state_0, goal_a, rigid
# ******************************************        Main Program Start       ***************************************** #
def main():
    # while True:
        for problem_file_name in [ "problems/" + x for x in os.listdir( "problems" ) ]:
            if "pddl" not in problem_file_name:
                continue
            # print( problem_file_name )
            problem_file_name = "problems/p15.pddl"
            problem_file = open( problem_file_name, "r" )
            problem_str = problem_file.read()
            problem_file.close()

            planner = IPyHOP( methods, actions )
            state_0, goal_a, rigid= init_rovers( problem_str, actions, methods )
            print( state_0 )
            print( goal_a )
            mc_executor = MonteCarloExecutor( actions, deviation_handler( actions, planner, rigid ) )
            actor = Actor( planner, mc_executor )
            history = actor.complete_to_do( state_0, [ goal_a ], verbose=3 )
            if history is False:
                raise ValueError("FAILED PLANNING")

# ******************************************        Main Program End        ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    try:
        main()
        print('\nFile executed successfully!\n')
    except KeyboardInterrupt:
        print('\nProcess interrupted by user. Bye!')


"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""
