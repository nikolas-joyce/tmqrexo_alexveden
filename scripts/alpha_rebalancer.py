try:
    from .settings import *
except SystemError:
    from scripts.settings import *

try:
    from .settings_local import *
except SystemError:
    try:
        from scripts.settings_local import *
    except SystemError:
        pass
    pass


import os, sys
import importlib
from backtester.swarms.swarm import Swarm
from backtester.strategy import OptParamArray
from tradingcore.swarmonlinemanager import SwarmOnlineManager

TMQRPATH = os.getenv("TMQRPATH", '')


def get_exo_names():
    exo_names_list = []

    for instrument in INSTRUMENTS_LIST:
        for exo in EXO_LIST:
            print("Processing : " + exo['name'])

            ExoClass = exo['class']
            for exo_name in ExoClass.names_list(instrument):
                exo_names_list.append(exo_name)

    return exo_names_list


def get_exo_names_mat():
    exo_names_list = []

    for file in os.listdir(os.path.join(TMQRPATH, "mat")):
        if 'strategy_' in file and '.mat' in file:
            exo_names_list.append(file)

    return exo_names_list



def main():
    # Getting the list of all EXOs / instruments
    exo_names = get_exo_names_mat()

    for exo in exo_names:
        print("Processing EXO: " + exo)

        # Load alpha modules to process
        for module in os.listdir('alphas'):
            if 'alpha_' in module and '.py' in module:
                m = importlib.import_module('scripts.alphas.{0}'.format(module.replace('.py','')))

                for direction in [-1, 1]:
                    print('Running alpha: ' + m.STRATEGY_NAME + ' Direction: {0}'.format(direction))
                    context = m.STRATEGY_CONTEXT
                    context['strategy']['exo_name'] = exo
                    context['strategy']['opt_params'][0] = OptParamArray('Direction', [direction])
                    context['strategy']['suffix'] = m.STRATEGY_SUFFIX

                    swm = Swarm(context)
                    swm.run_swarm()
                    swm.pick()
                    # Saving results to swarms directory
                    swm.save(os.path.join(TMQRPATH, "swarms"))

                    #
                    # Saving last EXO state to online DB
                    #
                    swmonline = SwarmOnlineManager(MONGO_CONNSTR, MONGO_EXO_DB, m.STRATEGY_CONTEXT)
                    swmonline.save(swm)

if __name__ == '__main__':
    main()
