#!/usr/bin/env python
"""
File Description: Rescue methods file. All the methods for Rescue planning domain are defined here.
"""

import math
from ipyhop import Methods

methods = Methods()


def tm1_move(state, r, l, rigid):  # Take the straight path.
    if state.loc[r] == l:
        yield []
        return
    elif state.robot_type[r] == 'wheeled':      # TODO: Ask if we are excluding UAVs from this method
        dist = None         # TODO: Ask why dist needs to be passed to the action/command.
        yield [('a_move_euclidean', r, state.loc[r], l, dist)]
        return
    yield None


def tm2_move(state, r, l, rigid):  # Take the manhattan path.
    if state.loc[r] == l:
        yield []
        return
    elif state.robot_type[r] == 'wheeled':  # TODO: Ask if we are excluding UAVs from this method
        dist = None  # TODO: Ask why dist needs to be passed to the action/command.
        yield [('a_move_manhattan', r, state.loc[r], l, dist)]
        return
    yield None


def tm3_move(state, r, l, rigid):  # Take the curved path.
    if state.loc[r] == l:
        yield []
        return
    elif state.robot_type[r] == 'wheeled':  # TODO: Ask if we are excluding UAVs from this method
        dist = None  # TODO: Ask why dist needs to be passed to the action/command.
        yield [('a_move_curved', r, state.loc[r], l, dist)]
        return
    yield None


def tm4_move(state, r, l, rigid):  # Fly to the location.
    if state.loc[r] == l:
        yield []
        return
    elif state.robot_type[r] == 'uav':
        yield [('a_move_fly', r, state.loc[r], l)]
        return
    yield None


def tm5_move(state, r, l, rigid):  # Fly to the location.
    if state.loc[r] == l:
        yield []
        return
    elif state.robot_type[r] == 'uav':
        yield [('a_move_alt_fly', r, state.loc[r], l)]
        return
    yield None


methods.declare_task_methods('move_task', [tm1_move, tm2_move, tm3_move, tm4_move, tm5_move])


def tm1_new_robot_encap(state, p, rigid):
    task_list = []
    r2 = state.new_robot[1]
    if r2 is not None:
        if state.has_medicine[r2] == 0:
            task_list.append(('get_supplies_task', r2))
        task_list.append(('help_person_task', r2, p))
        task_list.append(('a_free_robot', r2))
        yield task_list
        return
    yield None


methods.declare_task_methods('new_robot_encap_task', [tm1_new_robot_encap])


def tm1_rescue(state, r, p, rigid):
    if state.robot_type[r] != 'uav':
        task_list = []
        if state.has_medicine[r] == 0:
            task_list.append(('get_supplies_task', r))
        task_list.append(('help_person_task', r, p))
        yield task_list
        return
    yield None


def tm2_rescue(state, r, p, rigid):

    if state.robot_type[r] == 'uav':
        yield [('get_robot_task', ), ('new_robot_encap_task', p)]


methods.declare_task_methods('rescue_task', [tm1_rescue, tm2_rescue])


def tm1_support_person(state, r, p, rigid):
    if state.status[p] == 'injured':
        yield [('a_support_person', r, p), ]
        return
    yield None


def tm2_support_person(state, r, p, rigid):
    if state.status[p] == 'injured':
        yield [('a_support_person_2', r, p), ]
        return
    yield None


def tm3_support_person(state, r, p, rigid):
    if state.status[state.loc[p]] == 'has_debri':
        yield [('a_clear_location', r, state.loc[p]), ]
        return
    yield None


def tm4_support_person(state, r, p, rigid):
    if state.status[state.loc[p]] == 'has_debri':
        yield [('a_clear_location_2', r, state.loc[p]), ]
        return
    yield None


def tm5_support_person(state, r, p, rigid):
    yield [('a_check_real', state.loc[p]), ]


# Extra task added.
methods.declare_task_methods('support_task', [tm1_support_person, tm2_support_person, tm3_support_person,
                                              tm4_support_person, tm5_support_person])


# Modified this task method.
def tm1_help_person(state, r, p, rigid):
    yield [('move_task', r, state.loc[p]), ('a_inspect_location', r, state.loc[p]), ('a_inspect_person', r, p),
            ('support_task', r, p)]


methods.declare_task_methods('help_person_task', [tm1_help_person])


def eu_dist(l0, l1):
    (x0, y0) = l0
    (x1, y1) = l1
    return math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))


def tm1_get_supplies(state, r, rigid):     # Get supplies from the nearest robot.
    r2 = None
    nearest_dist = float("inf")

    for r1 in rigid['wheeled_robots']:
        if state.has_medicine[r1] > 0:
            dist = eu_dist(state.loc[r], state.loc[r1])
            if dist < nearest_dist:
                nearest_dist = dist
                r2 = r1

    if r2 is not None:
        yield [('move_task', r, state.loc[r2]), ('a_transfer', r2, r)]


def tm2_get_supplies(state, r, rigid):     # Get supplies from the base.
    yield [('move_task', r, (1, 1)), ('a_replenish_supplies', r)]


methods.declare_task_methods('get_supplies_task', [tm1_get_supplies, tm2_get_supplies])


# Added an ecapsulation for the rescue task
def tm1_rescue_encap(state, r, rigid):
    img = state.current_image[r]
    position = img['loc']
    person = img['person']

    if person is not None:
        yield [('rescue_task', r, person)]
    else:
        yield []


methods.declare_task_methods('rescue_encap_task', [tm1_rescue_encap])


def tm1_survey(state, r, l, rigid):
    if state.robot_type[r] != 'uav':
        yield None
        return

    yield [('adjust_altitute_task', r), ('a_capture_image', r, 'front_camera', l), ('rescue_encap_task', r),
            ('a_check_real', l)]


def tm2_survey(state, r, l, rigid):
    if state.robot_type[r] != 'uav':
        yield None
        return

    yield [('adjust_altitute_task', r), ('a_capture_image', r, 'bottom_camera', l), ('rescue_encap_task', r),
            ('a_check_real', l)]


methods.declare_task_methods('survey_task', [tm1_survey, tm2_survey])


def tm1_get_robot(state, rigid):
    dist = float("inf")
    robot = None

    for r in rigid['wheeled_robots']:
        if state.status[r] == 'free':
            _dist = eu_dist(state.loc[r], (1, 1))
            if _dist < dist:
                robot = r
                dist = _dist

    if robot is None:
        yield None
    else:
        yield [('a_engage_robot', robot)]


def tm2_get_robot(state, rigid):
    yield [('a_force_engage_robot',)]


methods.declare_task_methods('get_robot_task', [tm1_get_robot, tm2_get_robot])


def tm1_adjust_altitute(state, r, rigid):
    if state.altitude[r] == 'high':
        yield [('a_change_altitude', r, 'low')]


def tm2_adjust_altitute(state, r, rigid):
    if state.altitude[r] == 'low':
        yield [('a_change_altitude', r, 'high')]


methods.declare_task_methods('adjust_altitute_task', [tm1_adjust_altitute, tm2_adjust_altitute])


# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Rescue Methods isn't implemented.")

"""
Author(s): Yash Bansod
Repository: https://github.com/YashBansod/IPyHOP
Organization: University of Maryland at College Park
"""