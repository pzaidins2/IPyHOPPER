#!/usr/bin/env python
"""
File Description: data analysis and plotting
"""

import numpy as np
import os
import re
import matplotlib.pyplot as plt
import itertools

if __name__ == '__main__':
    # error rates tested
    error_rates = [ *range( 0, 90, 10 ) ]
    E = len( error_rates )
    # planner types used
    planner_types = [ "old", "new" ]
    P = len( planner_types )
    # metrics recorded
    metrics = [ "action_count", "cpu_time", "iteration_count" ]
    M = len( metrics )
    # number of tests per setting
    N = 1000
    # number of distinct problems
    Qs = [ 30, 20, 20 ]

    # domains
    domains = [ "openstacks", "rovers", "satellite" ]

    # list of data tensor
    results = [ -1 * np.ones( ( E, P, M, N, Q ) ) for Q in Qs ]

    # read in data


    coord_re = re.compile( r"([a-z]+)_([a-z]+)_([\w]+)\.csv" )

    for i in range( len( domains ) ):
        domain = domains[ i ]
        data_dir = domain + "/data"
        for error_dir in os.listdir( data_dir ):
            for file_name in os.listdir( data_dir + "/" + error_dir ):
                if ".csv" in file_name:
                    file_path = data_dir + "/" + error_dir + "/" + file_name
                    planner_type, _, metric = coord_re.search( file_name ).group( 1, 2, 3 )
                    coord = (
                        error_rates.index( int( error_dir ) ),
                        planner_types.index( planner_type ),
                        metrics.index( metric )
                    )
                    results[ i ][ coord ] = np.genfromtxt( file_path, delimiter="," )

    # plt.figure( 0 )
    # plt.title( "Old Replanning CPU Time vs Action Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 0, 0, :, q ], axis=(1) ) , np.mean( results[ :, 0, 1, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel("Action Count")
    # plt.ylabel("CPU Time (s)")
    # # plt.savefig( "old_cpu_action.png" )
    # plt.show()
    # plt.figure( 1 )
    # plt.title( "New Replanning CPU Time vs Action Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 1, 0, :, q ], axis=(1) ), np.mean( results[ :, 1, 1, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel( "Action Count" )
    # plt.ylabel( "CPU Time (s)" )
    # # plt.savefig( "new_cpu_action.png" )
    # plt.show()
    #
    # plt.figure( 2 )
    # plt.title( "Old Replanning CPU Time vs Iteration Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 0, 2, :, q ], axis=(1) ), np.mean( results[ :, 0, 1, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel( "Iteration Count" )
    # plt.ylabel( "CPU Time (s)" )
    # # plt.savefig( "old_cpu_action.png" )
    # plt.show()
    # plt.figure( 3 )
    # plt.title( "New Replanning CPU Time vs Iteration Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 1, 2, :, q ], axis=(1) ), np.mean( results[ :, 1, 1, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel( "Iteration Count" )
    # plt.ylabel( "CPU Time (s)" )
    # # plt.savefig( "new_cpu_action.png" )
    # plt.show()
    #
    # plt.figure( 4 )
    # plt.title( "Old Replanning Iteration Count vs Action Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 0, 0, :, q ], axis=(1) ), np.mean( results[ :, 0, 2, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel( "Action Count" )
    # plt.ylabel( "Iteration Count" )
    # # plt.savefig( "old_cpu_action.png" )
    # plt.show()
    # plt.figure( 5 )
    # plt.title( "New Replanning Iteration Count vs Action Count" )
    # for q in range( Q ):
    #     plt.scatter( np.mean( results[ :, 1, 0, :, q ], axis=(1) ), np.mean( results[ :, 1, 2, :, q ], axis=(1) ) )
    # plt.legend( Qs )
    # plt.xlabel( "Action Count" )
    # plt.ylabel( "Iteration Count" )
    # # plt.savefig( "new_cpu_action.png" )
    # plt.show()

    # normalize results by problem
    normalized_results = 3 * [ 0 ]

    # # linear
    # for i in range( len( domains ) ):
    #     r = results[ i ]
    #     r_max = np.max( r, axis = ( 0, 1, 3 ) )[ np.newaxis, np.newaxis, :, np.newaxis, : ]
    #     r_min = np.min( r, axis = ( 0, 1, 3 ) )[ np.newaxis, np.newaxis, :, np.newaxis, : ]
    #     normalized_results[ i ] = ( r - r_min ) / ( r_max - r_min + 1E-10 )

    # # z-score
    # for i in range( len( domains ) ):
    #     r = results[ i ]
    #     r_mean = np.mean( r, axis = ( 0, 1, 3 ) )[ np.newaxis, np.newaxis, :, np.newaxis, : ]
    #     r_std = np.std( r, axis = ( 0, 1, 3 ) )[ np.newaxis, np.newaxis, :, np.newaxis, : ]
    #     normalized_results[ i ] = ( r - r_mean ) / ( r_std + 1E-10 )

    # z-score (only dist of original)
    for i in range( len( domains ) ):
        r = results[ i ]
        print(r.shape)
        r_mean = np.mean( r, axis=(0, 3) )[ np.newaxis, 0, :, np.newaxis, : ]
        print(r_mean.shape)
        r_std = np.std( r, axis=(0, 3) )[ np.newaxis, 0, :, np.newaxis, : ]
        normalized_results[ i ] = (r - r_mean) / (r_std + 1E-10)

    # # log
    # for i in range( len( domains ) ):
    #     r = results[ i ]
    #     normalized_results[ i ] = np.log( r + 1E-10 )

    plt.figure( 6 )
    plt.subplot( 3, 1, 1 )
    plt.title( "New Replanning Z-Score Scaled Change vs Error Rate" )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 0, :, : ], axis=( 1, 2 ) )
                     - np.mean( normalized_results[ i ][ :, 0, 0, :, : ], axis=( 1, 2 ) ),
                     )
    plt.legend( domains )
    plt.ylabel( "Normalized Action Count" )
    plt.grid()
    plt.subplot( 3, 1, 2 )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 1, :, : ], axis=( 1, 2 ) )
                     - np.mean( normalized_results[ i ][ :, 0, 1, :, : ], axis=( 1, 2 ) ),
                     )
    plt.ylabel( "Normalized CPU Time (s/s)" )
    plt.grid()
    plt.subplot( 3, 1, 3 )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 2, :, : ], axis=(1, 2) )
                     - np.mean( normalized_results[ i ][ :, 0, 2, :, : ], axis=(1, 2) ),
                     )
    plt.ylabel( "Normalized Iteration Count" )
    plt.xlabel( "Error Rates (%)")
    plt.grid()
    plt.show()

    # plt.figure( 7 )
    # index = 2
    # plt.subplot( 3, 1, 1 )
    # plt.title( "New Replanning Difference: " + domains[ index ] )
    # mean_diff = np.mean( normalized_results[ index ][ :, 1, :, :, : ], axis=( 2 ) ) \
    #                  - np.mean( normalized_results[ index ][ :, 0, :, :, : ], axis=( 2 ) )
    # mean_std = np.std( normalized_results[ index ][ :, 1, :, :, : ], axis=(2) ) \
    #             + np.std( normalized_results[ index ][ :, 0, :, :, : ], axis=(2) )
    # for i in range( Qs[ index ] ):
    #     plt.plot( error_rates, mean_diff[ :, 0, i ] )
    # plt.ylabel( "Normalized Action Count" )
    # plt.legend( [ *range( 1, Qs[ index ] + 1 ) ], ncol=Qs[ index ] // 2 )
    # plt.subplot( 3, 1, 2 )
    # for i in range( Qs[ index ] ):
    #     plt.plot( error_rates, mean_diff[ :, 1, i ] )
    # plt.ylabel( "Normalized CPU Time (s/s)" )
    # plt.subplot( 3, 1, 3 )
    # for i in range( Qs[ index ] ):
    #     plt.plot( error_rates, mean_diff[ :, 2, i ] )
    # plt.ylabel( "Normalized Iteration Count" )
    #
    # plt.show()

    # fig = plt.figure( 8 )
    # ax = fig.add_subplot( projection="3d" )
    # plt.title( "New Replanning CPU Time vs Action Count" )
    # for index in range( len( domains ) ):
    #     mean_diff = np.mean( normalized_results[ index ][ :, 1, :, :, : ], axis=( 2 ) ) \
    #                      - np.mean( normalized_results[ index ][ :, 0, :, :, : ], axis=( 2 ) )
    #     mean_std = np.std( normalized_results[ index ][ :, 1, :, :, : ], axis=(2) ) \
    #                 + np.std( normalized_results[ index ][ :, 0, :, :, : ], axis=(2) )
    #     ax.scatter( mean_diff[ :, 0 ], mean_diff[ :, 1 ], mean_diff[ :, 2 ] )
    #
    # ax.set_xlabel( "Normalized Action Count" )
    # ax.set_ylabel( "Normalized CPU Time (s/s)" )
    # ax.set_zlabel( "Normalized Iteration Count" )
    # plt.legend( domains )
    # plt.show()

    # x = np.asarray( error_rates )
    #
    # bar_width = 1
    # c_0 = "blue"
    # c_1 = "red"
    # c_2 = "black"
    # plt.figure( 7 )
    # ax = plt.subplot( 3, 1, 1 )
    # index = 0
    # title = domains[ index ]
    # plt.title( title )
    # # plt.bar( x, new_mean_iteration_count, yerr=new_err_iteration_count, width=bar_width, label="new" )
    # # plt.bar( x + bar_width, old_mean_iteration_count, yerr=old_err_iteration_count, width=bar_width, label="old"  )
    # bp_0 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 0, 0, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x - 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_0, color=c_0 ),
    #                    capprops=dict( color=c_0 ),
    #                    whiskerprops=dict( color=c_0 ),
    #                    flierprops=dict( color=c_0, markeredgecolor=c_0 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # bp_1 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 1, 0, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x + 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_1, color=c_1 ),
    #                    capprops=dict( color=c_1 ),
    #                    whiskerprops=dict( color=c_1 ),
    #                    flierprops=dict( color=c_1, markeredgecolor=c_1 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # # plt.xlabel( "Problem #" )
    # plt.ylabel( "Normalized Action Count" )
    # ax.set_xticks( x )
    # ax.legend( [ bp_0[ "boxes" ][ 0 ], bp_1[ "boxes" ][ 0 ] ], planner_types )
    #
    # ax = plt.subplot( 3, 1, 2 )
    # # plt.bar( x, new_mean_cpu_time, yerr=new_err_cpu_time, width=bar_width, label="new" )
    # # plt.bar( x + bar_width, old_mean_cpu_time, yerr=old_err_cpu_time, width=bar_width, label="old" )
    # bp_0 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 0, 1, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x - 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_0, color=c_0 ),
    #                    capprops=dict( color=c_0 ),
    #                    whiskerprops=dict( color=c_0 ),
    #                    flierprops=dict( color=c_0, markeredgecolor=c_0 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # bp_1 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 1, 1, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x + 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_1, color=c_1 ),
    #                    capprops=dict( color=c_1 ),
    #                    whiskerprops=dict( color=c_1 ),
    #                    flierprops=dict( color=c_1, markeredgecolor=c_1 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # # plt.xlabel( "Problem #" )
    # plt.ylabel( "Normalized CPU Time (s/s)" )
    # ax.set_xticks( x )
    #
    # ax = plt.subplot( 3, 1, 3 )
    # # plt.bar( x, new_mean_action_count, yerr=new_err_action_count, width=bar_width, label="new" )
    # # plt.bar( x + bar_width, old_mean_action_count, yerr=old_err_action_count, width=bar_width, label="old" )
    # bp_0 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 0, 2, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x - 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_0, color=c_0 ),
    #                    capprops=dict( color=c_0 ),
    #                    whiskerprops=dict( color=c_0 ),
    #                    flierprops=dict( color=c_0, markeredgecolor=c_0 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # bp_1 = ax.boxplot( np.transpose( np.reshape( normalized_results[ index ][ :, 1, 2, :, : ], ( E, N * Qs[ index ] ) ) ), positions=x + 1.1 * bar_width / 2, widths=bar_width,
    #                    notch=True, labels=x, patch_artist=True,
    #                    boxprops=dict( facecolor=c_1, color=c_1 ),
    #                    capprops=dict( color=c_1 ),
    #                    whiskerprops=dict( color=c_1 ),
    #                    flierprops=dict( color=c_1, markeredgecolor=c_1 ),
    #                    medianprops=dict( color=c_2 ),
    #                    )
    # plt.xlabel( "Error Rate (%)" )
    # plt.ylabel( "Normalized Iteration Count" )
    # ax.set_xticks( x )
    # plt.show()

    plt.figure( 8 )
    plt.subplot( 3, 1, 1 )
    plt.title( "New Replanning Z-Score Scaled Change vs Error Rate" )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 0, :, : ], axis=( 1, 2 ) )
                     - np.mean( normalized_results[ i ][ :, 0, 0, :, : ], axis=( 1, 2 ) ),
                     )
    plt.legend( domains )
    plt.ylabel( "Normalized Action Count" )
    plt.grid()
    plt.subplot( 3, 1, 2 )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 1, :, : ], axis=( 1, 2 ) )
                     - np.mean( normalized_results[ i ][ :, 0, 1, :, : ], axis=( 1, 2 ) ),
                     )
    plt.ylabel( "Normalized CPU Time (s/s)" )
    plt.grid()
    plt.subplot( 3, 1, 3 )
    for i in range( len( domains ) ):
        plt.scatter( error_rates, np.mean( normalized_results[ i ][ :, 1, 2, :, : ], axis=(1, 2) )
                     - np.mean( normalized_results[ i ][ :, 0, 2, :, : ], axis=(1, 2) ),
                     )
    plt.ylabel( "Normalized Iteration Count" )
    plt.xlabel( "Error Rates (%)")
    plt.grid()
    plt.show()



"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""
