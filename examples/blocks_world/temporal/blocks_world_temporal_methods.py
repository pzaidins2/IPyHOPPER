#!/usr/bin/env python
"""
File Description: methods for temporal variant of blocksworld domain. Actions have duration and may be concurrent
"""

from ipyhop import Methods
methods = Methods()


methods.declare_goal_methods('pos', [gm_move1, gm_get, gm_put])

# ******************************************    Demo / Test Routine         ****************************************** #
if __name__ == '__main__':
    raise NotImplementedError("Test run / Demo routine for Temporal Blocks World not implemented.")

"""
Author(s): Paul Zzaidins
Repository: https://github.com/pzaidins2/IPyHOPPER.git
Organization: University of Maryland at College Park
"""
