#!/usr/bin/env python
"""
File Description: Robosub example file. Run this file to solve the Robosub planning problem.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from __future__ import print_function
from examples.robosub.domain.robosub_mod_methods import methods
from examples.robosub.domain.robosub_mod_actions import actions
from examples.robosub.problem.robosub_mod_problem import init_state, task_list_1
from ipyhop import IPyHOP, planar_plot


# ******************************************        Main Program Start      ****************************************** #
def main():
    print(methods)
    print(actions)
    print(init_state)

    planner = IPyHOP(methods, actions)
    planner.blacklist_command(('a_touch_back_v', 'v1', 'l2'))
    planner.blacklist_command(('a_touch_front_v', 'v1', 'l2'))
    plan = planner.plan(init_state, task_list_1, verbose=3)
    graph = planner.sol_tree



    print('Plan: ')
    for action in plan:
        print('\t', action)
    # planar_plot(graph, root_node=0)
    # fail_action = ('a_drop_garlic_closed_coffin', 'gm2', 'c1', 'l3')
    # fail_action = ('a_drop_garlic_closed_coffin', 'gm1', 'c1', 'l3')
    fail_action = ('a_drop_garlic_open_coffin', 'gm1', 'c1')
    # print( planner.sol_tree.nodes(data=True))
    for k, v in planner.sol_tree.nodes(data=True):
        # print( k )
        # print( v )
        if v[ "info" ] == fail_action:
            fail_node_id = k
            fail_node = v
            break
    fail_node_pos = plan.index( fail_action )
    parent_node_id = next(graph.predecessors(fail_node_id))
    parent_node = graph.nodes[parent_node_id]
    new_task_list = planner.replan(parent_node["state"], fail_node_pos, verbose=3)
    # new_task_list = [ graph.nodes[ new_task ][ "info" ] for new_task in new_task_list ]
    print("If failure occurs at: " + str(fail_action))
    print("New task list will be: " + str(new_task_list))
    planar_plot(graph, root_node=0)


# ******************************************        Main Program End        ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    try:
        main()
        print('\nFile executed successfully!\n')
    except KeyboardInterrupt:
        print('\nProcess interrupted by user. Bye!')

"""
Author(s): Yash Bansod
Repository: https://github.com/YashBansod/IPyHOP
Organization: University of Maryland at College Park
"""