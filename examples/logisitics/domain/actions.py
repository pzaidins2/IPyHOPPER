#!/usr/bin/env python
"""
File Description: Logistics (00) actions file. All the actions for Logistics planning domain are defined here.
Derived from: https://github.com/AI-Planning/classical-domains/blob/main/classical/logistics00/domain.pddl

Each IPyHOP action is a Python function. The 1st argument is the current state, and the others are the planning
action's usual arguments. This is analogous to how methods are defined for Python classes (where the first argument
is the class instance). For example, the function "a_pickup(state, b)" implements the planning action for the
task ('a_pickup', b).

The state is described with following properties:
- rigid = dict of properties that should not change
    - type_dict = dict with types as keys and sets of all objects of the corresponding type as values
    - in_city = dict with object as key and city as value where the object is in that city
- at = dict with object as key and location as value where the object is at that location
- inside = dict with object as key and object as value where the first object is inside the second


"""

from ipyhop import Actions
from typing import List, Dict, Set


def load_truck( state, o, t, l, rigid):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    # type check
    if( type_check( [ o, t, l ], ["object", "truck", "location"], type_dict ) ):
        # preconditons
        # t is at l
        # o is at l
        if( at[o] == l and at[t] == l ):
            # effects
            # o is not at l
            # o is in t
            state.at.pop(o)
            state.inside[o] = t
            return state

def load_airplane( state, o, a, l, rigid):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    # type check
    if( type_check( [ o, a, l ], ["object", "airplane", "location"], type_dict ) ):
        # preconditons
        # a is at l
        # o is at l
        if( at[o] == l and at[a] == l ):
            # effects
            # o is not at l
            # o is in a
            state.at.pop(o)
            state.inside[o] = a
            return state

def unload_truck( state, o, t, l, rigid):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    inside = state.inside
    # type check
    if( type_check( [ o, t, l ], ["object", "truck", "location"], type_dict ) ):
        # preconditons
        # t is at l
        # o is in t
        if( at[t] == l and inside[o] == t ):
            # effects
            # o is not in t
            # o is at l
            state.inside.pop(o)
            state.at[o] = l
            return state

def unload_airplane( state, o, a, l, rigid):
    type_dict = rigid[ "type_dict" ]
    at = state.at
    inside = state.inside
    # type check
    if( type_check( [ o, a, l ], ["object", "airplane", "location"], type_dict ) ):
        # preconditons
        # a is at l
        # o is in a
        if( at[t] == l and inside[o] == t ):
            # effects
            # o is not in t
            # o is at l
            state.inside.pop(o)
            state.at[o] = l
            return state

def drive_truck( state, t, l_from, l_to, c, rigid ):
    type_dict = rigid["type_dict"]
    at = state.at
    in_city = state.in_city
    # type check
    if (type_check( [ t, l_from, l_to, c ], [ "truck", "location", "location", "city" ], type_dict ) ):
        # preconditons
        # t is at l_from
        # l_from is in city
        # l_to is in city
        if( at[t] == l_from and in_city[l_from] == c and in_city[l_to] == c ):
            # effects
            # t is now at l_to
            state.at[t] = l_to
            return state

def fly_airplane( state, a, l_from, l_to, rigid ):
    type_dict = rigid["type_dict"]
    at = state.at
    # type check
    if (type_check( [ a, l_from, l_to], [ "airplane", "airport", "airport" ], type_dict ) ):
        # preconditons
        # a is at l_from
        if( at[a] == l_from ):
            # effects
            # a is at l_to
            state.at[a] = l_to
            return state
# Create a IPyHOP Actions object. An Actions object stores all the actions defined for the planning domain.
actions = Actions()
actions.declare_actions( [ load_truck, load_airplane, unload_truck, unload_truck, drive_truck, fly_airplane ] )

p_fail = 0.1
action_probability = {
    "load_truck": [ 1 - p_fail, p_fail ],
    "load_airplane": [ 1 - p_fail, p_fail ],
    "unload_truck": [ 1 - p_fail, p_fail ],
    "unload_airplane": [ 1 - p_fail, p_fail ],
    "drive_truck": [ 1 - p_fail, p_fail ],
    "fly_airplane": [ 1 - p_fail, p_fail ],
}

action_cost = {
    "load_truck": 1,
    "load_airplane": 1,
    "unload_truck": 1,
    "unload_airplane": 1,
    "drive_truck": 1,
    "fly_airplane": 1,
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