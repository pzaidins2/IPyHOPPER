#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""
from itertools import product
from typing import Iterator, List, Union, cast

from examples.blocks_world.temporal.blocks_world_temporal_actions import (Block, ClearGoal, IsOnGoal,
    MoveBlockToBlockCall, MoveBlockToTableCall,
    Surface, Table, )
from ipyhop import (ChronicleInterface, ObjectVarChange, ObjectVarPersistence, ReferenceChronicle, RestorationTuple,
    TemporalActionCall, TemporalConstraint, TemporalGoal, TemporalMethod, TemporalMethodOutput, TemporalMethods,
    TemporalNetwork, TemporalRestorationTuple, ValueChronicle)

CI = ChronicleInterface()
temporal_methods_instance = TemporalMethods()


# is_on goal can be achieved by single move at t_now
# block on doing goal until t_e
# move block to surface_0 from surface_1
def tgm_is_on_single_now(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: IsOnGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    surface_0 = temporal_goal[ 3 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    assert predicate == "is_on" and bool_val == True
    # object constraints
    # force (t_0 is_on block_0, surface_1)
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    blocks_lst: List[ Surface ] = value_chronicle.domain_objects[ "blocks" ]
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    t_now = reference_chronicle.t_ordered[ -1 ]
    # t_0 = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    # temporal constraints
    if t_e == t_now:
        return
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_e, "==", t_now, 1),
    ]
    # change assertions
    change_assertion_lst: List[ ObjectVarChange ] = [ ]
    print( reference_chronicle )
    for surface_1 in surface_lst:
        if CI.verify_object_assertion_list(
                reference_chronicle, value_chronicle, [
                    (t_now, "is_on", block_0, surface_1, True),
                    (t_now, "clear", block_0, True),
                    (t_now, "clear", surface_0, True),
                ],
        ):
            # persistence assertions
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                # block_0 must be clear for the entire action
                (t_now, t_e, "clear", block_0, True),
                # surface_0 must be clear at the start
                (t_now, t_now, "clear", surface_0, True),
                # blocks cannot be on more than one surface for a single time point
                # nor can they have more than one block on themselves
                (t_now, t_now, "is_on", block_0, surface_1, True),
                (t_e, t_e, "is_on", block_0, surface_0, True),
                *[ (t_now, t_now, "is_on", block_0, x, False) for x in
                    filter( lambda y: y != surface_1, surface_lst ) ],
                *[ (t_e, t_e, "is_on", block_0, x, False) for x in filter( lambda y: y != surface_0, surface_lst ) ],

            ]
            # only the table can have multiple objects on it
            if surface_1 != table:

                persistence_assertion_lst.extend(
                        [
                            *[ (t_now, t_now, "is_on", x, surface_1, False) for x in
                                filter( lambda y: y != block_0, blocks_lst ) ],

                        ],
                )
            if surface_0 != table:
                persistence_assertion_lst.extend(
                        [
                            *[ (t_e, t_e, "is_on", x, surface_0, False) for x in
                                filter( lambda y: y != block_0, blocks_lst ) ],

                        ],
                )
            # all different check
            obj_lst: List[ Surface ] = [ block_0, surface_1, surface_0 ]
            # action call changes based on ending on block or table
            if surface_0 == table:
                action_call = (
                    "move_block_to_table",
                    (t_now, t_e),
                    block_0,
                    surface_1,
                )
                action_call = cast( MoveBlockToTableCall, action_call )
            else:
                action_call = (
                    "move_block_to_block",
                    (t_now, t_e),
                    block_0,
                    surface_1,
                    surface_0,

                )
                action_call = cast( MoveBlockToBlockCall, action_call )
            if len( set( obj_lst ) ) == len( obj_lst ):
                # initialize rollback data structures
                temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
                change_update_dict = { }
                persistence_update_dict = { }
                new_reference_chronicle = reference_chronicle.copy()
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
                ):
                    # define list of subgoals

                    subgoal_lst: List[ Union[ MoveBlockToTableCall, MoveBlockToBlockCall, ClearGoal, IsOnGoal ] ] = [
                        action_call,
                    ]
                    restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # break


# is_on recursive method
# t is_on block_0 surface_0

# t_minus_one block_0 is on some surface_1
# clear block_0 and surface_0 and move block_0 to surface_0
def tgm_is_on_recurse(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: IsOnGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    surface_0 = temporal_goal[ 3 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    assert predicate == "is_on" and bool_val == True
    t_s = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    t_now: int = reference_chronicle.t_ordered[ -1 ]
    # object constraints
    # force (t_s is_on block_0, surface_1)
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    blocks_lst: List[ Surface ] = value_chronicle.domain_objects[ "blocks" ]
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    # temporal constraints
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_e, "==", t_s, 1),
        (t_now, "<", t_s, 0),
    ]
    # change assertions
    change_assertion_lst: List[ ObjectVarChange ] = [ ]
    table_target_flag: bool = table == surface_0
    if True or not CI.verify_object_assertion_list(
            reference_chronicle, value_chronicle, [
                (t_now, "clear", block_0, True),
                (t_now, "clear", surface_0, True),
            ],
    ):
        # persistence assertions
        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
            (t_s, t_e, "clear", block_0, True),
            (t_s, t_s, "clear", surface_0, True),
        ]
        # intializae rollback data structures
        temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
        change_update_dict = { }
        persistence_update_dict = { }
        new_reference_chronicle = reference_chronicle.copy()
        if CI.update_chronicle(
                new_reference_chronicle, value_chronicle, change_assertion_lst,
                persistence_assertion_lst,
                temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
        ):
            # define list of subgoals

            subgoal_lst: List[
                Union[ MoveBlockToTableCall, MoveBlockToBlockCall, ClearGoal, IsOnGoal ] ] = [
                (t_s, "clear", block_0, True),
                (t_s, "clear", surface_0, True),
                (t_e, "is_on", block_0, surface_0, True),
            ]
            restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
            method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
            yield method_output


# clear goal can be achieved by single move at t_now
# clear block_0 by moving block_1 elsewhere
def tgm_clear_single_now(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: ClearGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    assert predicate == "clear" and bool_val == True
    # object constraints
    # force (t_now is_on block_0, surface_1)
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    blocks_lst: List[ Block ] = value_chronicle.domain_objects[ "blocks" ]
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    t_now = reference_chronicle.t_ordered[ -1 ]
    if t_now == t_e:
        return
    # temporal constraints
    temporal_constraint_lst: List[ TemporalConstraint ] = [
        (t_e, "==", t_now, 1),
    ]
    # change assertions
    change_assertion_lst: List[ ObjectVarChange ] = [ ]
    # get block_1 on block_0
    for block_1 in surface_lst:
        if CI.verify_object_assertion_list(
                reference_chronicle, value_chronicle,
                [
                    (t_now, "is_on", block_1, block_0, True),
                    (t_now, "clear", block_1, True),
                ],
        ):
            # find available clear surface
            for surface_0 in surface_lst:
                # all different check
                obj_lst: List[ Surface ] = [ block_0, block_1, surface_0 ]
                if len( set( obj_lst ) ) == len( obj_lst ):
                    if CI.verify_object_assertion_list(
                            reference_chronicle, value_chronicle,
                            [
                                (t_now, "clear", surface_0, True),
                            ],
                    ):
                        # persistence assertions
                        persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                            # block_1 must be clear for the entire action
                            (t_now, t_now, "clear", block_1, True),
                            # surface_0 must be clear at the start
                            (t_now, t_now, "clear", surface_0, True),
                            (t_e, t_e, "clear", block_0, True),
                            # blocks cannot be on more than one surface for a single time point
                            # nor can they have more than one block on themselves
                            (t_now, t_now, "is_on", block_1, block_0, True),
                            (t_e, t_e, "is_on", block_1, surface_0, True),
                            *[ (t_now, t_now, "is_on", block_1, x, False) for x in
                                filter( lambda y: y != block_0, surface_lst ) ],
                            *[ (t_now, t_now, "is_on", x, block_0, False) for x in
                                filter( lambda y: y != block_1, blocks_lst ) ],

                            *[ (t_e, t_e, "is_on", block_1, x, False) for x in
                                filter( lambda y: y != surface_0, surface_lst ) ],
                        ]
                        if surface_0 != table:
                            # only the table can have multiple objects on it
                            persistence_assertion_lst.extend(
                                    [
                                        *[ (t_e, t_e, "is_on", x, surface_0, False) for x in
                                            filter( lambda y: y != block_1, blocks_lst ) ],
                                    ],
                            )
                        # action call changes based on ending on block or table
                        if surface_0 == table:
                            action_call = (
                                "move_block_to_table",
                                (t_now, t_e),
                                block_1,
                                block_0,
                            )
                            action_call = cast( MoveBlockToTableCall, action_call )
                        else:
                            action_call = (
                                "move_block_to_block",
                                (t_now, t_e),
                                block_1,
                                block_0,
                                surface_0,

                            )
                            action_call = cast( MoveBlockToBlockCall, action_call )
                        if len( set( obj_lst ) ) == len( obj_lst ):
                            # intializae rollback data structures
                            temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
                            change_update_dict = { }
                            persistence_update_dict = { }
                            new_reference_chronicle = reference_chronicle.copy()
                            if CI.update_chronicle(
                                    new_reference_chronicle, value_chronicle, change_assertion_lst,
                                    persistence_assertion_lst,
                                    temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                                    change_update_dict=change_update_dict,
                                    persistence_update_dict=persistence_update_dict,
                            ):
                                # define list of subgoals

                                subgoal_lst: List[
                                    Union[ MoveBlockToTableCall, MoveBlockToBlockCall, ClearGoal, IsOnGoal ] ] = [
                                    action_call,
                                ]
                                restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                                method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                                yield method_output


# block on top of clear target must be cleared first
# clear block_0 by moving block_1 elsewhere
def tgm_clear_recurse(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: ClearGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    assert predicate == "clear" and bool_val == True and block_0 != table
    # object constraints
    # force (t_now is_on block_0, surface_1)
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    blocks_lst: List[ Block ] = value_chronicle.domain_objects[ "blocks" ]
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    t_now = reference_chronicle.t_ordered[ -1 ]

    # don't do this method if an immeditate clear is possible
    for block_1 in blocks_lst:
        if CI.verify_object_assertion_list(
                reference_chronicle, value_chronicle,
                [
                    (t_now, "is_on", block_1, block_0, True),
                    (t_now, "clear", block_1, True),
                ],
        ):
            return
    t_s = min_stn.get_n_new_time_point_labels( 1 )[ 0 ]
    # clear block_1 currently on block_0
    for block_1 in blocks_lst:
        if block_1 != block_0:
            if CI.verify_object_assertion_list(
                    reference_chronicle, value_chronicle,
                    [
                        (t_now, "is_on", block_1, block_0, True),
                        (t_now, "clear", block_1, False),
                    ],
            ):
                # temporal constraints
                temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, "==", t_s, 1),
                    (t_now, "<", t_s, 0),
                ]
                # change assertions
                change_assertion_lst: List[ ObjectVarChange ] = [ ]
                # persistence assertions
                persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                    (t_s, t_e, "clear", block_1, True),
                    (t_e, t_e, "clear", block_0, True),
                ]
                # initialize rollback data structures
                temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
                change_update_dict = { }
                persistence_update_dict = { }
                new_reference_chronicle = reference_chronicle.copy()
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst,
                        persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict,
                        persistence_update_dict=persistence_update_dict,
                ):
                    # define list of subgoals

                    subgoal_lst: List[
                        Union[ MoveBlockToTableCall, MoveBlockToBlockCall, ClearGoal, IsOnGoal ] ] = [
                        (t_s, "clear", block_1, True),
                        (t_e, "clear", block_0, True),
                    ]
                    restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output

# progress stack
# given temporal goal (t, "is_on", block_0, surface_0, True ), ensures block_0 is moved from surface_1
# to surface_0
def tgm_progress_stack(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: IsOnGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    surface_0 = temporal_goal[ 3 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    t_0, t_1, t_2, t_e_one_less = min_stn.get_n_new_time_point_labels( 4 )
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    assert predicate == "is_on" and bool_val == True
    # object constraints
    # force (t_s is_on block_0, surface_1)
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    t_s = reference_chronicle.t_ordered[ -1 ]
    for surface_1 in surface_lst:
        # all different check
        obj_lst: List[ Surface ] = [ block_0, surface_1, surface_0 ]
        if len( set( obj_lst ) ) == len( obj_lst ):
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [ ]
            # persistence assertions
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                (t_0, t_e, "clear", block_0, True),
                (t_1, t_e_one_less, "clear", surface_0, True),
                (t_2, t_e_one_less, "is_on", block_0, surface_1, True),
                *[ (t_2, t_e_one_less, "is_on", block_0, x, False) for x in
                    filter( lambda y: y != surface_1, value_chronicle.domain_objects[ "surfaces" ] ) ],
            ]
            # temporal assertions
            for separation_con in ("==", "<"):
                temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, "==", t_e_one_less, 1),
                    (t_s, separation_con, t_0, 0),
                    (t_s, separation_con, t_1, 0),
                    (t_s, separation_con, t_2, 0),
                ]
                temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
                # attempt to add all
                change_update_dict = { }
                persistence_update_dict = { }
                new_reference_chronicle = reference_chronicle.copy()
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
                ):
                    # define list of subgoals
                    # action call changes based on ending on block or table
                    if surface_0 == table:
                        action_call = (
                            "move_block_to_table",
                            (t_e_one_less, t_e),
                            block_0,
                            surface_1,
                        )
                        action_call = cast( MoveBlockToTableCall, action_call )
                    else:
                        action_call = (
                            "move_block_to_block",
                            (t_e_one_less, t_e),
                            block_0,
                            surface_1,
                            surface_0,

                        )
                        action_call = cast( MoveBlockToBlockCall, action_call )
                    subgoal_lst: List[ Union[ MoveBlockToTableCall, MoveBlockToBlockCall, ClearGoal, IsOnGoal ] ] = [
                        (t_0, "is_on", block_0, surface_1, True),
                        (t_0, "clear", block_0, True),
                        (t_1, "clear", surface_0, True),
                        action_call,
                    ]
                    restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)  # type: ignore
                    yield method_output
                    # # if initial success but later failure
                    # CI.restore_chronicle(
                    #         reference_chronicle, value_chronicle, change_update_dict, persistence_update_dict,
                    #         temporal_restoration_tup,
                    # )


# clear block
# clear block_0 by moving block_1 on top of block_0 to be on surface_0
def tgm_clear_block(
        reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle,
        temporal_goal: ClearGoal,
) -> Iterator[ TemporalMethodOutput ]:
    # localize variables
    t_e: int = temporal_goal[ 0 ]
    predicate: str = temporal_goal[ 1 ]
    block_0 = temporal_goal[ 2 ]
    bool_val: bool = temporal_goal[ -1 ]
    min_stn: TemporalNetwork = value_chronicle.temporal_network
    t_0, t_1, t_2, t_e_one_less = min_stn.get_n_new_time_point_labels( 4 )
    assert predicate == "clear" and bool_val == True
    # iterate over all combinations of block_1 and surface_0
    block_lst: List[ Block ] = value_chronicle.domain_objects[ "blocks" ]
    surface_lst: List[ Surface ] = value_chronicle.domain_objects[ "surfaces" ]
    table: Table = value_chronicle.domain_objects[ "table" ][ 0 ]
    t_s = reference_chronicle.t_ordered[ -1 ]
    for block_1, surface_0 in product( block_lst, surface_lst ):
        # object constraints
        obj_lst: List[ Surface ] = [ block_0, block_1, surface_0 ]
        # all different check
        if len( set( obj_lst ) ) == len( obj_lst ):
            # change assertions
            change_assertion_lst: List[ ObjectVarChange ] = [ ]
            # persistence assertions
            persistence_assertion_lst: List[ ObjectVarPersistence ] = [
                (t_2, t_e_one_less, "is_on", block_1, block_0, True),
                *[ (t_2, t_e_one_less, "is_on", block_1, x, False) for x in
                    filter( lambda y: y != block_0, value_chronicle.domain_objects[ "surfaces" ] ) ],
                (t_0, t_e, "clear", block_1, True),
            ]
            for separation_con in ("==", "<"):
                # temporal assertions
                temporal_constraint_lst: List[ TemporalConstraint ] = [
                    (t_e, "==", t_e_one_less, 1),
                    (t_2, "<=", t_0, 0),
                    (t_s, separation_con, t_0, 0),
                    (t_s, separation_con, t_2, 0),
                ]
                if surface_0 != table:
                    persistence_assertion_lst.append( (t_1, t_e_one_less, "clear", surface_0, True) )
                    temporal_constraint_lst.extend(
                            [
                                (t_1, "<=", t_e_one_less, 0),
                                (t_s, separation_con, t_1, 0),
                            ],
                    )
                temporal_restoration_tup: TemporalRestorationTuple = ([ ], [ ], [ ])
                # attempt to add all
                change_update_dict = { }
                persistence_update_dict = { }
                new_reference_chronicle = reference_chronicle.copy()
                if CI.update_chronicle(
                        new_reference_chronicle, value_chronicle, change_assertion_lst, persistence_assertion_lst,
                        temporal_constraint_lst, temporal_restoration_tup=temporal_restoration_tup,
                        change_update_dict=change_update_dict, persistence_update_dict=persistence_update_dict,
                ):
                    # action call changes based on ending on block or table
                    if surface_0 == table:
                        action_call = (
                            "move_block_to_table",
                            (t_e_one_less, t_e),
                            block_1,
                            block_0,
                        )
                        action_call = cast( MoveBlockToTableCall, action_call )
                    else:
                        action_call = (
                            "move_block_to_block",
                            (t_e_one_less, t_e),
                            block_1,
                            block_0,
                            surface_0,
                        )
                        action_call = cast( MoveBlockToBlockCall, action_call )
                    # define list of subgoals
                    subgoal_lst: List[ Union[ TemporalGoal, TemporalActionCall ] ] = [
                        (t_0, "clear", block_1, True),
                        (t_2, "is_on", block_1, block_0, True),
                    ]
                    if surface_0 != table:
                        subgoal_lst.append( (t_1, "clear", surface_0, True) )
                    subgoal_lst.append( action_call )
                    restoration_tup: RestorationTuple = (reference_chronicle, temporal_restoration_tup)
                    method_output: TemporalMethodOutput = (restoration_tup, subgoal_lst)
                    yield method_output
                    # # if initial success but later failure
                    # CI.restore_chronicle(
                    #         reference_chronicle, value_chronicle, change_update_dict, persistence_update_dict,
                    #         temporal_restoration_tup,
                    # )


# move block to table
# def tgm_move_block_to_table(
#         reference_chronicle: ReferenceChronicle, value_chronicle: ValueChronicle, goal: TemporalGoal,
#         block: Block, start_pos: Block,
# ) -> TemporalActionOutput:
#     # initialization
#     persistence_update_dict: Dict[ str, int ] = { }
#     change_update_dict: Dict[ str, int ] = { }
#     t_end: int = goal[ 0 ]
#
#     (t_start,) = value_chronicle.temporal_network.get_n_new_time_point_labels( 1 )
#     # add temporal constraints
#     temporal_constraint_lst: List[ TemporalConstraint ] = [
#         (t_start, "==", t_end, 1),
#     ]
#     success_flag, *temporal_rest_tuple = CI.add_temporal_constraints_from(
#             value_chronicle, temporal_constraint_lst,
#     )
#     if success_flag:
#         # add persistence assertions
#         persistence_assertion_lst: List[ ObjectVarPersistence ] = [
#             (t_start, t_end, "clear", block, True),
#         ]
#         if CI.add_persistences( reference_chronicle, value_chronicle,
#                 persistence_assertion_lst, persistence_update_dict ):
#             return (reference_chronicle, cast( TemporalRestorationTuple, temporal_rest_tuple ))
#
#     CI.restore_chronicle(
#             reference_chronicle, value_chronicle, change_update_dict,
#             persistence_update_dict, temporal_rest_tuple,
#     )


# NEED: Temporal extension of Goal type: has goal predicate name and time point
is_on_methods_lst: List[ TemporalMethod ] = [ tgm_is_on_single_now, tgm_is_on_recurse ]
clear_methods_lst: List[ TemporalMethod ] = [ tgm_clear_single_now, tgm_clear_recurse ]

temporal_methods_instance.declare_temporal_goal_methods( 'is_on', is_on_methods_lst )
temporal_methods_instance.declare_temporal_goal_methods( 'clear', clear_methods_lst )

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Temporal Blocks World not implemented.")

"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
