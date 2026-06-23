#!/usr/bin/env python
"""
File Description: Racetrack actions file. All the actions for Racetrack planning domain are defined here.
Derived from: PyHOP example of Racetrack domain variant by Dana Nau <nau@cs.umd.edu>

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

The racetrack actions use three state variables:
- loc = racecar location (x,y) as int tuple
- v = racecar velocity (vx, vy) as int tuple
- walls = location of all walls as {[}((x1,y1),(x2,y2)) ... } as set of tuples of location tuples representing
        the start and end points of all walls
"""

from ipyhop import Actions
import numpy as np

# all actions are usable on condition that there is no crash
# set velocity to new_v
def set_v( state, new_v ):
    loc = state.loc
    v = state.v
    walls = state.rigid[ "walls" ]
    # can only adjust v by one step
    if np.linalg.norm( np.asarray( new_v ) - np.asarray( v ) ) < 1.9:
        # location after one step
        new_loc = ( loc[ 0 ] + new_v[ 0 ], loc[ 1 ] + new_v[ 1 ] )
        move = ( loc, new_loc )
        # if a crash would not occur, update state
        if not crash( move, walls ):
            state.loc  = new_loc
            state.v = new_v
            return state
        else:
            print("\nSPLAT\n")

# Create a IPyHOP Actions object. An Actions object stores all the actions defined for the planning domain.
actions = Actions()
actions.declare_actions( [ set_v ] )

action_probability = {
    "set_v": [ 1, 0 ]
}

action_cost = {
    "set_v": 1
}

actions.declare_action_models(action_probability, action_cost)


# from Dana Nau below
###########################################################
####  Domain-Specific Functions for the Racetrack game ####
###########################################################

# def next_states(state, walls):
#     """Return a list of states we can go to from state"""
#     states = []
#     (loc, (vx, vy)) = state
#     for dx in [0, -1, 1]:
#         for dy in [0, -1, 1]:
#             (wx, wy) = (vx + dx, vy + dy)
#             newloc = (loc[0] + wx, loc[1] + wy)
#             if not crash((loc, newloc), walls):
#                 states.append((newloc, (wx, wy)))
#     return states


def goal_test(state, f_line):
    """Test whether state is on the finish line and has velocity (0,0)"""
    return state[1] == (0, 0) and intersect((state[0], state[0]), f_line)


def crash(move, walls):
    """Test whether move intersects a wall in walls"""
    for wall in walls:
        if intersect(move, wall): return True
    return False


def intersect(e1, e2):
    """Test whether edges e1 and e2 intersect"""

    # First, grab all the coordinates
    ((x1a, y1a), (x1b, y1b)) = e1
    ((x2a, y2a), (x2b, y2b)) = e2
    dx1 = x1a - x1b
    dy1 = y1a - y1b
    dx2 = x2a - x2b
    dy2 = y2a - y2b

    if (dx1 == 0) and (dx2 == 0):  # both lines vertical
        if x1a != x2a:
            return False
        else:  # the lines are collinear
            return collinear_point_in_edge((x1a, y1a), e2) \
                   or collinear_point_in_edge((x1b, y1b), e2) \
                   or collinear_point_in_edge((x2a, y2a), e1) \
                   or collinear_point_in_edge((x2b, y2b), e1)
    if (dx2 == 0):  # e2 is vertical (so m2 = infty), but e1 isn't vertical
        x = x2a
        # compute y = m1 * x + b1, but minimize roundoff error
        y = (x2a - x1a) * dy1 / float(dx1) + y1a
        return collinear_point_in_edge((x, y), e1) and collinear_point_in_edge((x, y), e2)
    elif (dx1 == 0):  # e1 is vertical (so m1 = infty), but e2 isn't vertical
        x = x1a
        # compute y = m2 * x + b2, but minimize roundoff error
        y = (x1a - x2a) * dy2 / float(dx2) + y2a
        return collinear_point_in_edge((x, y), e1) and collinear_point_in_edge((x, y), e2)
    else:  # neither line is vertical
        # check m1 = m2, without roundoff error:
        if dy1 * dx2 == dx1 * dy2:  # same slope, so either parallel or collinear
            # check b1 != b2, without roundoff error:
            if dx2 * dx1 * (y2a - y1a) != dy2 * dx1 * x2a - dy1 * dx2 * x1a:  # not collinear
                return False
            # collinear
            return collinear_point_in_edge((x1a, y1a), e2) \
                   or collinear_point_in_edge((x1b, y1b), e2) \
                   or collinear_point_in_edge((x2a, y2a), e1) \
                   or collinear_point_in_edge((x2b, y2b), e1)
        # compute x = (b2-b1)/(m1-m2) but minimize roundoff error:
        x = (dx2 * dx1 * (y2a - y1a) - dy2 * dx1 * x2a + dy1 * dx2 * x1a) / float(dx2 * dy1 - dy2 * dx1)
        # compute y = m1*x + b1 but minimize roundoff error
        y = (dy2 * dy1 * (x2a - x1a) - dx2 * dy1 * y2a + dx1 * dy2 * y1a) / float(dy2 * dx1 - dx2 * dy1)
    return collinear_point_in_edge((x, y), e1) and collinear_point_in_edge((x, y), e2)


def collinear_point_in_edge(point, edge):
    """
    Helper function for intersect, to test whether a point is in an edge,
    assuming the point and edge are already known to be collinear.
    """
    (x, y) = point
    ((xa, ya), (xb, yb)) = edge
    # point is in edge if (i) x is between xa and xb, inclusive, and (ii) y is between
    # ya and yb, inclusive. The test of y is redundant unless the edge is vertical.
    if ((xa <= x <= xb) or (xb <= x <= xa)) and ((ya <= y <= yb) or (yb <= y <= ya)):
        return True
    return False

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Racetrack Actions isn't implemented.")

"""
Author(s): Paul Zaidins, Dana Nau
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""