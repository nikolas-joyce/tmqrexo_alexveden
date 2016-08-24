import numpy as np
import pandas as pd
import pickle
import os
from ast import literal_eval

class Swarm:
    def __init__(self, context):
        """
        Initialize picking engine with context
        :param context: dict(), strategy setting context
        :return:
        """
        self.context = context
        self.global_filter = None
        self._rebalancetime = None

        self._swarm = None
        self._swarm_stats = None
        self._swarm_inposition = None

        self._picked_swarm = None
        self._picked_inposition = None
        self._picked_exposure = None

        self._last_date = None
        self._last_exoquote = None
        self._last_exposure = None
        self._last_members_list = None
        self._last_rebalance_date = None

        self._equity = None

        strategy_settings = self.context['strategy']
        # Initialize strategy class
        self.strategy = strategy_settings['class'](self.context)

    def run_swarm(self):
        # Run strategy swarm
        self._swarm, self._swarm_exposure, self._swarm_inposition = self.strategy.run_swarm_backtest()
        #
        # Average swarm multiplied by members_count
        #   for reproduce comparable results 'picked_swarm' vs 'avg_swarm'
        eq_changes = self._swarm.diff()
        self._swarm_avg = eq_changes.mean(axis=1).cumsum() * self.context['swarm']['members_count']

    @property
    def raw_equity(self):
        """
        Raw swarm cumulative equity (average swarm equity)
        :return:
        """
        if self._swarm_avg is None:
            raise ValueError("Run run_swarm() method before access this property")
        return self._swarm_avg

    @property
    def raw_swarm(self):
        """
        Raw swarm equities DataFrame
        :return:
        """
        if self._swarm is None:
            raise ValueError("Run run_swarm() method before access this property")
        return self._swarm

    @property
    def raw_inposition(self):
        """
        Raw swarm inposition flag
        :return:
        """
        if self._swarm_inposition is None:
            raise ValueError("Run run_swarm() method before access this property")
        return self._swarm_inposition

    def raw_exposure(self):
        """
        Raw swarm exposure = PositionSize * Direction * InPosition
        :return:
        """
        if self._swarm_exposure is None:
            raise ValueError("Run run_swarm() method before access this property")
        return self._swarm_exposure

    @property
    def picked_swarm(self):
        """
        Picked swarm equities DataFrame
        :return:
        """
        if self._picked_swarm is None:
            raise ValueError("Run pick() method before access this property")
        return self._picked_swarm

    @property
    def picked_inposition(self):
        """
        Picked swarm InPosition DataFrame
        :return:
        """
        if self._picked_inposition is None:
            raise ValueError("Run pick() method before access this property")
        return self._picked_inposition

    @property
    def picked_exposure(self):
        """
        Picked swarm exposure = PositionSize * Direction * InPosition
        :return:
        """
        if self._picked_exposure is None:
            raise ValueError("Run pick() method before access this property")
        return self._picked_exposure

    @property
    def picked_equity(self):
        """
        Net equity of picked swarm
        :return:
        """
        if self._equity is None:
            raise ValueError("Run pick() method before access this property")
        return self._equity


    @property
    def rebalancetime(self):
        """
        Rebalance time Series
        :return:
        """
        if self._rebalancetime is None:
            raise ValueError("Run pick() method before access this property")
        return self._rebalancetime


    def pick(self):
        """
        Backtesting and swarm picking routine
        :param swarm:
        :return:
        """

        swarm_settings = self.context['swarm']
        nSystems = swarm_settings['members_count']
        rankerclass = swarm_settings['ranking_class']

        self._rebalancetime = swarm_settings['rebalance_time_function'](self._swarm)

        picked_swarm_equity = np.zeros((len(self._swarm), nSystems))
        picked_swarm_inposition = np.zeros((len(self._swarm), nSystems))
        picked_swarm_exposure = np.zeros((len(self._swarm), nSystems))

        swarm_members = None
        swarm_members_next = None
        rebalance_info = []

        #
        # Clear ranking class cache if applicable
        #
        rankerclass.clear()

        for i in range(1, len(self._rebalancetime)):
            if swarm_members is not None and len(swarm_members) > 0:
                # Comment:
                # - get swarm / filter it by picked members columns
                # - Calculate diff() to previous equity values
                # NB this is matrix operation!
                last_swm_eq_change = self._swarm[swarm_members].iloc[i - 1:i + 1].diff().values[-1]

                # - Add swarm's equity change to picked swarm equity
                # NB this is matrix operation!
                picked_swarm_equity[i] = picked_swarm_equity[i-1] + last_swm_eq_change

                # Store picked in position data
                picked_swarm_inposition[i] = self._swarm_inposition[swarm_members].iloc[i].values

                # Store swarm exposure in position data
                picked_swarm_exposure[i] = self._swarm_exposure[swarm_members].iloc[i].values

                swarm_members = swarm_members_next
            else:
                # NB this is matrix operation!
                swarm_members = swarm_members_next
                picked_swarm_equity[i] = picked_swarm_equity[i - 1]

            # == True - to avoid NaN values to pass condition
            if self._rebalancetime[i] == True:
                # To avoid future referencing in ranking functions use slicing
                swm_slice = self._swarm.iloc[:i + 1, :]

                # Pick new ranked swarm members
                #swarm_members, rank_info = ranker_14days(swm_slice, nSystems)
                swarm_members_next, rank_info = rankerclass.rank(swm_slice, nSystems)

                rebalance_info.append({
                    'rebalance_date': self._swarm.index[i],
                    'best_members': swarm_members_next,
                    'rank_info': rank_info
                })

        self._picked_swarm = pd.DataFrame(picked_swarm_equity, self._swarm.index)
        self._picked_inposition = pd.DataFrame(picked_swarm_inposition, self._swarm.index)
        self._picked_exposure = pd.DataFrame(picked_swarm_exposure, self._swarm.index)
        self.rebalance_info = rebalance_info

        # Storing last state values used in online calculations
        self.fill_last_state()

    def fill_last_state(self):
        """
        Store last state values used in online calculations
        :return:
        """
        self._last_exposure = self.picked_exposure.iloc[-1].sum()
        self._last_date = self.picked_swarm.index[-1]
        self._last_members_list = self.rebalance_info[-1]['best_members']
        self._last_rebalance_date = self.rebalance_info[-1]['rebalance_date']
        self._last_exoquote = self.strategy.data['exo'].iloc[-1]
        self._equity = self.picked_swarm.sum(axis=1)

    @property
    def exo_name(self):
        return self.strategy.exoinfo.exo_info['name']

    @property
    def name(self):
        """
        Return swarm manager human-readable name
        Underlying_EXOName_Strategy_Direction
        :return:
        """
        exoname = self.strategy.exoinfo.exo_info['name']
        strategyname = self.strategy.name

        direction_param = self.context['strategy']['opt_params'][0]

        if direction_param.name.lower() != 'direction':
            raise ValueError('First OptParam of strategy must be Direction')

        if len(direction_param.array) == 2:
            direction = 'Bidir'
        else:
            if direction_param.array[0] == 1:
                direction = 'Long'
            elif direction_param.array[0] == -1:
                direction = 'Short'

        suffix = ''
        if 'suffix' in self.context['strategy'] \
                and self.context['strategy']['suffix'] is not None \
                and len(self.context['strategy']['suffix']) > 0:
            suffix = "_" + self.context['strategy']['suffix']

        return '{0}_{1}_{2}{3}'.format(exoname, direction, strategyname, suffix)

    def save(self, directory,  filename=None):
        if not os.path.isdir(directory):
            os.makedirs(directory)

        if filename is None:
            fn = os.path.join(directory, self.name + '.swm')
        else:
            fn = filename

        with open(fn, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename=None, strategy_context=None, directory=''):
        fn = filename

        if strategy_context is not None:
            smgr = Swarm(strategy_context)
            fn = os.path.join(directory, smgr.name()+'.swm')

        with open(fn, 'rb') as f:
            return pickle.load(f)





    @property
    def last_date(self):
        """
        Last date of swarm calculation
        :return:
        """
        if self._last_date is None:
            raise ValueError("Run pick() method before access this property")
        return self._last_date

    @property
    def last_exposure(self):
        """
        Last net exposure of picked swarm
        :return:
        """
        if self._last_exposure is None:
            raise ValueError("Run pick() method before access this property")
        return self._last_exposure

    @property
    def last_exoquote(self):
        """
        Last EXO quote
        :return:
        """
        if self._last_exoquote is None:
            raise ValueError("Run pick() method before access this property")
        return self._last_exoquote

    @property
    def last_members_list(self):
        """
        Last member list for picked swarm
        :return:
        """
        if self._last_members_list is None:
            raise ValueError("Run pick() method before access this property")
        return self._last_members_list

    @property
    def last_rebalance_date(self):
        """
        Last rebalance date
        :return:
        """
        if self._last_rebalance_date is None:
            raise ValueError("Run pick() method before access this property")
        return self._last_rebalance_date


    def laststate_to_dict(self):
        """
        Return last state of swarm for online trading
        for MongoDB saving
        :return:
        """
        state_dict = {
            'last_date': self.last_date,
            'last_exposure': self.last_exposure,
            'last_exoquote': self.last_exoquote,
            'last_members_list': self.last_members_list,
            'last_rebalance_date': self.last_rebalance_date,
            'picked_equity': pickle.dumps(self.picked_equity),
        }
        return state_dict


    def laststate_update(self, exo_price, swarm_exposure):
        """
        Updates last equity, exposure, exo_quote (used for real time run)
        :param exo_price: price series of EXO
        :param swarm_exposure: last net swarm exposure
        :return: None
        """
        if self._equity is None or len(self._equity) <= 1:
            raise ValueError("Improperly initiated error: self._equity is None or len(self._equity) <= 1")

        # 1. Filter exo_price and swarm_exposure >= self.last_date
        _exo_price = exo_price[exo_price.index >= self.last_date]
        _swarm_exposure = swarm_exposure[swarm_exposure.index >= self.last_date]

        if len(_exo_price) != len(_swarm_exposure):
            raise ValueError("len(_exo_price) != len(_swarm_exposure)")


        for i in range(len(_exo_price)):
            # Do sanity checks
            # Check that date index matches
            if _exo_price.index[i] != _swarm_exposure.index[i]:
                raise ValueError("len(_exo_price) != len(_swarm_exposure)")

            # Check that exo_quote is matching in history
            # To avoid calculation mistakes
            if _exo_price.index[i] == self.last_date:
                if _exo_price.values[i] != self.last_exoquote:
                    raise ValueError("New historical EXO price doesn't match the last_exoquote on same day! Is EXO recalculated?")

                # Just ignore same date swarm updates
            else: # Date of EXO price > self.last_date

                # We have new quote data
                # Update equity series with (exo_price[i] - self.last_exoquote) * self.last_exposure

                # Use previous exposure to calculate quotes
                self._equity[_exo_price.index[i]] = self._equity.values[-1] + (_exo_price.values[i] - self.last_exoquote) * self.last_exposure

                # Update self.last_* properties for next loop step
                self._last_exoquote = _exo_price.values[i]
                self._last_date = _exo_price.index[i]
                self._last_exposure = _swarm_exposure.values[i]

    @staticmethod
    def parse_params(members_list):
        """
        Parse alpha-parameters tuple-string from MongoDB
        :param members_list: list of strings with stingified tuples params
        :return: list of tuples (params for alpha strategy)
        """
        return [literal_eval(p.strip()) for p in members_list]

    @staticmethod
    def laststate_from_dict(state_dict, strategy_context):
        """
        Restores last swarm state from dictionary
        :return:
        """
        # TODO: implement load swarm last state from dict (Mongo)
        pass



