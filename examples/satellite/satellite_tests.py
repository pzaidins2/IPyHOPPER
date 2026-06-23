#!/usr/bin/env python
"""
File Description: Satellites testing file. Run this file to create Satellite test data.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from examples.satellite.domain.actions import actions
from examples.satellite.domain.methods import methods
from examples.satellite.domain.deviations import deviation_handler
from ipyhop import IPyHOP
from ipyhop.planner_old import IPyHOP_Old
from ipyhop.actor import Actor
from ipyhop.mc_executor import MonteCarloExecutor
import os
from examples.satellite.satellite_example import init_sat
import numpy as np
import time
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from scipy import stats


def run_experiment( i, j, k, problem_file_path ):
    problem_file = open( problem_file_path, "r" )
    problem_str = problem_file.read()
    problem_file.close()

    # init actor
    planner_type = [ IPyHOP, IPyHOP_Old ]
    planner_type = planner_type[ i ]
    planner = planner_type( methods, actions )
    state_0, goal_a, rigid = init_sat( problem_str, actions, methods)
    dev_hand = deviation_handler( actions, planner, rigid )
    mc_executor = MonteCarloExecutor( actions, dev_hand )
    actor = Actor( planner, mc_executor )

    # planning and acting
    try:
        start_time = time.process_time_ns()
        history = actor.complete_to_do( state_0, [ goal_a ] )
        time_elapsed = time.process_time_ns() - start_time
        # metrics
        iteration_count = planner.iterations
        cpu_time = time_elapsed - dev_hand.determine_deviation_time
        action_count = len( history )
        print( ( ( i, j, k ), ( iteration_count, cpu_time, action_count )  ) )
        return ( ( i, j, k ), ( iteration_count, cpu_time, action_count )  )
    except:
        print( "\nEXCEPTION OCCURRED: " + str( ( i, j, k ) ) + "\n" )
        return ( ( i, j, k ), ( -1, -1, -1 ) )
def main():
    # problem_file_names = filter( lambda x: "pddl" in x, os.listdir( "problems" ) )
    # problem_paths = [ "problems/" + x for x in problem_file_names ]
    # N = 1000
    # M = len( problem_paths )
    # P = 2
    # metrics = np.ndarray( ( P, N, M, 3 ) )
    #
    # print( metrics.shape )
    # args = []
    # for i in range( P ):
    #     for j in range( N ):
    #         for k in range( M ):
    #             args.append( ( i, j, k, problem_paths[ k ] ) )
    #
    # # with cProfile.Profile() as pr:
    # # for exp_set in args:
    # #     run_experiment( *exp_set )
    # #
    # # pr.print_stats()
    #
    # with Pool( processes=cpu_count() ) as pool:
    #     output = pool.starmap_async( run_experiment, args, chunksize=1 )
    #     while True:
    #         if output.ready():
    #             break
    #         print( str( round( 100 - 100 * output._number_left / len( args ), 3 ) ) + " %" )
    #         time.sleep( 60 )
    # for exp in output.get():
    #     metrics[ exp[ 0 ] ] = np.asarray( exp[1] )
    #
    # new_iteration_count = metrics[ 0, :, :, 0 ]
    # new_cpu_time = metrics[ 0, :, :, 1 ]
    # new_action_count = metrics[ 0, :, :, 2 ]
    # old_iteration_count = metrics[ 1, :, :, 0 ]
    # old_cpu_time = metrics[ 1, :, :, 1 ]
    # old_action_count = metrics[ 1, :, :, 2 ]
    #
    # # save to csv
    # np.savetxt( "new_satellite_iteration_count.csv", new_iteration_count, delimiter="," )
    # np.savetxt( "new_satellite_cpu_time.csv", new_cpu_time, delimiter="," )
    # np.savetxt( "new_satellite_action_count.csv", new_action_count, delimiter="," )
    # np.savetxt( "old_satellite_iteration_count.csv", old_iteration_count, delimiter="," )
    # np.savetxt( "old_satellite_cpu_time.csv", old_cpu_time, delimiter="," )
    # np.savetxt( "old_satellite_action_count.csv", old_action_count, delimiter="," )

    # load csv
    new_iteration_count = np.genfromtxt( "new_satellite_iteration_count.csv", delimiter="," )
    new_cpu_time = np.genfromtxt( "new_satellite_cpu_time.csv", delimiter="," )
    new_action_count = np.genfromtxt( "new_satellite_action_count.csv", delimiter="," )
    old_iteration_count = np.genfromtxt( "old_satellite_iteration_count.csv", delimiter="," )
    old_cpu_time = np.genfromtxt( "old_satellite_cpu_time.csv", delimiter="," )
    old_action_count = np.genfromtxt( "old_satellite_action_count.csv", delimiter="," )

    N, M = new_iteration_count.shape

    # ns to s
    new_cpu_time /= 1E9
    old_cpu_time /= 1E9

    # mean
    new_mean_iteration_count = np.mean( new_iteration_count, axis=0 )
    new_mean_cpu_time = np.mean( new_cpu_time, axis=0 )
    new_mean_action_count = np.mean( new_action_count, axis=0 )
    old_mean_iteration_count = np.mean( old_iteration_count, axis=0 )
    old_mean_cpu_time = np.mean( old_cpu_time, axis=0 )
    old_mean_action_count = np.mean( old_action_count, axis=0 )

    print( np.mean( (new_mean_cpu_time - old_mean_cpu_time) / old_mean_cpu_time ) )
    print( np.mean( (new_mean_iteration_count- old_mean_iteration_count ) / old_mean_iteration_count ) )
    # x = stats.ttest_ind( new_iteration_count, old_iteration_count, equal_var=False )
    # print( np.max( x.statistic ) )
    # print( np.mean( x.statistic ) )
    # print( np.max( x.pvalue ) )
    # print( np.mean( x.pvalue ) )
    # x = stats.ttest_ind( new_cpu_time, old_cpu_time, equal_var=False )
    # print( np.max( x.statistic ) )
    # print( np.mean( x.statistic ) )
    # print( np.max( x.pvalue ) )
    # print( np.mean( x.pvalue ) )
    # standard error
    new_err_iteration_count = np.std( new_iteration_count, axis=0 ) / np.sqrt( N )
    new_err_cpu_time = np.std( new_cpu_time, axis=0 ) / np.sqrt( N )
    new_err_action_count = np.std( new_action_count, axis=0 ) / np.sqrt( N )
    old_err_iteration_count = np.std( old_iteration_count, axis=0 ) / np.sqrt( N )
    old_err_cpu_time = np.std( old_cpu_time, axis=0 ) / np.sqrt( N )
    old_err_action_count = np.std( old_action_count, axis=0 ) / np.sqrt( N )

    x = np.asarray( [ i + 1 for i in range( M ) ] )
    x_range = x[ 0:M + 2:2 ]

    bar_width = 0.3
    position_offset = 1.2
    c_0 = "red"
    c_1 = "cyan"
    c_2 = "black"
    plt.figure( 0 )
    plt.rcParams.update( { 'font.size': 12 } )


    ax = plt.subplot( 3, 1, 2 )
    bp_0 = ax.boxplot( new_cpu_time, positions=x - position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_0, color=c_0 ),
                       capprops=dict( color=c_0 ),
                       whiskerprops=dict( color=c_0 ),
                       flierprops=dict( color=c_0, markeredgecolor=c_0, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    bp_1 = ax.boxplot( old_cpu_time, positions=x + position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_1, color=c_1 ),
                       capprops=dict( color=c_1 ),
                       whiskerprops=dict( color=c_1 ),
                       flierprops=dict( color=c_1, markeredgecolor=c_1, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    plt.ylabel( "CPU Time (s)" )
    # plt.yscale( "log" )
    ax.set_xticks( x_range )
    ax.set_yticks( range( 0, 4, 1 ) )

    ax = plt.subplot( 3, 1, 3 )
    bp_0 = ax.boxplot( new_action_count, positions=x - position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_0, color=c_0 ),
                       capprops=dict( color=c_0 ),
                       whiskerprops=dict( color=c_0 ),
                       flierprops=dict( color=c_0, markeredgecolor=c_0, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    bp_1 = ax.boxplot( old_action_count, positions=x + position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_1, color=c_1 ),
                       capprops=dict( color=c_1 ),
                       whiskerprops=dict( color=c_1 ),
                       flierprops=dict( color=c_1, markeredgecolor=c_1, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    plt.xlabel( "Problem #" )
    plt.ylabel( "Action Count" )
    ax.set_xticks( x_range )
    ax.set_yticks( range( 0, 300, 50 ) )

    ax = plt.subplot( 3, 1, 1 )
    bp_0 = ax.boxplot( new_iteration_count, positions=x - position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_0, color=c_0 ),
                       capprops=dict( color=c_0 ),
                       whiskerprops=dict( color=c_0 ),
                       flierprops=dict( color=c_0, markeredgecolor=c_0, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    bp_1 = ax.boxplot( old_iteration_count, positions=x + position_offset * bar_width / 2, widths=bar_width,
                       notch=True, labels=2 * x - 1, patch_artist=True,
                       boxprops=dict( facecolor=c_1, color=c_1 ),
                       capprops=dict( color=c_1 ),
                       whiskerprops=dict( color=c_1 ),
                       flierprops=dict( color=c_1, markeredgecolor=c_1, marker="." ),
                       medianprops=dict( color=c_2 ),
                       )
    plt.ylabel( "Iteration Count" )
    # plt.yscale( "log" )
    ax.set_xticks( x_range )
    ax.set_yticks( range( 0, 10000, 2000 ) )
    ax.legend( [ bp_0[ "boxes" ][ 0 ], bp_1[ "boxes" ][ 0 ] ], [ "IPyHOPPER", "Lazy-Refineahead" ] )
    title = "Satellites Domain"
    plt.title( title )
    plt.savefig( title + ".png", bbox_inches='tight', dpi=1000 )
    plt.show()

    # plt.figure( 1 )
    # plt.bar( x, (new_mean_cpu_time - old_mean_cpu_time) / old_mean_cpu_time,
    #          yerr=np.sqrt( np.power( new_err_cpu_time / new_mean_cpu_time, 2 ) +
    #                        np.power( old_err_cpu_time / old_mean_cpu_time, 2 ) ) )
    # plt.show()

    # plt.figure(2)
    # ax = plt.subplot( 3, 1, 1 )
    # title = "Rovers Domain"
    # plt.title( title )
    # plt.bar( x, new_mean_iteration_count, yerr=new_err_iteration_count, width=bar_width, label="new", color=c_0 )
    # plt.bar( x + bar_width, old_mean_iteration_count, yerr=old_err_iteration_count, width=bar_width, label="old",
    #          color=c_1 )
    # # plt.xlabel( "Problem #" )
    # plt.ylabel( "Iteration Count" )
    # # plt.yscale( "log" )
    # ax.set_xticks( x )
    #
    # ax = plt.subplot( 3, 1, 2 )
    # plt.bar( x, new_mean_cpu_time, yerr=new_err_cpu_time, width=bar_width, label="new", color=c_0 )
    # plt.bar( x + bar_width, old_mean_cpu_time, yerr=old_err_cpu_time, width=bar_width, label="old", color=c_1 )
    # # plt.xlabel( "Problem #" )
    # plt.ylabel( "CPU Time (s)" )
    # # plt.yscale( "log" )
    # ax.set_xticks( x )
    #
    # ax = plt.subplot( 3, 1, 3 )
    # plt.bar( x, new_mean_action_count, yerr=new_err_action_count, width=bar_width, label="new", color=c_0 )
    # plt.bar( x + bar_width, old_mean_action_count, yerr=old_err_action_count, width=bar_width, label="old", color=c_1 )
    # plt.xlabel( "Problem #" )
    # plt.ylabel( "Action Count" )
    # ax.set_xticks( x )
    # plt.legend()
    # # plt.savefig( title + ".png")
    # plt.show()
    #
    # plt.figure( 3 )
    # plt.plot( x, ((new_mean_cpu_time - old_mean_cpu_time) / old_mean_cpu_time) )
    # plt.plot( x, ((new_mean_iteration_count - old_mean_iteration_count) / old_mean_iteration_count) )
    # plt.plot( x, ((new_mean_action_count - old_mean_action_count) / old_mean_action_count) )
    # plt.legend(["CPU Time","Iteration Count", "Action Count"])
    # plt.show()

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