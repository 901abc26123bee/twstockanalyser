import unittest
import pandas as _pd
from twstockanalyzer.scrapers.strategy import Strategy
import twstockanalyzer.scrapers.const as constd


class StrategyTest(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy()

    def test_curve_to_line(self):
        pass

    def test_trend_closer_to_golden_cross(self):
        pass

    def test_find_latest_w_pattern(self):
        pass

    def test_is_downtrend_in_prices_ma(self):
        pass

    def test_check_osc_stick_heigh(self):
        # data_osc_green_week = {
        #     "OSC": [-3, -1, 4, 5, 6, 3, 1, -0.4, -1, -0.6, -0.5],
        # }
        # result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_green_week))
        # self.assertEqual(result, constd.OSC_GREEN_WEEK)

        data_osc_green_strong = {
            "OSC": [-3, -1, 4, 5, 2, 3, 1, -3, -9, -20, -11, -2],
        }
        result = self.strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_strong)
        )
        self.assertEqual(result, constd.OSC_GREEN_STRONG)

        data_osc_green_consolidation = {
            "OSC": [-3, -1, 4, 5, 6, 3, 1, -1, -3, -4, -1, -2],
        }
        result = self.strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_consolidation)
        )
        self.assertEqual(result, constd.OSC_GREEN_CONSOLIDATION)

        data_osc_red_week = {
            "OSC": [3, 1, -3, -9, -20, -11, -2, 4, 5, 5, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_red_week))
        self.assertEqual(result, constd.OSC_RED_WEEK)

        data_osc_red_strong = {
            "OSC": [3, 1, -0.4, -1, -0.6, -0.5, 4, 5, 6, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_red_strong))
        self.assertEqual(result, constd.OSC_RED_STRONG)

        data_osc_red_consolidation = {
            "OSC": [3, 1, -1, -3, -4, -1, -2, 4, 5, 6, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_red_consolidation)
        )
        self.assertEqual(result, constd.OSC_RED_CONSOLIDATION)
