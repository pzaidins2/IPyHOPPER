#!/usr/bin/env python
"""
File Description: Openstacks (Propositional) actions file. All the actions for Openstacks planning domain are defined here.
Derived from: https://github.com/shop-planner/plan-repair-icaps2020-htnws/blob/master/problems/openstacks/domain.lisp

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

The state is described with following properties:
- rigid = dict of properties that should not change
    - type_dict = dict with types as keys and sets of all objects of the corresponding type as values
    - includes = dict with orders as keys and set of products needed as values
    - included_in = inverse of includes such that o in included_in[ next( iter( includes[ o ] ) ) ]
    - max_stacks = int for max allowable number of maximum stacks
- made = dict with products as keys and boolean value representing whether product has been made
- busy = boolean value that is True when product in production else False
- making = dict with products as keys and bool indicating whether product is in production as values
- started = dict with orders as keys and bool indicating whether order has open stack as values
- delivered = dict with ( order, product ) as keys and bool representing whether product has been delivered for order as values
- stacks_open = int for number of current open stacks
- shipped = dict with orders as keys and bool indicating whether the order has shipped as values
- waiting = dict with orders as keys and bool indicating whether the order is waiting as values

"""

from ipyhop import Actions
from typing import List, Dict, Set

def make_product( state, p, rigid ):
    type_dict = rigid[ "type_dict" ]
    made = state.made
    started = state.started
    included_in = rigid[ "included_in" ]
    # type check
    if type_check( [ p ], [ "product" ], type_dict ):
        # preconditions
        # p has not been made yet
        # started all orders that contain p
        if not( made[ p ] ) and all( [ started[ o ] for o in included_in[ p ] ] ):
            # effects
            # p is made
            state.made[ p ] = True
            return state

def start_order( state, o, rigid ):
    type_dict = rigid[ "type_dict" ]
    waiting = state.waiting
    stacks_open = state.stacks_open
    max_stacks = rigid[ "max_stacks"]
    # type check
    if type_check( [ o ], [ "order" ], type_dict ):
        # precondtions
        # waiting on order
        # fewer open stacks than the maximum
        if waiting[ o ] and stacks_open < max_stacks:
            # effects
            # no longer waiting for order
            state.waiting[ o ] = False
            # started order
            state.started[ o ] = True
            # open new stack
            state.stacks_open += 1
            return state

def ship_order( state, o, rigid ):
    type_dict = rigid[ "type_dict" ]
    made = state.made
    started = state.started
    stacks_open = state.stacks_open
    includes = rigid[ "includes" ]
    # type check
    if type_check( [ o ], [ "order" ], type_dict ):
        # preconditions
        # order is started
        # all products included in order are made
        # a stack is open
        # print("SHIP")
        # print( o )
        # print( started[ o ] and all( [ made[ p ] for p in includes[ o ] ] ) and stacks_open > 0 )
        if started[ o ] and all( [ made[ p ] for p in includes[ o ] ] ) and stacks_open > 0:
            # effects
            # order is no longer started
            state.started[ o ] = False
            # order is shipped
            state.shipped[ o ] = True
            # an open stack is closed
            state.stacks_open -= 1
            return state

# special replanning action
def reset( state, o, rigid ):
    started = state.started
    shipped = state.shipped
    type_dict = rigid[ "type_dict" ]
    waiting = state.waiting
    # type check
    if type_check( [ o ], [ "order" ], type_dict ):
        # preconditions
        # o is started
        # o is not shipped
        # o is not waiting
        if started[ o ] and not( shipped[ o ] ) and not( waiting[ o ] ):
            # effects
            # o is waiting
            state.waiting[ o ] = True
            # o is not started
            state.started[ o ] = False
            return state

# action that exists for verify-orders to cause failure in plan when missing unshipped orders
def verify_orders( state, multigoal, rigid ):
    shipped = state.shipped
    want_shipped = multigoal.shipped
    need_shipped = { *want_shipped.items() } - { *shipped.items() }
    # print(need_shipped)
    if len( need_shipped ) == 0:
        return state

# Create a IPyHOP Actions object. An Actions object stores all the actions defined for the planning domain.
actions = Actions()
actions.declare_actions( [ make_product, start_order, ship_order, reset, verify_orders ] )

p_fail = 1
action_probability = {
    "make_product": [ 1 - p_fail, p_fail ],
    "start_order": [ 1 - p_fail, p_fail ],
    "ship_order": [ 1 - p_fail, p_fail ],
    "reset": [ 1 - p_fail, p_fail ],
    "verify_orders": [ 1 - p_fail, p_fail ],
}

action_cost = {
    "make_product": 1,
    "start_order": 1,
    "ship_order": 1,
    "reset": 1,
    "verify_orders": 1
}

actions.declare_action_models(action_probability, action_cost)

# ******************************************    Helper Functions            ****************************************** #
# takes list of entities to be type checked, their expected types, and a dict defining the objects for each type
# returns True if all checks are good else False
def type_check( entity_list: List[ str ], type_list: List[ str ], type_dict: Dict[ str, Set[ str ] ] ) -> bool:
    return all( map( lambda x, y: True if x in type_dict[ y ] else False, entity_list, type_list ) )


# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Racetrack Actions isn't implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""