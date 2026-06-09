#!/usr/bin/env python
"""
File Description: File used for definition of TemporalActions Class.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from __future__ import division, print_function

from typing import Any, Callable, Dict, List, Tuple, Union

from ipyhop.actions import Actions
from ipyhop.chronicle import ObjectVarChange, ReferenceChronicle, RestorationTuple

# NEEDS TO BE EXPANDED, PLACEHOLDER FOR TYPE CHECKING
# placeholder for temporal goal which is specified as timepoint and a predicate with its args
# and the bool value it should evaluate to at that timepoint
TemporalGoal = Tuple[ int, str, *Tuple[ Any, ... ], bool ]
# lowest level of method-action hierarchy that declares that a list of predicate-arg-bools happens
# at the timepoint, no logic/search when IPyHOPPER reads this it checks that no contradictions
# are introduced
# extra layer helps with concurrent nature of temporal planning
TemporalSingletonAction = Tuple[ int, List[ ObjectVarChange ] ]
# middle level of hierarchy, corresponds to formalism actions
# the first 3 parameters must be as follows
# 0: the reference chronicle (which will recieve the state deepcopy treatment)
# 1: the value chronicle (which will be passed by reference and uses the reference chronicle to note current
# list start and ends)
# 2: the label of the earliest time point needed for the action
# and returns a tuple with restoration tuple and list of singleton actions if valid ones exist otherwise returns None
TemporalActionOutput = Union[ Tuple[ RestorationTuple, List[ TemporalSingletonAction ] ], None ]
TemporalActionCall = Tuple[ Any, ... ]
TemporalAction = Callable[ [ ReferenceChronicle, RestorationTuple, int, ... ],
TemporalActionOutput ]


# ******************************************    Class Declaration Start     ****************************************** #
class TemporalActions( Actions ):
    """
    Temporal extension/adaptation of Actions

    Each temporal action is of type TemporalAction. It must accept a ReferenceChronicle and a ValueChronicle as the
    first and second arguments respectively. Additional arguments are optional. The return type is TemporalActionOutput.
    None should be returned if an action would induce a contradiction in the chronicle. Otherwise, return the
    RestorationTuple
    (which contains the new reference chronicle and the temporal restoration tuple needed to rollback changes to the
    underlying TemporalNetwork) and the list of TemporalSingletonAction(s) to be applied to the chronicle.

    """

    def __init__(self):
        super().__init__()

    # ******************************        Class Method Declaration        ****************************************** #
    def __str__(self):
        a_str = super().__str__()
        ta_str = a_str.replace( "ACTIONS", "TEMPORAL ACTIONS" )
        return ta_str

    # ******************************        Class Method Declaration        ****************************************** #
    def __repr__(self):
        return self.__str__()

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_temporal_actions(self, temporal_action_lst: List[ TemporalAction ]) -> None:
        """
        Calls declare_actions of parent class
        """
        super().declare_actions( temporal_action_lst )  # type: ignore

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_temporal_action_models(
            self, t_act_prob_dict: Dict[ str, List[ float ] ], t_act_cost_dict: Dict[ str, float ],
    ):
        """
        Calls declare_action_models of parent class
        """
        super().declare_action_models( t_act_prob_dict, t_act_cost_dict )

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_actions(self, action_list):
        raise (ValueError( "Not currently supported for temporal planning" ))

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_action_models(self, act_prob_dict, act_cost_dict):
        raise (ValueError( "Not currently supported for temporal planning" ))


# ******************************************    Class Declaration End       ****************************************** #

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
