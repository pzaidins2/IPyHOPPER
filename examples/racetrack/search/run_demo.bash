#!/bin/bash

###############################################################################
#
# File: run_tests.bash
# Author: Dana Nau <nau@cs.umd.edu>
# Last updated: Feb 18, 2020
#
# This bash script uses three lists (racetrack problems, heuristic functions,
# and search strategies) and iterates over every possible combination of
# problem, heuristic function, and search strategy. For each combination, it
# does the search, and prints and/or draws information about what it does.
#
# IMPORTANT: TO GET THIS FILE TO WORK, YOU NEED TO MODIFY IT.
#
# You'll need to specify the python pathname, and the sample problems,
# heuristics, and search strategies that you want to use. 
# The comments will tell you where to make changes.
#
###############################################################################


set -f    # disable globbing, because we don't want the name a* to be expanded

###############################################################################
#
# START OF CUSTOMIZATION OPTIONS
# Below are the things you need to modify
#
###############################################################################



### IMPORTANT: Change this to use the pathname of YOUR python program
#
python=$PYTHON_PATH


# This line gives the rootname of the file that contains the test problems.
# Modify it if you want to use a different file.
#
prob_file=sample_probs	          # i.e., use the file sample_probs.py


# Below, the first line is a list of all the problems in sample_probs.py, 
# roughly in increasing order of difficulty.  Modify the second line to include
# just the ones that you want to use.
#
problems=(rect20 rect20a rect20b rect20c rect20d rect20e rect50 wall8a wall8b lhook16 rhook16a rhook16b spiral16 spiral24 pdes30 pdes30b rectwall8 rectwall16 rectwall32 rectwall32a twisty0)
problems=(lhook16)


# Here's the rootname of the file that contains the heuristic functions.
# Replace it with the rootname of your heuristic function file.
#
heur_file=sample_heuristics

# The first line is a list of all the heuristic functions in sample_heuristics.py.
# Modify the second line to specify the heuristic function(s) you want to use.
#
heuristics=(h_edist h_esdist h_walldist)
heuristics=(h_walldist)


# The first line is a list of all the available search strategies.
# Modify the second line to specify the ones you want to use.
#
strategies=(bf df uc gbf a*)
strategies=(gbf)

# Modify the following line to specify how verbose you want fsearch.main to be.
# The options are 0, 1, 2, 3, 4.
#
verb=2

# Use draw=1 to draw the search tree, or draw=0 to draw nothing
#
draw=1

###############################################################################
#
# END OF CUSTOMIZATION OPTIONS
#
###############################################################################


# The following code will iterate over every combination of sample problem, 
# heuristic function, and search strategy in your above lists. For each combination,
# it will first display the results graphically, and then do a time test.

# exit the loop when the user presses ^C, rather than going to the next iteration
trap "echo Exited!; exit;" SIGINT SIGTERM   

for prob in ${problems[*]}
do
  for heur in ${heuristics[*]}
  do
    for strat in ${strategies[*]}
    do

        # strings for preliminary setup, running the program, and printing the result
        setup="import racetrack, $prob_file, $heur_file"
        run_prog="result=racetrack.main($prob_file.$prob, '$strat', $heur_file.$heur, $heur_file, verbose=$verb, draw=$draw, title='$strat, $heur, $prob')"
        
        echo ''
        echo "Running '$strat, $heur, $prob with verbose=$verb and draw=$draw"
        # execute the strings in python
        python -c "$setup; $run_prog"
    done
  done
done
