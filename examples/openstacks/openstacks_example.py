#!/usr/bin/env python
"""
File Description: Openstacks World example file. Run this file to solve the Openstacks planning problem.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from examples.openstacks.domain.actions import actions
from examples.openstacks.domain.methods import methods
from examples.openstacks.domain.deviations import deviation_handler
from ipyhop import IPyHOP, State
from ipyhop.mulitgoal import MultiGoal
from ipyhop.actor import Actor
from ipyhop.mc_executor import MonteCarloExecutor
import re
from functools import partial
import os

# ******************************************        Helper Functions        ****************************************** #

# create sat pyhop problem
def init_openstacks( pddl_str, actions, methods ):
    # create intial state
    state_0 = State("state_0")
    # create multigoal
    goal_a = MultiGoal("goal_a")
    # define object types
    object_re = re.compile(r"(\w.+\w)\W*- (\w+)")
    rigid = dict()
    rigid[ "type_dict" ] = dict()
    type_dict = rigid[ "type_dict" ]
    rigid[ "max_stacks" ] = 0
    object_re_matches = object_re.findall( pddl_str )
    for obj_list, obj_type in object_re_matches:
        type_dict[ obj_type ] = { *obj_list.split( " " ) }
        if obj_type == "count":
            rigid[ "max_stacks" ] = len( type_dict[ obj_type ] ) - 1
    # uniary relations
    unary_re = re.compile( r"(waiting|shipped) (\w+)" )
    state_0.waiting = dict()
    goal_a.shipped = dict()
    unary_re_matches = unary_re.findall( pddl_str )
    for var, val in unary_re_matches:
        if var in { "waiting" }:
            getattr( state_0, var )[ val ] = True
        elif var in{ "shipped" }:
            getattr( goal_a, var )[ val ] = True
    # binary relations
    binary_re = re.compile( r"(includes) (\w+) (\w+)" )
    binary_re_matches = binary_re.findall( pddl_str )
    rigid[ "includes"] = { x: set() for x in type_dict[ "order" ] }
    rigid[ "included_in" ] = { x: set() for x in type_dict[ "product" ] }
    for var, val_0, val_1 in binary_re_matches:
        if var == "includes":
            rigid[ "includes" ][ val_0 ].add( val_1 )
            rigid[ "included_in" ][ val_1 ].add( val_0 )
    # set to default values
    state_0.made = dict()
    state_0.busy = False
    state_0.making = dict()
    state_0.started = dict()
    # state_0.delivered = dict()
    state_0.stacks_open = 0
    state_0.shipped = dict()
    for p in type_dict[ "product" ]:
        for rel in [ "made", "making" ]:
            getattr( state_0, rel )[ p ] = False
    for o in type_dict[ "order" ]:
        for rel in [ "started", "shipped" ]:
            getattr( state_0, rel )[ o ] = False
    # for o, p in product( type_dict[ "order" ], type_dict[ "product" ] ):
    #     getattr( state_0, "delivered" )[ ( o, p ) ] = False

    # rigid never needs to be copied so avoid this by partial evaluation of actions, methods, and deviation_handler that take rigid
    methods.goal_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.goal_method_dict.items() } )
    methods.task_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.task_method_dict.items() } )
    methods.multigoal_method_dict.update(
        { l: [ partial( m, rigid=rigid ) for m in ms ] for l, ms in methods.multigoal_method_dict.items() } )
    actions.action_dict.update( { l: partial( a, rigid=rigid ) for l, a in actions.action_dict.items() } )

    goal_a.goal_tag = "mg_plan"
    return state_0, goal_a, rigid
# ******************************************        Main Program Start       ***************************************** #
def main():
    # while True:
        for problem_file_name in [ "problems/" + x for x in os.listdir( "problems" ) ]:
            if "pddl" not in problem_file_name:
                continue
            print( problem_file_name )
            # problem_file_name = "problems/p10.pddl"
            problem_file = open( problem_file_name, "r" )
            problem_str = problem_file.read()
            problem_file.close()

            planner = IPyHOP( methods, actions )
            planner.branch_cycle_check_flag = False
            state_0, goal_a, rigid = init_openstacks( problem_str, actions, methods )
            mc_executor = MonteCarloExecutor( actions, deviation_handler( actions, planner, rigid ) )
            actor = Actor( planner, mc_executor )
            history = actor.complete_to_do( state_0, [ goal_a ],verbose=3 )
            if history is False:
                raise(ValueError("history should never be False for example"))
            # print( history )


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
