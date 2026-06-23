#!/usr/bin/env python
"""
File Description: Racetrack example file. Run this file to solve the Rescue planning problem.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from __future__ import print_function
from examples.racetrack.task_based.methods import methods
from examples.racetrack.task_based.actions import actions
from examples.racetrack.search.sample_probs import rect20, rect50, rectwall32a, twisty0
from examples.racetrack.search.racetrack import main as search
from examples.racetrack.search.sample_heuristics import h_esdist
from ipyhop import IPyHOP, MonteCarloExecutor, planar_plot, State
from ipyhop.actor import Actor


# ******************************************        Helper Functions        ****************************************** #
def prob_to_state_and_task( prob ):
    init_state = State( 'init_state' )
    init_state.rigid = dict()
    init_state.rigid[ "walls" ] = tuple( [ tuple( x ) for x in prob[ 2: ][ 0 ] ] )
    loc = prob[0]
    init_state.loc = loc
    f_line = tuple( prob[ 1 ] )
    v = (0, 0)
    init_state.v = v
    task = ( "finish_at", f_line )
    return init_state, [ task ]
# ******************************************        Main Program Start      ****************************************** #
def main():
    # res = search(rect20, "bf", h_esdist )
    # print( res )
    init_state, task_list = prob_to_state_and_task( twisty0 )
    print(methods)
    print(actions)
    print(init_state)
    planner = IPyHOP(methods, actions)
    mc_executor = MonteCarloExecutor(actions)
    actor = Actor(planner, mc_executor)
    history = actor.complete_to_do(init_state, task_list, verbose=3)

# ******************************************        Main Program End        ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    try:
        main()
        print('\nFile executed successfully!\n')
    except KeyboardInterrupt:
        print('\nProcess interrupted by user. Bye!')

"""
Author(s): Yash Bansod
Repository: https://github.com/YashBansod/IPyHOP
Organization: University of Maryland at College Park
"""