#!/usr/bin/env python
"""
File Description: File used for definition of actor
"""

# ******************************************    Libraries to be imported    ****************************************** #
from typing import List, Union, Tuple, Optional
from ipyhop.state import State
from ipyhop.planner import IPyHOP
from ipyhop.planner_old import IPyHOP_Old
from ipyhop.mc_executor import MonteCarloExecutor
from networkx import dfs_preorder_nodes


# ******************************************    Class Declaration Start     ****************************************** #
class Actor:
    # ******************************        Class Method Declaration        ****************************************** #
    """
    Actor Constructor.

    :param planner: An instance of IPyHOP class containing the collection of methods and actions in the planning domain.
    :param executor: An instance of MonteCarloExecutor class containing the collection of actions in the planning domain.
    """
    def __init__(self, planner: Union[ IPyHOP, IPyHOP_Old ], executor: MonteCarloExecutor):
        self.planner = planner
        self.executor = executor

    # ******************************        Class Method Declaration        ****************************************** #
    """
        Method that .

        :param initial_state: An instance of State class representing the initial state.
        :param to_do_list: A list of tuples of strings representing tasks and goals that must be completed and achieved.
    """
    def complete_to_do(self, initial_state: State, to_do_list: List[Tuple[str]], verbose: Optional[int]=0) -> List[Tuple[str]]:
        # list of actions performed
        history = []
        # find plan to complete to_do_list
        plan = self.planner.plan(initial_state, to_do_list, verbose=verbose)

        # print( self.planner.iterations )
        if verbose >= 1:
            print("Initial plan created\n")
            if verbose >= 2:
                print("Plan is:\n" + str( plan ) + "\n")
            print("Executing plan...\n")
        curr_state = initial_state

        # act on plan until completion or failure, replanning has needed
        did_replan = False
        plan_impossible = False
        plan_success = False
        exec_index = 0
        # if len( [ *self.planner.sol_tree.nodes ] ) == 1:
        #     plan_impossible = True
        #     if verbose > 0:
        #         print("No Plan is possible")
        #     raise ("No plan is possible...")
        # original plan failed
        if plan is False:
            plan_impossible = True
        while not ( plan_impossible or plan_success ):
            # execute until success or failure

            exec_result = self.executor.execute( curr_state, plan[ exec_index: ] )
            # catch plan failures
            if exec_result is False:
                plan_impossible = True
                break

            # unzip list of tuples into seperate lists
            action_list, state_list = [ *zip( *exec_result ) ]
            # if no state is None plan executed successfully
            # if type( self.planner ) == IPyHOP_Old and plan == [ ]:
            #     plan_impossible = True
            #     raise( "No plan found!" )
            #     if verbose >= 1:
            #         print( "No plan is possible..." )
            #     break
            if state_list[ -1 ] is not None:
                plan_success = True
                history += [ *action_list[ 1: ] ]
                if verbose >= 1:
                    print("Plan executed successfully")
                break
            else:
                # where failure occurred in most recent execution
                action_index = len( state_list ) - 1
                history += action_list[ 1: ]
                if verbose >= 2:
                    print("Plan failed at: " + str(action_list[action_index]))
                # update location relative to whole plan
                exec_index += action_index - 1
                # sanity check
                assert plan[ exec_index ] == action_list[ action_index ]
                # replan
                curr_state = state_list[ -2 ]
                replan_result = None
                if type( self.planner ) == IPyHOP:
                    plan, exec_index = self.planner.replan( curr_state, exec_index, verbose )
                elif type( self.planner ) == IPyHOP_Old:
                    if not did_replan:
                        preorder_action_nodes = [ *filter( lambda x: self.planner.sol_tree.nodes[ x ][ "type" ] == "A",
                                                       dfs_preorder_nodes( self.planner.sol_tree, source=0 ) ) ]
                        fail_node_id = preorder_action_nodes[ exec_index ]
                    else:
                        fail_node_id = plan_node_ids[ exec_index  ]
                    assert self.planner.sol_tree.nodes[ fail_node_id ][ "info" ] == action_list[ action_index ]
                    replan_result = self.planner.replan( curr_state, fail_node_id, verbose )
                    replan_result = plan, plan_node_ids
                    exec_index = 0
                else:
                    raise( ValueError( "Invalid Planner" ) )
                did_replan = True

                if replan_result is False:
                    plan_impossible = True
                    print( "No Plan Repair Exists")
                    break
                else:
                    if verbose >= 2:
                        print( "New plan is:")
                        print(plan)
        if verbose >= 2 and plan_success:
            print("History:")
            for act in history:
                print(act)
        if plan_impossible:
            return False
        else:
            return history



# ******************************************    Class Declaration End       ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Actor isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
"""
