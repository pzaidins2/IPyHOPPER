#!/bin/bash

###############################################################################
#
# File: run_tests.bash
# Author: Dana Nau <nau@cs.umd.edu>
# Last updated: Sept 28, 2019
#
# test whether Python retains global variables during timing tests
#
###############################################################################



### IMPORTANT!!! Change this to use the pathname of YOUR python program
#
python=/Users/Nau/anaconda3/bin/python


# exit the loop when the user presses ^C, rather than going to the next iteration
trap "echo Exited!; exit;" SIGINT SIGTERM   


# Here's the code for doing a time test.
echo ''
echo "Time testing with flag == True"

filename=test_global

# execute the time test
$python -m timeit -s "import importlib, $filename" "importlib.reload($filename); $filename.foo(100000000,True)"

# Here's the code for doing a time test.
echo ''
echo "Time testing with flag == False"

# execute the time test
$python -m timeit -s "import importlib, $filename" "importlib.reload($filename); $filename.foo(100000000,False)"

# execute the time test
$python -m timeit -s "import importlib, $filename" "pass"

