import unittest
import pandas as pd
import numpy as np
import pyximport;
pyximport.install(setup_args={"include_dirs": np.get_include()})
from backtester.backtester_fast import backtest, calc_costs, stats_exposure

class BacktesterTestCase(unittest.TestCase):
    def test_inposition(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)

        for i in range(len(inpos)):
            # Fix: 2016-05-30 Exit bar is not in position
            exp = pd.Series([0, 1, 1, 0, 0, 0, 0, 0, 0, 0])
            self.assertEqual(exp[i], inpos.values[i])

    def test_pnl(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=-1)

        for i in range(len(inpos)):
            exp = pd.Series([0, 0, -1, -1, 0, 0, 0, 0, 0, 0])
            self.assertEqual(exp[i], pl.values[i])

    def test_same_bar_exit(self):
        """
        Entering to position even is we have exit_signal on the same bar
        :return:
        """
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule = pd.Series([0, 1, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)

        for i in range(len(inpos)):
            exp = pd.Series([0, 1, 1, 0, 0, 0, 0, 0, 0, 0])
            self.assertEqual(exp[i], inpos.values[i])







    #########################################################33
    #
    #   New exposure stats testing
    #

    def test_stats_exposure_no_costs(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule = pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)

        equity, statsistics = stats_exposure(data, inpos*1.0, costs=None)

        self.assertEqual(statsistics, {})

        for i in range(len(equity)):
            exp = pd.Series([0, 0, 1, 2, 2, 2, 2, 2, 2, 2])
            self.assertEqual(exp[i], equity.values[i])

    def test_stats_exposure_costs(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)
        costs = pd.DataFrame({'rollover_costs': pd.Series(0.0, index=inpos.index),
                              'transaction_costs': pd.Series(1.0, index=inpos.index)})
        series_df, statsistics = stats_exposure(data, inpos * 1.0, costs=costs)



        for i in range(len(series_df)):
            exp = pd.Series([0, -1, 0, 0, 0, 0, 0, 0, 0, 0])
            self.assertEqual(exp[i], series_df['equity'].values[i])

    def test_stats_exposure_no_costs_2trades(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 1, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)
        equity, statsistics = stats_exposure(data, inpos * 1.0, costs=None)

        for i in range(len(inpos)):
            exp = pd.Series(   [0, 1, 1, 0, 0, 1, 1, 1, 0, 0])
            self.assertEqual(exp[i], inpos.values[i])

        for i in range(len(equity)):
            exp = pd.Series(   [0, 0, 1, 2, 2, 2, 3, 4, 5, 5])
            self.assertEqual(exp[i], equity.values[i])

    def test_stats_exposure_size(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 1, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)
        #equity, statsistics = stats(pl, inpos, positionsize=pd.Series(2, index=inpos.index, dtype=np.float), costs=None)
        equity, statsistics = stats_exposure(data, inpos * 2.0, costs=None)


        for i in range(len(equity)):
            exp = pd.Series([0, 0, 2, 4, 4, 4, 6, 8, 10, 10])
            self.assertEqual(exp[i], equity.values[i])

    def test_stats_exposure_costs_with_position_size(self):
        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule =  pd.Series([0, 0, 0, 1, 0, 0, 0, 0, 1, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)

        costs = pd.DataFrame({'rollover_costs': pd.Series(0.0, index=inpos.index),
                              'transaction_costs': pd.Series(1.0, index=inpos.index)})

        series_df, statsistics = stats_exposure(data, inpos * 2.0, costs=costs)

        for i in range(len(series_df)):
            exp = pd.Series([0, -2, 0, 0, 0, -2, 0, 2, 2, 2])
            self.assertEqual(exp[i], series_df.equity.values[i])

    def test_stats_exposure_1bar_inposition(self):
        inpos = pd.Series([0, 1, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8)

        data = pd.DataFrame({'exo': pd.Series(range(10))}, dtype=np.float)
        costs = pd.DataFrame({'rollover_costs': pd.Series(0.0, index=inpos.index), 'transaction_costs': pd.Series(1.0, index=inpos.index)})
        equity, statsistics = stats_exposure(data, inpos * 1.0, costs=costs)

        for i in range(len(equity)):
            exp = pd.Series([0, -1, -1, -1, -1, -1, -1, -1, -1, -1])
            self.assertEqual(exp[i], equity.values[i])

    #
    #
    #
    #
    def test_stats_exposure_delta(self):
        data = pd.DataFrame({'exo': pd.Series(range(10)), 'delta': pd.Series(np.ones(10)*2)}, dtype=np.float)
        entry_rule = pd.Series([0, 1, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
        exit_rule = pd.Series( [0, 0, 0, 1, 0, 0, 0, 0, 1, 0], dtype=np.uint8)

        pl, inpos = backtest(data, entry_rule.values, exit_rule.values, direction=1)
        equity, statistics = stats_exposure(data, inpos * 1.0, costs=None, extendedstats=True)

        self.assertTrue('delta' in equity)

        delta = equity['delta']

        self.assertEqual(delta[0], 0)
        self.assertEqual(delta[1], 2)
        self.assertEqual(delta[2], 2)
        self.assertEqual(delta[3], 0)
        self.assertEqual(delta[4], 0)
        self.assertEqual(delta[5], 2)
        self.assertEqual(delta[6], 2)
        self.assertEqual(delta[7], 2)
        self.assertEqual(delta[8], 0)
        self.assertEqual(delta[9], 0)

    def test_calc_costs(self):
        #calc_costs(transaction_costs, rollover_costs, prev_exposure, curr_exposure)

        # Usual transaction +2 exposure
        costs = calc_costs(12, 0, 0, 2)
        self.assertEqual(-24, costs)

        # Decrease size +1 exposure
        costs = calc_costs(12, 0, 3, 2)
        self.assertEqual(-12, costs)

        # Rollover event without position change
        costs = calc_costs(12, 24, 3, 3)
        self.assertEqual(-24*3, costs)

        # Rollover event with position change
        costs = calc_costs(12, 24, 3, 2)
        self.assertEqual(-24 * 3 + -12*1, costs)

        # Rollover event with position exit
        costs = calc_costs(12, 24, 3, 0)
        self.assertEqual(-24 * 3 + -12 * 3, costs)




if __name__ == '__main__':
    unittest.main()
