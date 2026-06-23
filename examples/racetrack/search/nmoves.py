"""
File: nmoves.py
Author: Dana Nau <nau@cs.umd.edu>
Last updated: Sept 5, 2019

This file contains a Racetrack heuristic function h_nmoves(state,fline,walls). 
It returns the number of moves that would be needed to reach the finish line
if there were no walls. The arguments are:

   - state is the current state. It should have the form ((x,y), (u,v)), where
      (x,y) is the current location and (u,v) is the current velocity.
   - fline is the finish line. It should have the form ((x1,y1), (x2,y2)), 
      where (x1,y1) and (x2,y2) are the two endpoints, and it should be either
      either vertical (x1 == x2) or horizontal (y1 == y2).
   - walls is a list of walls, each wall having the form ((x1,y1), (x2,y2)).
   
Unlike the heuristic functions in heuristic.py, h_nmoves is admissible. However,
it demonstrates how admissibility can reduce efficiency. With h_nmoves, A* is
guaranteed to find optimal solutions, but A* will generate many more nodes
than it generates with the heuristic functions in heuristics.py.
"""

import math

def cdist(v,t):
    """
    Return the distance we'll travel, assuming there are no walls,
    if the current speed is v and we want the last move to be at speed t.
    """
    if v < 0 or t < 0:
        raise Exception("v and t must be nonnegative")
    if t == v:
        return t
    elif t < v:
        # stopping distance for v, minus stopping distance for t
        return v*(v-1)/2 - t*(t-1)/2
    else:
        # stopping distance for 5, minus stopping distance for v
        return t*(t+1)/2 - v*(v+1)/2


def nmoves(v,d):
    """
    Return the number of moves we'll need to go exactly distance d
    if our current speed is v and there are no walls.
    """
    if d < 0:
        d = -d; v = -v    # ensure d >= 0:
    
    if v < 0:                  # going the wrong way, need to stop and reverse direction
        v = -v
        # add the distance needed to come to a stop
        d = d + cdist(v,0)
        # stopping requires v moves
        return v + nmoves(0,d)
        
    if cdist(v,0) > d:          # going too fast, will overshoot and have to back up
        d = cdist(v,0) - d      # distance once we've stopped
        return v + nmoves(0,d)   # v moves to stop, plus number of moves to get to d
    
    if cdist(v,0) == d:         # we'll come to a stop at exactly distance d
        return v                # v moves needed to stop
    
    else:
        # find tmax = largest t such that cdist(v,t) + cdist(t,0) <= d
        t = max(v-1,0)
        while (cdist(v,t) + cdist(t,0) <= d):
            tmax = t; dmax = cdist(v,t) + cdist(t,0)
            t = t+1
            
        # number of extra moves needed if dmax < d
        if dmax < d:
            extra = math.ceil((d - dmax) / tmax)
        else: extra = 0
        
        # moves to change from v to tmax, plus moves to stop + extra moves
        return (tmax - v) + tmax + extra



def h_nmoves(state,fline,walls):
    """
    Return the exact number of moves needed to finish if there are no walls.
    """
    ((x,y),(u,v)) = state    
    ((x1,y1),(x2,y2)) = fline
    if x1 == x2:           # fline is vertical, so iterate over y
        mx = nmoves(u,(x1-x))
        my = min([nmoves(v,y3-y) for y3 in range(min(y1,y2),max(y1,y2)+1)])
    else:                  # fline is horizontal, so iterate over x
        my = nmoves(v, (y1-y))
        mx = min([nmoves(u,x3-x) for x3 in range(min(x1,x2),max(x1,x2)+1)])

    return max(mx,my)
