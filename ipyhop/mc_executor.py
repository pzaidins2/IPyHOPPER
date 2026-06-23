#!/usr/bin/env python
"""
File Description: File used for definition of monte-carlo plan executor
"""

# ******************************************    Libraries to be imported    ****************************************** #
from typing import List, Union, Tuple, Callable, Optional
from ipyhop.state import State
from ipyhop.actions import Actions
import numpy as np


# ******************************************    Class Declaration Start     ****************************************** #
class MonteCarloExecutor(object):
    def __init__(self, actions: Actions, deviation_handler: Optional[Callable[
        [Tuple[Tuple[str],State]], State]]=None, seed=None):
        self.actions = actions
        self.deviation_handler = deviation_handler
        self.exec_list = None
        if seed is not None:
            np.random.seed(seed)

    # ******************************        Class Method Declaration        ****************************************** #
    def execute( self, state: State, plan: List[str], actions: Union[Actions, None] = None,  ) -> List[Tuple]:
        self.actions = actions if actions is not None else self.actions
        self.exec_list = [(None, state.copy())]
        deviation_handler = self.deviation_handler
        state_copy = state.copy()
        for i, act_inst in enumerate( plan ):
            # print(act_inst)
            act_name = act_inst[0]
            act_params = act_inst[1:]
            act_func = self.actions.action_dict[act_name]
            act_prob = self.actions.action_prob[act_name]
            result = np.random.choice(len(act_prob), 1, p=act_prob)[0]
            result_state = None
            if result == 0:
                result_state = act_func(state_copy, *act_params)
            else:
                if deviation_handler is not None:
                    deviation_state = deviation_handler( i, plan, state_copy )
                    # print(self.exec_list)
                    self.exec_list[ -1 ] = (self.exec_list[ -1 ][ 0 ], deviation_state)
                    result_state = act_func( deviation_state, *act_params )
            self.exec_list.append( (act_inst, result_state) )
            if result_state is None:
                return self.exec_list
            state_copy = result_state.copy()
        return self.exec_list


# ******************************************    Class Declaration End       ****************************************** #
# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for MonteCarloExecutor isn't implemented.")

"""
Author(s): Yash Bansod
Repository: https://github.com/YashBansod/IPyHOP
"""
