#!/usr/bin/env python
"""
File Description: Openstacks methods file. All the methods for Openstacks planning domain are defined here.
Derived from: PyHOP example of Openstacks domain variant as described https://ipg.host.cs.st-andrews.ac.uk/challenge/#challenge
specifcally the sequenced strips ADL no-cost variant

Each IPyHOP method is a Python function. The 1st argument is the current state (this is analogous to Python methods,
in which the first argument is the class instance). The rest of the arguments must match the arguments of the
task that the method is for. For example, the task ('get', b1) has a method "tm_get(state, b1)", as shown below.
"""

from ipyhop import Methods

# ******************************************    Helper Functions                     ********************************* #

def ship_cost_heuristic( included_in, started, includes, made, p ):
    # set of not started orders that includes p
    includes_p_orders = included_in[ p ]
    unstarted_orders = filter( lambda x: not( started[ x ] ), includes_p_orders )
    return order_costs( started, includes, made, unstarted_orders )

def order_costs( started, includes, made, os ):
    # sum of invifdual order costs
    return sum( map( lambda x: order_cost( started, includes, made, x ), os ) )

def order_cost( started, includes, made, o ):
    # product cost, add 1 if order started
    cost = product_cost( includes, made, o )
    if started[ o ]:
        cost += 1
    return cost

def product_cost( includes, made, o ):
    # number of products included in order and not made
    ps = includes[ o ]
    unmade_ps = { *filter( lambda x: not( made[ x ] ), ps ) }
    return len( unmade_ps )

def ready_to_ship( includes, made, o ):
    p_in_o = includes[ o ]
    return all( [ made[ p ] for p in p_in_o ] )

# ******************************************    Methods                     ****************************************** #

# Create a IPyHOP Methods object. A Methods object stores all the methods defined for the planning domain.
methods = Methods()

def mgm_plan( state, multigoal, rigid ):
    shipped = state.shipped
    want_shipped = multigoal.shipped
    need_shipped = { *want_shipped.items() } - { *shipped.items() }
    # if unfulfilled shipments
    if len( need_shipped ) > 0:
        new_multigoal = multigoal.copy()
        new_multigoal.goal_tag = "t_plan_for_goals"
        yield [ ( "t_reset_order_status", ), ( "t_plan_for_goals", new_multigoal  ) ]

methods.declare_multigoal_methods( "mg_plan", [ mgm_plan ] )

def tm_reset_order_status_0( state, rigid ):
    started = state.started
    shipped = state.shipped
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    # reset all orders that are started but not shipped recursively
    for o in orders:
        if started[ o ] and not shipped[ o ]:
            yield [ ( "reset", o ), ( "t_reset_order_status", ) ]

def tm_reset_order_status_1( state, rigid ):
    started = state.started
    # end reset recursion
    if not any( started.values() ):
        yield [ ]

methods.declare_task_methods( "t_reset_order_status", [ tm_reset_order_status_0, tm_reset_order_status_1 ] )

def tm_plan_for_goals_0( state, multigoal, rigid ):
    has_shipped = { *state.shipped.items() }
    want_shipped = { *multigoal.shipped.items() }
    need_shipped = want_shipped - has_shipped
    # recursively ship orders
    if len( need_shipped ) > 0:
        yield [ ( "t_one_step", ), ( "t_plan_for_goals", multigoal ) ]

def tm_plan_for_goals_1( state, multigoal, rigid ):
    has_shipped = { *state.shipped.items() }
    want_shipped = { *multigoal.shipped.items() }
    need_shipped = want_shipped - has_shipped
    # end recursion
    if len( need_shipped ) == 0:
        yield [ ( "verify_orders", multigoal ) ]

methods.declare_task_methods( "t_plan_for_goals", [ tm_plan_for_goals_0, tm_plan_for_goals_1 ] )


def tm_one_step_0( state, rigid ):
    shipped = state.shipped
    includes = rigid[ "includes" ]
    made = state.made
    started = state.started
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    # ship order that has not shipped, is ready to ship, and is started
    for o in orders:
        if not( shipped[ o ] ) and started[ o ] and ready_to_ship( includes, made, o ):
            yield [ ( "shipped", o, True ) ]

def tm_one_step_1( state, rigid ):
    shipped = state.shipped
    includes = rigid[ "includes" ]
    made = state.made
    started = state.started
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    stacks_open = state.stacks_open
    max_stacks = rigid[ "max_stacks" ]
    # repair order if needed and possible
    if stacks_open < max_stacks:
        for o in orders:
            if not( shipped[ o ] ) and not( started[ o ] ) and ready_to_ship( includes, made, o ):
                yield [ ( 'start_order', o ) ]

def tm_one_step_2( state, rigid ):
    shipped = state.shipped
    includes = rigid[ "includes" ]
    made = state.made
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    # check that for all orders, either the order is shipped or there does not exist a product
    # that for that order is included and not made
    if all( [ shipped[ o ] or any( [ not( made[ p ] ) for p in includes[ o ] ] ) for o in orders ] ):
        yield [ ( "t_make_a_product", ) ]

methods.declare_task_methods( "t_one_step", [ tm_one_step_0, tm_one_step_1, tm_one_step_2 ] )

def tm_make_a_product( state, rigid ):
    includes = rigid[ "includes" ]
    included_in = rigid[ "included_in" ]
    started = state.started
    shipped = state.shipped
    made = state.made
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    products = type_dict[ "product" ]
    # filter products to only those that are not made and in unshipped orders
    valid_products = set()
    unshipped_orders = { *filter( lambda x: not( shipped[ x ] ), orders) }
    unmade_products = { *filter( lambda x: not( made[ x ] ), products ) }
    for o in unshipped_orders:
        includes_o = includes[ o ]
        valid_products |= ( unmade_products & includes_o )
        unmade_products -= includes_o
    # sort products by ship cost heuristic
    valid_products = [ *valid_products ]
    valid_products.sort( key=lambda x: ship_cost_heuristic( included_in, started, includes, made, x ) )
    for v_p in valid_products:
        yield [ ( "made", v_p, True ) ]

methods.declare_task_methods( "t_make_a_product", [ tm_make_a_product ] )

def gm_ship_an_order( state, o, val, rigid ):
    shipped = state.shipped
    includes = rigid[ "includes" ]
    made = state.made
    stacks_open = state.stacks_open
    # o is order
    # o is not shipped
    # all p that o includes are made
    # there exists an open stack
    # print( ( "ship_order", o ) )
    # print( shipped[ o ] )
    # print( stacks_open )
    # print( ready_to_ship( includes, made, o ) )
    if not( shipped[ o ] ) and stacks_open > 0 and ready_to_ship( includes, made, o ):
        yield [ ( "ship_order", o ) ]

methods.declare_goal_methods( "shipped", [ gm_ship_an_order ] )

def gm_make_product( state, p, val, rigid ):
    yield [ ( "t_start_orders", p ), ( "make_product", p ) ]

methods.declare_goal_methods( "made", [ gm_make_product ] )

def tm_start_orders_0( state, p, rigid ):
    included_in = rigid[ "included_in" ]
    started = state.started
    # start all orders that include p that are not started
    if( any( not( started[ o ] ) for o in included_in[ p ] )):
        yield [ ( "t_start_an_order_for", p ), ( "t_start_orders", p ) ]

def tm_start_orders_1( state, p, rigid ):
    included_in = rigid[ "included_in" ]
    started = state.started
    # start all orders that include p that are not started
    include_p_orders = included_in[ p ]
    if all( [ started[ o ] for o in include_p_orders ] ):
        yield [ ]

methods.declare_task_methods( "t_start_orders", [ tm_start_orders_0, tm_start_orders_1 ] )

def tm_start_an_order_for( state, p, rigid ):
    max_stacks = rigid[ "max_stacks" ]
    stacks_open = state.stacks_open
    includes = rigid[ "includes" ]
    type_dict = rigid[ "type_dict" ]
    orders = type_dict[ "order" ]
    started = state.started
    for o in orders:
        if not( started[ o ] ) and stacks_open < max_stacks and p in includes[ o ]:
            yield [ ( "start_order", o ) ]

methods.declare_task_methods( "t_start_an_order_for", [ tm_start_an_order_for ] )

# def tm_verify_orders( state, multigoal, rigid ):
#     shipped = state.shipped
#     want_shipped = multigoal.shipped
#     need_shipped = { *want_shipped.items() } - { *shipped.items() }
#     if len( need_shipped ) == 0:
#         yield [ ( "verify_orders", multigoal ) ]
#
# methods.declare_task_methods( "t_verify_orders", [ tm_verify_orders ] )
#
# def ship_products( state, o, val, rigid ):
#     stacks_open = state.stacks_open
#     if stacks_open > 0:
#         yield [ ( "ship_order", o ) ]
#
# methods.declare_goal_methods( "shipped", [ ship_products ] )




"""
Author(s): Paul Zaidins
Repository: https://github.com/pzaidins2/IPyHOP
Organization: University of Maryland at College Park
"""
