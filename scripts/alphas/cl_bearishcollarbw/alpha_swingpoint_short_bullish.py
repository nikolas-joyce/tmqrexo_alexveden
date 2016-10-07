from backtester.costs import CostsManagerEXOFixed
from backtester.strategy import OptParam, OptParamArray
from backtester.swarms.rankingclasses import *
from backtester.swarms.rebalancing import SwarmRebalance
from strategies.strategy_swingpoint import StrategySwingPoint

STRATEGY_NAME = "SwingPoint"

STRATEGY_SUFFIX = 'bullish-sample-'

STRATEGY_CONTEXT = {
    'strategy': {
        'class': StrategySwingPoint,
        'exo_name': 'CL_BearishCollarBW',        # <---- Select and paste EXO name from cell above
        'opt_params': [
                        #OptParam(name, default_value, min_value, max_value, step)
                        OptParamArray('Direction', [-1]),
                        OptParam('sphTreshold', 2, 2, 12, 2),
                        OptParam('splTreshold', 2, 2, 13, 2),
            #bearish_breakout, bearish_failure, bullish_breakout, bullish_failure
                        OptParamArray('RulesIndex', [1]),
                        OptParam('MedianPeriod', 5, 30, 30, 5)
            ],
    },
    'swarm': {
        'members_count': 5,
        'ranking_class': RankerBestWithCorrel(window_size=-1, correl_threshold=0.5),
        'rebalance_time_function': SwarmRebalance.every_friday,

    },
    'costs': {
        'manager': CostsManagerEXOFixed,
        'context': {
            'costs_options': 3.0,
            'costs_futures': 3.0,
        }
    }
}