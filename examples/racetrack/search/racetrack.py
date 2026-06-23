"""
File: racetrack.py
Author: Dana Nau <nau@cs.umd.edu>
Last updated: Feb 18, 2020

This version includes my timing-test fix from last September.
"""

import examples.racetrack.search.tdraw as tdraw
import turtle    # Code to use Python's "turtle drawing" package
import math, sys
import examples.racetrack.search.fsearch as fsearch
import importlib


def main(problem, strategy, h, v_0=(0,0), verbose=2, draw=0, title=''):
    """
    Args are as follows:
    - prob should be a triple [s0, f_line, walls], where
        s0 is the initial state, f_line is the finish line, walls is a list of walls
    - strategy should be 'bf' (best first), 'df' (depth first),
        'uc' (uniform cost), 'gbf' (greedy best first), 'a*', or
        'none' (don't try to solve the problem, just display it).
    - h should be a heuristic function of three arguments h(s,f_line,walls), where
        s is the current state, f_line is the finish line, walls is a list of walls
    - module should be the name of the file that contains h
    - verbose should be one of the following:
        0 - silent, just return the answer.
        1 - print some statistics at the end of the search.
        2 - print brief info at each iteration, and statistics at the end of the search.
        3 - print additional info at each iteration, and stats at the end of the search.
        4 - print the above, and pause at each iteration.
    - draw should either be 0 (draw nothing) or 1 (draw everything)
    - title is a title to put at the top of the drawing. It defaults to the names of the
        search strategy and heuristic (if there is one)
    """
    s0 = (problem[0], v_0)    # initial state
    f_line = problem[1]
    walls = problem[2]
    # convert h, next_states, and goal_test to the one-arg functions fsearch wants
    h_for_fsearch = lambda state: h(state, f_line, walls)
    next_for_fsearch = lambda state: [(s,1) for s in next_states(state,walls)]
    goal_for_fsearch = lambda state: goal_test(state,f_line)

    if draw:
        draw_edges = tdraw.draw_edges
        if title == '': 
            if h:  title = strategy + ', ' + h.__name__
            else:  title = strategy
        turtle.Screen()             # open the graphics window
        tdraw.draw_problem(problem, title=title)
    else:
        draw_edges = None
    if strategy != 'none':
        # importlib.reload(module)
        solution = fsearch.main(s0, next_for_fsearch, goal_for_fsearch, strategy, \
        h_for_fsearch, verbose, draw_edges)
    else:
        solution = None
    if verbose:
       print('Solution ({} states):\n{}'.format(len(solution), solution))
    # if draw:
    #     print("\n*** Finished running '{}'.".format(title))
    #     print("Type carriage return to continue:")
    #     sys.stdin.readline()
#        turtle.mainloop()
    return solution


###########################################################
####  Domain-Specific Functions for the Racetrack game ####
###########################################################

def next_states(state,walls):
    """Return a list of states we can go to from state"""
    states = []
    (loc,(vx,vy)) = state
    for dx in [0,-1,1]:
        for dy in [0,-1,1]:
            (wx,wy) = (vx+dx,vy+dy)
            newloc = (loc[0]+wx,loc[1]+wy)
            if not crash((loc,newloc),walls):
                states.append((newloc,(wx,wy)))
    return states

def goal_test(state,f_line):
    """Test whether state is on the finish line and has velocity (0,0)"""
    return state[1] == (0,0) and intersect((state[0],state[0]), f_line)

def crash(move,walls):
    """Test whether move intersects a wall in walls"""
    for wall in walls:
        if intersect(move,wall): return True
    return False


def intersect(e1,e2):
    """Test whether edges e1 and e2 intersect"""       
    
    # First, grab all the coordinates
    ((x1a,y1a), (x1b,y1b)) = e1
    ((x2a,y2a), (x2b,y2b)) = e2
    dx1 = x1a-x1b
    dy1 = y1a-y1b
    dx2 = x2a-x2b
    dy2 = y2a-y2b
    
    if (dx1 == 0) and (dx2 == 0):       # both lines vertical
        if x1a != x2a: return False
        else:   # the lines are collinear
            return collinear_point_in_edge((x1a,y1a),e2) \
                or collinear_point_in_edge((x1b,y1b),e2) \
                or collinear_point_in_edge((x2a,y2a),e1) \
                or collinear_point_in_edge((x2b,y2b),e1)
    if (dx2 == 0):      # e2 is vertical (so m2 = infty), but e1 isn't vertical
        x = x2a
        # compute y = m1 * x + b1, but minimize roundoff error
        y = (x2a-x1a)*dy1/float(dx1) + y1a
        return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
    elif (dx1 == 0):        # e1 is vertical (so m1 = infty), but e2 isn't vertical
        x = x1a
        # compute y = m2 * x + b2, but minimize roundoff error
        y = (x1a-x2a)*dy2/float(dx2) + y2a
        return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 
    else:       # neither line is vertical
        # check m1 = m2, without roundoff error:
        if dy1*dx2 == dx1*dy2:      # same slope, so either parallel or collinear
            # check b1 != b2, without roundoff error:
            if dx2*dx1*(y2a-y1a) != dy2*dx1*x2a - dy1*dx2*x1a:  # not collinear
                return False
            # collinear
            return collinear_point_in_edge((x1a,y1a),e2) \
                or collinear_point_in_edge((x1b,y1b),e2) \
                or collinear_point_in_edge((x2a,y2a),e1) \
                or collinear_point_in_edge((x2b,y2b),e1)
        # compute x = (b2-b1)/(m1-m2) but minimize roundoff error:
        x = (dx2*dx1*(y2a-y1a) - dy2*dx1*x2a + dy1*dx2*x1a)/float(dx2*dy1 - dy2*dx1)
        # compute y = m1*x + b1 but minimize roundoff error
        y = (dy2*dy1*(x2a-x1a) - dx2*dy1*y2a + dx1*dy2*y1a)/float(dy2*dx1 - dx2*dy1)
    return collinear_point_in_edge((x,y),e1) and collinear_point_in_edge((x,y),e2) 


def collinear_point_in_edge(point, edge):
    """
    Helper function for intersect, to test whether a point is in an edge,
    assuming the point and edge are already known to be collinear.
    """
    (x,y) = point
    ((xa,ya),(xb,yb)) = edge
    # point is in edge if (i) x is between xa and xb, inclusive, and (ii) y is between
    # ya and yb, inclusive. The test of y is redundant unless the edge is vertical.
    if ((xa <= x <= xb) or (xb <= x <= xa)) and ((ya <= y <= yb) or (yb <= y <= ya)):
       return True
    return False
        

