"""
File: make_random_probs.py
Author: Dana Nau <nau@cs.umd.edu>
Last updated: April 18, 2019 (modified to increase minimum distance between walls)

Some code to make random racetrack problems. It doesn't do a very good job,
and I'll look for a way to replace it with something better.

The main program creates problems and prints them to standard output, so if you 
want to put them in a file you should either cut-and-paste from the command-line 
window or redirect standard output.

Each randomly generated problem is on a square grid with some randomly generated
obstacles, so they look pretty different from the ones in sample_probs.py. 
They also are a bit flaky, e.g., sometimes the finish line will partially overlap
some of the obstacles.
"""

import sys              # We need sys.readline
import tdraw, turtle    # Code to use Python's "turtle drawing" package

import numpy
from numpy.random import randint as randint
import time


def main(n=20, size=48, display=0, title=''):
    """
    Program to generate random racetracks. The parameters are as follows:
    
    n: number of racetracks to create.
    
    size: each racetrack is a square grid of dimensions approximately size x size. 
    Because of some idiosyncracies involving the maze subroutine, the dimensions are
    rounded to the nearest multiple of 4.
    
    title: a string to use as part of each racetrack's name.

    display: each time a racetrack is created, its definition will be printed out.
    Furthermore, if display > 0, an ASCII drawing of the racetrack will be printed,
    and if display > 1, the racetrack will be drawn using tdraw.
    """
    
    for i in range(n):

        title = 'problem {}'.format(i)
        problem = make_one(size=size, complexity=1, density=1, display=display, title=title)
        s0 = (problem[0], (0,0))    # initial state
        f_line = problem[1]
        walls = problem[2]

        print('problem{} = {}\n'.format(i, problem))
        if display>0:
            print("\n*** maketrack: finished drawing {}.".format(title), end=' ')
            print("Hit carriage return to continue.\n")
            sys.stdin.readline()


def make_one(size=48, display=0, title='', density=1, complexity=1):
    """
    Create a random racetrack and print out its definition. The parameters are:
    
    size: each racetrack is a square grid of dimensions approximately size x size. 
    Because of some idiosyncracies involving the maze subroutine, the dimensions are
    rounded to the nearest multiple of 4.
    
    title: a string to use as part of each racetrack's name.

    display: if display > 0, an ASCII drawing of the maze will be printed (in
    addition to the racetrack's definition). If display > 1, the racetrack will
    also be displayed in a graphics window.

    density and complexity: arguments for the maze subroutine. They affect how
    many obstacles (inner walls) to create, and how long each of them should be.

    The strategy is as follows. First, use the maze subroutine to create a random
    maze of dimensions size/4 x size/4. Next, add a starting point and finish line.
    Then, so the distance between adjacent walls won't be too small, multiply all
    coordinates by 4, to get a racetrack of dimensions size x size.
    """

    # The maze program requires width and height to be odd, 
    # so round them to the nearest odd integer
    xmax = ymax = (size // 4) * 2 + 1
    M = maze(xmax, ymax, complexity, density)

#    if display>0: print_maze(M,xmax,ymax,title)
    
    # M is a 2-D array of True/False (i.e., blocked/non-blocked) values.
    # Look for horizontal and vertical strings of blocked points, and
    # translate them into walls for the racetrack problem.
    walls = []
    for x in range(xmax):
        walls.extend(make_vertical_walls(xmax,ymax,x,M))
    for y in range(ymax):
        walls.extend(make_horizontal_walls(xmax,ymax,y,M))
    
    (start,x,y) = choose_starting_point(M,xmax,ymax)
    finish = choose_finish_line(x,y,M,xmax,ymax)
    print(finish)

    if display>0: print_racetrack(title,start,finish,M,xmax,ymax)
    
    # the racetrack's width and height are 1/2 of what we want, so double them
    problem = double_prob(start, finish, walls)
    problem = double_prob(start, finish, walls)
    if display>1:
        draw_edges = tdraw.draw_edges
        turtle.Screen()                # open the graphics window
        turtle.clearscreen()
        tdraw.draw_problem(problem, title=title)
    return problem
    
    
def choose_starting_point(M,xmax,ymax):
    """
    Randomly choose the starting point from one of four locations in the maze M: 
    near the bottom left, bottom right, top left, or top right.
    """

    # choose starting point
    x = round(xmax/6.0)
    y = round(ymax/6.0)
    if randint(0,1): x = xmax - x
    if randint(0,1): y = xmax - y
    
    # adjust starting point so that it isn't on a wall. Do this by iterating
    # through 25 possible locations and taking the first one that works.
    start = False
    for xx in [x, x-1, x+1, x-2, x+2]:
        for yy in [y, y-1, y+1, y-2, y+2]:
            if xx in range(1,xmax) and yy in range(1,ymax) and not M[xx,yy]:
                start = (xx,yy)
                break
        if start: break

    # Return both the starting point and the unmodified (x,y) values. The latter
    # are needed to tell choose_finish_line what quadrant the starting point is in,
    # so that it can put the finish line in a different quadrant.
    return (start, x,y)


def choose_finish_line(x,y,M,xmax,ymax):
    """
    Create a finish line near a different corner from the starting point.
    The finish line may overlap with one or more walls, but 
    neither of the endpoints should be inside a wall.
    """

    # Create the first finish-line vertex near one of the three corners
    # that aren't near the starting point. Choose among them at random.
    choose = randint(0,2)
    if choose == 0:
        fin1x = x
        fin1y = round(ymax-y)
    elif choose == 1:
        fin1x = round(xmax-x)
        fin1y = y
    else:
        fin1x = round(xmax-x)
        fin1y = round(ymax-y)

    # For the other vertex, choose randomly between horizontal and vertical
    # orientations.

    fin2x = fin1x
    fin2y = fin1y
    horizontal = randint(0,1)
    if horizontal:            # move the x coordinate away from the corner
        if fin2x < xmax/2:    fin2x = round(fin2x + xmax/4)
        else:                fin2x = round(fin2x - xmax/4)
    else:                    # move the y coordinate away from the corner
        if fin2y < ymax/2:    fin2y = round(fin2y + ymax/4)
        else:                fin2y = round(fin2y - ymax/4)
        
#    print('foo', (fin1x,fin1y), (fin2x, fin2y))
    
    # To try to ensure that the problem is solvable, adjust the finish line
    # so that neither endpoint is on a wall. We try up to 25 different
    # locations, and I believe at least one of them should work. This
    # won't prevent *every* case where the finish line intersects a wall,
    # but it catches some of them - and it's a lot easier than running
    # an "intersect" operation with every wall in the maze.
    
    finish = False
    for x in [0, -1, +1, -2, +2]:
        for y in [0, -1, +1, -2, +2]:
            if fin1x + x in range(xmax) and fin2x + x in range(xmax) \
            and fin1y + y in range(ymax) and fin2y + y in range(ymax) \
            and not M[fin1x + x, fin1y + y] and not M[fin2x + x, fin2y + y]:
                finish = [(fin1x + x, fin1y + y), (fin2x + x, fin2y + y)]
                break
        if finish: break
    return finish


def maze(width=15, height=15, complexity=1, density=1):
    """
    Modified version of a random maze generator from Wikipedia.
    It returns a 2-D array of True/False values indicating whether each point
    is blocked. A horizontal or vertical string of blocked points is a wall.
    Both width and height should be odd, otherwise the maze generator will
    add 1 to make them odd.
    """
    
    # Ensure height and width are odd numbers
    shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
    
    # make number of paths to draw = density * 1/10 * (width + height)
    density = density * (shape[0] + shape[1]) // 10
    
    # make number of edges per path = complexity * width * height
    complexity = complexity * shape[0] * shape[1]

    # Build the maze
    Z = numpy.zeros(shape, dtype=bool)
    # Fill borders
    Z[0, :] = Z[-1, :] = 1
    Z[:, 0] = Z[:, -1] = 1
    # Make aisles
    for i in range(density):
        x, y = randint(0, shape[1] // 2) * 2, randint(0, shape[0] // 2) * 2
        Z[y, x] = 1
        for j in range(complexity):
            neighbours = []
            if x > 1:              neighbours.append((y, x - 2))
            if x < shape[1] - 2:  neighbours.append((y, x + 2))
            if y > 1:              neighbours.append((y - 2, x))
            if y < shape[0] - 2:  neighbours.append((y + 2, x))
            if len(neighbours):
                y_,x_ = neighbours[randint(0, len(neighbours) - 1)]
                if Z[y_, x_] == 0:
                    Z[y_, x_] = 1
                    Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                    x, y = x_, y_

    return Z


def make_horizontal_walls(xmax,ymax,y,M):
    startx = None
    walls = []
    for x in range(xmax):
        if startx is None:
            if M[x,y]:            # start a wall at x
                startx = x
        else:                     # wall in progress
            if x == xmax - 1:     # end of row, so terminate the wall at x
                walls.append([(startx,y), (x,y)])
                startx = None
            elif not M[x,y]:      # either the wall ended or it was just a point
                if x == startx+1: # it was just a point
                    startx = None
                else:             # it was a wall, and it ended at x-1
                    walls.append([(startx,y), (x-1,y)])
                    startx = None
    return walls

def make_vertical_walls(xmax,ymax,x,M):
    starty = None
    walls = []
    for y in range(ymax):
        if starty is None:
            if M[x,y]:           # start a wall at y
                starty = y
        else:                    # wall in progress
            if y == ymax - 1:    # end of row, so terminate the wall at y
                walls.append([(x,starty), (x,y)])
                starty = None
            elif not M[x,y]:    # either the wall ended or it was just a point
                if y == starty+1:    # it was just a point
                    starty = None
                else:
                    walls.append([(x,starty), (x,y-1)])
                starty = None
    return walls

def print_racetrack(title,start,finish,M,xmax,ymax):
    """
    Print a text representation of a racetrack.
    xmax and ymax are the x and y dimensions of the matrix.
    """

    ((x1,y1), (x2,y2)) = finish    
    print(title)
    for y in range(ymax-1,-1,-1):
        for x in range(xmax):
            if M[x,y]: print('x', end=' ')
            elif start == (x,y): print('@', end=' ')
            elif y1 == y2 and y == y1 and min(x1,x2) <= x and x <= max(x1,x2): print('-', end=' ')
            elif x1 == x2 and x == x1 and min(y1,y2) <= y and y <= max(y1,y2): print('|', end=' ')
            else:    print(' ', end=' ')
        print('')

def double_prob(start, finish, walls):
    """Double both the x and y dimensions of a racetrack problem."""
    return [double_point(start), double_edge(finish), double_edges(walls)]

def double_point(point):
    return (2*point[0], 2*point[1])

def double_edge(edge):
    return [double_point(edge[0]), double_point(edge[1])]

def double_edges(edges):
    return [double_edge(e) for e in edges]

