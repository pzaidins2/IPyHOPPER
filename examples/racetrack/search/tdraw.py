"""
File: tdraw.py
Author: Dana Nau <nau@cs.umd.edu>
Last updated: Aug 30, 2019

A drawing module for the racetrack domain. The main programs are:

 - draw_problem((s0, finish_line, walls), grid=True, title=''):
     Draw the initial state, finish line, and walls. grid is a flag telling whether to
     plot a grid behind the problem; title is a name to put at the top of the drawing.

 - draw_edges(edges,status): draw each edge in edges; edge color depends on status.
   The graphics window, which you can open by calling turtle.Screen(), needs to be
   open before you call this function.
"""

import turtle

def draw_problem(problem, grid=True, title=''):
    """
    draw_problem first set_scale to set the plotting scale,
    then it draws walls, s0, and finish line.
    The grid argument tells whether or not to draw a grid behind the problem.
    """
    (s0, finish_line, walls) = problem
    turtle.Screen()                 # open the graphics window
    clear()                         # make sure the window is empty
    set_scale(walls,grid)
    draw_lines(walls)
    if s0: 
        draw_dot(s0,color='red',size=8)
    if finish_line: 
        draw_lines([finish_line], color='brown', width=2, dots=0)
    if title: 
        draw_title(title,lowerleft,upperright)

def draw_title(title,ll,ur):
    """Write title at the top of the drawing."""
    turtle.penup()
    size = upperright - lowerleft
    turtle.goto(ur/2.5,ur+size*.01)
    turtle.write(title,font=('Arial',20,'normal'))

def draw_path(path):
    """draw a path"""
    pos0 = False
    for pos1 in path:
        if pos0:
            draw_lines([(pos0,pos1)], color='red', width=2, dots=8)
        pos0 = pos1

# for each node status, What width, color, and dot size to use
status_options = {
    'add':            (1, 'green', 0),  # generated nodes being put into frontier
    'discard':        (1, 'orange', 0), # generated nodes being discarded
    'expand':         (2, 'blue', 5),   # node expanded
    'frontier_prune': (1, 'orange', 0), # nodes pruned from frontier
    'explored_prune': (2, 'purple', 0), # nodes pruned from explored
    'solution':       (3, 'red', 8),    # nodes in the solution path
    }


def draw_edges(edges,status):
    """
    Draw the line for an individual edge. Use status to tell what kind of
    edge: add, discard, expand, re-exand, prune, retract, solution
    """
    (width, color, dots) = status_options[status]
    draw_lines(edges, width=width, color=color, dots=dots)


################## Primitives #######################
# These get called by the above functions.
# You probably won't need to call any of them directly.
    
def clear():
    """Clear the graphics window."""
    turtle.clear()

def set_scale(lines,grid=True):
    """This sets the coordinate scale for a square window whose dimensions are large
    enough to accommodate the lines that you need to draw. If grid=True, it will draw
    grid lines.
    """
    global lowerleft
    global upperright
    lowerleft = min([min(x0,y0,x1,y1) for ((x0,y0),(x1,y1)) in lines])
    upperright = max([max(x0,y0,x1,y1) for ((x0,y0),(x1,y1)) in lines])
    size = upperright - lowerleft
    margin = size*.1
    turtle.setworldcoordinates(lowerleft - margin, lowerleft - margin, \
        upperright + margin, upperright + margin)
    turtle.pen(speed=0,shown=False)         # 0 means use maximum possible speed
    if grid: draw_grid(lowerleft,upperright)
    
def draw_lines(lines, color='black', width=3, dots=0):
    """draw every line in lines"""
    turtle.pen(speed=0,shown=False)
    turtle.color(color)
    turtle.width(width)
    for line in lines:
        (p0, p1) = list(line)
        if p0 != p1:
            turtle.penup()
            turtle.goto(p0)
            draw_dot(p0,color='blue',size=6)
            turtle.pendown()
            turtle.goto(p1)
        if dots>0: draw_dot(p1,color=color,size=dots)


def draw_dot(loc,color='red',size=8):
    """put a dot at location loc"""
    turtle.penup()
    turtle.goto(loc)
    turtle.dot(size,color)

def draw_finish(loc,color='red',size=8):
    """put a dot at location loc"""
    (x,y) = loc
    turtle.penup()
    turtle.goto((x,y))
    turtle.dot(size,color)

def draw_grid(ll,ur):
    size = ur - ll
    # ad hoc way of choosing what grid lines to draw
    for gridsize in [1, 2, 5, 10, 20, 50, 100 ,200, 500]:
        lines = (ur-ll)/gridsize
        # print('gridsize', gridsize, '->', int(lines)+1, 'lines')
        if lines <= 11: break
    turtle.color('darkgray')
    turtle.width(1)
    
    # draw vertical grid lines:
    x = ll
    while x <= ur:
        if x == ur or int(x/gridsize)*gridsize == x:
            turtle.penup()
            turtle.goto(x, ll-.35*gridsize)
            turtle.write(str(x),align="center",font=("Arial",16,"normal"))
            turtle.goto(x,ll)
            turtle.pendown()
            turtle.goto(x,ur)
            # print(x,ll,'to',x,ur)
        x += 1
        
    # draw horizontal grid lines:
    y = ll
    while y <= ur:
        if y == ur or int(y/gridsize)*gridsize == y:
            turtle.penup()
            turtle.goto(ll-.1*gridsize, y - .06*gridsize)
            turtle.write(str(y),align="right",font=("Arial",16,"normal"))
            turtle.goto(ll,y)
            turtle.pendown()
            turtle.goto(ur,y)
            # print(ll,y,'to',ur,y)
        y += 1
