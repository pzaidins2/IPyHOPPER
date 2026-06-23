#!/usr/bin/env python
"""
File Description: Openstacks deviations file. All the deviations for Openstack planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/openstacks/deviation-operators.lisp

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

"""

from typing import List, Dict, Set
from examples.satellite.domain.actions import type_check
import random
from functools import partial
from networkx import dfs_preorder_nodes
from copy import deepcopy
import time

# initialization must have original solution plan and a deviation must occur exactly once
class shopfixer_deviation_handler():
    def __init__( self, actions, planner, rigid ):
        self.actions = actions
        self.rigid = rigid
        self.planner = planner
        self.determine_deviation_time = 0
        self.deviation_max = 0
        self.base_probability = 0.1

    def determine_deviation( self, act_tuple, state ):
        start = time.process_time_ns()
        # find all valid deviations in original plan
        # print( act_insts )
        deviation_states = []
        # getting all valid deviation for current state and ation
        for d_operator in self.deviation_operators:
            for d_state in d_operator( act_tuple, state ):
                if d_state is not None:
                    deviation_states.append(d_state)
        self.deviation_state_count = len( deviation_states )
        if self.deviation_state_count > 0:
            chosen_deviation = random.choice( deviation_states )
        else:
            chosen_deviation = None
        self.chosen_deviation = chosen_deviation
        self.deviation_max = max(self.deviation_state_count, self.deviation_max)
        self.determine_deviation_time += time.process_time_ns() - start

    def __call__( self, plan_index, plan, state ):
        # print( (act_tuple, self.chosen_pair[ 0 ]) )
        self.determine_deviation( plan[plan_index], state )
        # regularize deviation possibility
        # we want states with many deviations to be more likely to produce a mutation
        if self.chosen_deviation is None:
            return state
        else:
            # trigger deviation with probability modified by possible deviation
            # we want all deviations over the course of the plan to trigger with equal likelihood
            have_deviation = random.uniform(0,1)
            if have_deviation < self.base_probability * self.deviation_state_count / self.deviation_max:
                return self.chosen_deviation
            else:
                return state


# openstacks deviation handler
class deviation_handler( shopfixer_deviation_handler ):

    def __init__( self, actions, planner, rigid ):
        super().__init__( actions, planner, rigid )
        self.deviation_operators = [
            # original says this can make unfixable plan, but still present and no work around given
            # d_unmake_product,
            d_unship_order
        ]
        self.deviation_operators = [ partial( d_operator, rigid=self.rigid ) for d_operator in
                                     self.deviation_operators ]



def d_unmake_product( act_tuple, state, rigid ):
    made = state.made
    included_in = rigid[ "included_in" ]
    type_dict = rigid[ "type_dict" ]
    products = [ *type_dict[ "product" ] ]
    shipped = state.shipped
    # random product that is made and not shipped is unmade
    # random.shuffle( products )
    for p in products:
        if made[ p ] and all([ not( shipped[ o ] ) for o in included_in[ p ] ] ):
            new_state = state.copy()
            new_state.made[ p ] = False
            yield new_state

def d_unship_order( act_tuple, state, rigid ):
    shipped = state.shipped
    stacks_open = state.stacks_open
    max_stacks = rigid[ "max_stacks" ]
    type_dict = rigid[ "type_dict" ]
    orders = [ *type_dict[ "order" ] ]
    # unship random order
    if stacks_open < max_stacks:
        # random.shuffle( orders )
        for o in orders:
            if shipped[ o ]:
                new_state = state.copy()
                new_state.started[ o ] = False
                new_state.shipped[ o ] = False
                new_state.waiting[ o ] = True
                yield new_state




# ******************************************    Helper Functions            ****************************************** #

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Openstacks Deviations isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""
