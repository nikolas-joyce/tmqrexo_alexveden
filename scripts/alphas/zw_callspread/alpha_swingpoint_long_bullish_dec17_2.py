#
#
#  Automatically generated file 
#        Created at: 2017-01-25 12:25:22.395578
#
from backtester.swarms.rebalancing import SwarmRebalance
from backtester.costs import CostsManagerEXOFixed
from backtester.strategy import OptParamArray
from strategies.strategy_swingpoint import StrategySwingPoint
from backtester.strategy import OptParam
from backtester.swarms.rankingclasses import RankerBestWithCorrel


STRATEGY_NAME = StrategySwingPoint.name

STRATEGY_SUFFIX = "_Bullish_Dec17_2"

STRATEGY_CONTEXT = {
    'strategy': {
        'class': StrategySwingPoint,
        'exo_name': 'ZW_CallSpread',
        'opt_params': [
            OptParamArray('Direction', [1]), 
            OptParam('sphTreshold', 2, 1, 2, 1), 
            OptParam('splTreshold', 2, 3, 3, 1), 
            OptParamArray('RulesIndex', [1, 2]), 
            OptParam('MedianPeriod', 5, 22, 52, 13), 
        ],
    },
    'swarm': {
        'members_count': 1,
        'ranking_class': RankerBestWithCorrel(window_size=-1, correl_threshold=-0.5),
        'rebalance_time_function': SwarmRebalance.every_friday,
    },
    'costs': {
        'context': {
            'costs_futures': 3.0,
            'costs_options': 3.0,
        },
        'manager': CostsManagerEXOFixed,
    },
}
