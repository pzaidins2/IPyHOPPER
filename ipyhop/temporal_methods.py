#!/usr/bin/env python
"""
File Description: File used for definition of TemporalMethods Class.
"""

# ******************************************    Libraries to be imported    ****************************************** #
from __future__ import division, print_function

from typing import Any, Callable, Iterator, List, Tuple, Union

from ipyhop.chronicle import ReferenceChronicle, RestorationTuple, ValueChronicle
from ipyhop.methods import Methods
from ipyhop.temporal_actions import TemporalActionCall, TemporalGoal

# highest level of hierarchy, corresponds to formalism methods
# function given reference and value chronicles and (a temporal goal (t,...) or method call)
# gives an iterator that yields valid pairs of restoration tuples and sublists with temporal goals or
# action calls
TemporalMethodCall = TemporalActionCall
TemporalMethodOutput = Union[ Tuple[ RestorationTuple, List[ Union[ TemporalGoal, TemporalActionCall ] ] ], None ]

TemporalMethod = Callable[
    [ ReferenceChronicle, ValueChronicle, TemporalGoal, *Tuple[ Any, ... ] ],
    Iterator[ TemporalMethodOutput ] ]


# ******************************************    Class Declaration Start     ****************************************** #
class TemporalMethods( Methods ):
    """
    Temporal extension/adaptation of Methods class

    Each temporal method is of type TemporalMethod. It must accept a ReferenceChronicle and a ValueChronicle as the
    first and second arguments respectively. Additional arguments are optional. The return type is
    Iterator[TemporalMethodOutput].
    If no more valid decompositions can be found None is retured. Otherwise, yields the
    RestorationTuple
    (which contains the new reference chronicle and the temporal restoration tuple needed to rollback changes to the
    underlying TemporalNetwork) and the resulting valid decomposition (a list of new subgoals and or calls to temporal
    actions).

    NOTE: Only singular temporal goals are supported unlike the multigoals of nontemporal planning

    """

    def __init__(self):
        super().__init__()

    # ******************************        Class Method Declaration        ****************************************** #
    def __str__(self):
        m_str = super().__str__()
        tm_str = m_str.replace( 'Method', 'Temporal Method' )
        return tm_str

    # ******************************        Class Method Declaration        ****************************************** #
    def __repr__(self):
        return self.__str__()

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_temporal_goal_methods(self, temporal_goal_name: str, temporal_method_list: List[ TemporalMethod ]):
        """
        Marks the listed temporal methods as relevant to the temporal goal named

        :param temporal_goal_name: Name of the temporal goal.
        :param temporal_method_list: List of temporal methods.
        """
        super().declare_goal_methods( temporal_goal_name, temporal_method_list )  # type: ignore

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_task_methods(self, task_name: str, method_list: List[ TemporalMethod ]):
        raise (ValueError( "Not currently supported for temporal planning" ))

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_goal_methods(self, goal_name: str, method_list):
        raise (ValueError( "Not currently supported for temporal planning" ))

    # ******************************        Class Method Declaration        ****************************************** #
    def declare_multigoal_methods(self, multigoal_tag: Union[ None, str ], method_list):
        raise (ValueError( "Not currently supported for temporal planning" ))



# ******************************************    Class Declaration End       ****************************************** #

# **************************************        Function Declaration        ****************************************** #
def _goals_not_achieved(state, multigoal):
    raise (ValueError( "Not currently supported for temporal planning" ))


def mgm_split_multigoal(state, multigoal):
    raise (ValueError( "Not currently supported for temporal planning" ))


"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
