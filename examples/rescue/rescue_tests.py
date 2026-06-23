#!/usr/bin/env python
"""
File Description: rescues testing file. Run this file to create rescue test data.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from examples.rescue.domain.rescue_actions import actions
from examples.rescue.domain.rescue_methods import methods
from examples.rescue.problem.rescue_prob_gen import StateSampler
from ipyhop import IPyHOP
from ipyhop.planner_old import IPyHOP_Old
from ipyhop.actor import Actor
from ipyhop.mc_executor import MonteCarloExecutor
import numpy as np
import time
import matplotlib.pyplot as plt


def run_experiment( i, j, k ):

    # init actor
    planner_type = [ IPyHOP, IPyHOP_Old ]
    planner_type = planner_type[ i ]
    planner = planner_type( methods, actions )
    state_sampler = StateSampler( seed_val=j )
    state_0, goal_a = state_sampler.sample( actions, methods, state_name="state_0" )
    mc_executor = MonteCarloExecutor( actions, seed=k )
    actor = Actor( planner, mc_executor )

    # planning and acting
    try:
        start_time = time.process_time()
        history = actor.complete_to_do( state_0, goal_a )
        time_elapsed = time.process_time() - start_time
        # metrics
        iteration_count = planner.iterations
        cpu_time = time_elapsed
        action_count = len( history )
        action_cost = 0
        for act in history:
            action_cost += actions.action_cost[ act[ 0 ] ]
        node_expansions = planner.node_expansions
        print( ((i, j, k), (action_cost, action_count, cpu_time, iteration_count, node_expansions)) )
        return ((i, j, k), (action_cost, action_count, cpu_time, iteration_count, node_expansions))
    except:
        print( "\nEXCEPTION OCCURRED: " + str( (i, j, k) ) + "\n" )
        return ((i, j, k), (-1, -1, -1, -1, -1))

if __name__ == '__main__':
    plt.rcParams.update( { 'font.size': 15 } )
    # N = 10000
    # P = 2
    # M = 100
    # metrics = np.ndarray( ( P, N, M, 5 ) )
    #
    # print( metrics.shape )
    # args = []
    # for i in range( P ):
    #     for j in range( N ):
    #         for k in range( M ):
    #             args.append( ( i, j, k ) )
    #
    # # with cProfile.Profile() as pr:
    # # for exp_set in args:
    # #     ( i, j, k ), ( action_count, cpu_time, iteration_count ) = run_experiment( *exp_set )
    # #     if action_count > 1000 or iteration_count > 1000:
    # #         break
    #
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
    # new_rescue_action_cost = metrics[ 0, :, :, 0 ]
    # new_rescue_action_count = metrics[ 0, :, :, 1 ]
    # new_rescue_cpu_time = metrics[ 0, :, :, 2 ]
    # new_rescue_iteration_count = metrics[ 0, :, :, 3 ]
    # new_rescue_node_expansions = metrics[ 0, :, :, 4 ]
    # old_rescue_action_cost = metrics[ 1, :, :, 0 ]
    # old_rescue_action_count = metrics[ 1, :, :, 1 ]
    # old_rescue_cpu_time = metrics[ 1, :, :, 2 ]
    # old_rescue_iteration_count = metrics[ 1, :, :, 3 ]
    # old_rescue_node_expansions = metrics[ 1, :, :, 4 ]
    #
    # # save to csv
    # np.savetxt( "new_rescue_action_cost.csv", new_rescue_action_cost, delimiter="," )
    # np.savetxt( "new_rescue_action_count.csv", new_rescue_action_count, delimiter="," )
    # np.savetxt( "new_rescue_cpu_time.csv", new_rescue_cpu_time, delimiter="," )
    # np.savetxt( "new_rescue_iteration_count.csv", new_rescue_iteration_count, delimiter="," )
    # np.savetxt( "new_rescue_node_expansions.csv", new_rescue_node_expansions, delimiter="," )
    # np.savetxt( "old_rescue_action_cost.csv", old_rescue_action_cost, delimiter="," )
    # np.savetxt( "old_rescue_action_count.csv", old_rescue_action_count, delimiter="," )
    # np.savetxt( "old_rescue_cpu_time.csv", old_rescue_cpu_time, delimiter="," )
    # np.savetxt( "old_rescue_iteration_count.csv", old_rescue_iteration_count, delimiter="," )
    # np.savetxt( "old_rescue_node_expansions.csv", old_rescue_node_expansions, delimiter="," )

    # load csv
    new_rescue_action_cost = np.genfromtxt( "data/new_rescue_action_cost.csv", delimiter="," )
    new_rescue_action_count = np.genfromtxt( "data/new_rescue_action_count.csv", delimiter="," )
    new_rescue_cpu_time = np.genfromtxt( "data/new_rescue_cpu_time.csv", delimiter="," )
    new_rescue_iteration_count = np.genfromtxt( "data/new_rescue_iteration_count.csv", delimiter="," )
    new_rescue_node_expansions = np.genfromtxt( "data/new_rescue_node_expansions.csv", delimiter="," )
    old_rescue_action_cost = np.genfromtxt( "data/old_rescue_action_cost.csv", delimiter="," )
    old_rescue_action_count = np.genfromtxt( "data/old_rescue_action_count.csv", delimiter="," )
    old_rescue_cpu_time = np.genfromtxt( "data/old_rescue_cpu_time.csv", delimiter="," )
    old_rescue_iteration_count = np.genfromtxt( "data/old_rescue_iteration_count.csv", delimiter="," )
    old_rescue_node_expansions = np.genfromtxt( "data/old_rescue_node_expansions.csv", delimiter="," )

    P = 2
    N, M = new_rescue_action_count.shape

    # fail logical masks
    fail_mask = np.zeros( ( N, M ) )

    # True is fail and False is goal achieved
    new_fail = new_rescue_action_count < fail_mask
    old_fail = old_rescue_action_count < fail_mask

    # Problem fail rate
    new_fail_rate = np.mean( new_fail, axis=1 )
    old_fail_rate = np.mean( old_fail, axis=1 )

    # different failures
    fail_diff = new_fail_rate - old_fail_rate
    print( np.mean( new_fail_rate ) )
    print( np.mean( old_fail_rate ) )
    print( np.mean( fail_diff ) )
    print( np.mean( (new_fail_rate > 0) & (old_fail_rate == 0) ) )
    print( np.mean( (new_fail_rate == 0) & (old_fail_rate > 0) ) )
    print( np.mean( (new_fail_rate != 0) & (new_fail_rate != 1) ) )
    print( np.mean( (old_fail_rate != 0) & (old_fail_rate != 1) ) )
    print( old_fail_rate[ (old_fail_rate != 0) & (old_fail_rate != 1) ] )
    print("\n")

    # filter out failed problems
    # neither had failures
    shared_pass = np.logical_not( np.logical_or( new_fail_rate > 0, old_fail_rate > 0 ) )
    new_rescue_action_cost = new_rescue_action_cost[ shared_pass ]
    new_rescue_action_count = new_rescue_action_count[ shared_pass ]
    new_rescue_cpu_time = new_rescue_cpu_time[ shared_pass ]
    new_rescue_iteration_count = new_rescue_iteration_count[ shared_pass ]
    new_rescue_node_expansions = new_rescue_node_expansions[ shared_pass ]
    old_rescue_action_cost = old_rescue_action_cost[ shared_pass ]
    old_rescue_action_count = old_rescue_action_count[ shared_pass ]
    old_rescue_cpu_time = old_rescue_cpu_time[ shared_pass ]
    old_rescue_iteration_count = old_rescue_iteration_count[ shared_pass ]
    old_rescue_node_expansions = old_rescue_node_expansions[ shared_pass ]

    print( np.mean( ( np.mean( new_rescue_action_cost, axis=1 ) - np.mean( old_rescue_action_cost, axis=1 ) ) / np.mean( old_rescue_action_cost, axis=1 ) ) )
    print( 2 * np.std( (np.mean( new_rescue_action_cost, axis=1 ) - np.mean( old_rescue_action_cost, axis=1 )) / np.mean(
        old_rescue_action_cost, axis=1 ) ) / np.sqrt( N ) )
    print( np.mean( ( np.mean( new_rescue_node_expansions, axis=1 ) - np.mean( old_rescue_node_expansions, axis=1 ) ) / np.mean( old_rescue_node_expansions, axis=1 ) ) )
    print( 2 * np.std(
        (np.mean( new_rescue_node_expansions, axis=1 ) - np.mean( old_rescue_node_expansions, axis=1 )) / np.mean(
            old_rescue_node_expansions, axis=1 ) ) / np.sqrt( N ) )
    print( np.mean(
        (np.mean( new_rescue_cpu_time, axis=1 ) - np.mean( old_rescue_cpu_time, axis=1 )) / np.mean(
            old_rescue_cpu_time, axis=1 ) ) )

    P = 2
    N, M = new_rescue_iteration_count.shape

    plt.scatter( np.mean( old_rescue_action_cost, axis=1 ), np.mean( new_rescue_action_cost, axis=1 ), marker="x" )
    x = np.asarray( [ min( np.min( np.mean( old_rescue_action_cost, axis=1 ) ),
                           np.min( np.mean( new_rescue_action_cost, axis=1 ) ) ),
                      max( np.max( np.mean( old_rescue_action_cost, axis=1 ) ),
                           np.max( np.mean( new_rescue_action_cost, axis=1 ) ) ) ] )
    plt.plot( x, x, color="black", linestyle="dashed" )
    plt.gca().set_aspect( 'equal', adjustable='box' )
    plt.xlabel( "Mean Lazy-Refineahead Action Cost" )
    plt.ylabel( "Mean IPyHOPPER Action Cost" )
    plt.title( "Rescue Domain" )
    plt.savefig( "rescue_action_cost.png", bbox_inches='tight', dpi=1000 )
    plt.show()


    # plt.scatter( np.mean( old_rescue_action_count, axis=1 ), np.mean( new_rescue_action_count, axis=1 ) )
    # x = np.asarray( [ min( np.min( np.mean( old_rescue_action_count, axis=1 ) ),
    #                        np.min( np.mean( new_rescue_action_count, axis=1 ) ) ),
    #                   max( np.max( np.mean( old_rescue_action_count, axis=1 ) ),
    #                        np.max( np.mean( new_rescue_action_count, axis=1 ) ) ) ] )
    # plt.plot( x, x, color="black", linestyle="dashed" )
    # plt.gca().set_aspect( 'equal', adjustable='box' )
    # plt.xlabel( "Mean Old Action Count" )
    # plt.ylabel( "Mean New Action Count" )
    # plt.title( "Rescue Domain" )
    # plt.show()

    # plt.scatter( np.mean( old_rescue_cpu_time, axis=1 ), np.mean( new_rescue_cpu_time, axis=1 ) )
    # x = np.asarray( [ min( np.min( np.mean( old_rescue_cpu_time, axis=1 ) ),
    #                        np.min( np.mean( new_rescue_cpu_time, axis=1 ) ) ),
    #                   max( np.max( np.mean( old_rescue_cpu_time, axis=1 ) ),
    #                        np.max( np.mean( new_rescue_cpu_time, axis=1 ) ) ) ] )
    # plt.plot( x, x, color="black", linestyle="dashed" )
    # plt.gca().set_aspect( 'equal', adjustable='box' )
    # plt.xlabel( "Mean Old CPU Time (s)" )
    # plt.ylabel( "Mean New CPU Time (s)" )
    # plt.title( "Rescue Domain" )
    # plt.show()
    #
    # plt.scatter( np.mean( old_rescue_iteration_count, axis=1 ), np.mean( new_rescue_iteration_count, axis=1 ) )
    # x = np.asarray( [ min( np.min( np.mean( old_rescue_iteration_count, axis=1 ) ),
    #                        np.min( np.mean( new_rescue_iteration_count, axis=1 ) ) ),
    #                   max( np.max( np.mean( old_rescue_iteration_count, axis=1 ) ),
    #                        np.max( np.mean( new_rescue_iteration_count, axis=1 ) ) ) ] )
    # plt.plot( x, x, color="black", linestyle="dashed" )
    # plt.gca().set_aspect( 'equal', adjustable='box' )
    # plt.xlabel( "Mean Old Iteration Count" )
    # plt.ylabel( "Mean New Iteration Count" )
    # plt.title( "Rescue Domain" )
    # plt.show()

    plt.scatter( np.mean( old_rescue_node_expansions, axis=1 ), np.mean( new_rescue_node_expansions, axis=1 ), marker="x" )
    x = np.asarray( [ min( np.min( np.mean( old_rescue_node_expansions, axis=1 ) ),
                           np.min( np.mean( new_rescue_node_expansions, axis=1 ) ) ),
                      max( np.max( np.mean( old_rescue_node_expansions, axis=1 ) ),
                           np.max( np.mean( new_rescue_node_expansions, axis=1 ) ) ) ] )
    plt.plot( x, x, color="black", linestyle="dashed" )
    plt.gca().set_aspect( 'equal', adjustable='box' )
    plt.xlabel( "Mean Lazy-Refineahead Node Expansions" )
    plt.ylabel( "Mean IPyHOPPER Node Expansions" )
    plt.title( "Rescue Domain" )
    plt.savefig( "rescue_node_expansions.png", bbox_inches='tight', dpi=1000)
    plt.show()



"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""