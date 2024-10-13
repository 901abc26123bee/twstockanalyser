import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.strategy.macd import MACDIndicatorStrategy
import twstockanalyzer.strategy.const as constd


class MACDStrategyTest(unittest.TestCase):
    def setUp(self):
        self.macd_strategy = MACDIndicatorStrategy()

    def test_check_osc_stick_heigh(self):
        data_osc_green_week = {
            "OSC": [-3, -1, 4, 5, 6, 3, 1, -0.4, -1, -0.6, -0.5],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_week)
        )
        self.assertEqual(result, {constd.OSC_GREEN_WEEK})

        data_osc_green_strong = {
            "OSC": [-3, -1, 4, 5, 2, 3, 1, -3, -9, -20, -11, -2],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_strong)
        )
        self.assertEqual(result, {constd.OSC_GREEN_STRONG})

        data_osc_green_consolidation = {
            "OSC": [-3, -1, 4, 5, 6, 3, 1, -1, -3, -4, -1, -2],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_consolidation)
        )
        self.assertEqual(result, {constd.OSC_GREEN_CONSOLIDATION})

        data_osc_red_week = {
            "OSC": [3, 1, -3, -9, -20, -11, -2, 4, 5, 5, 3, 1],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_red_week)
        )
        self.assertEqual(result, {constd.OSC_RED_WEEK})

        data_osc_red_strong = {
            "OSC": [3, 1, -0.4, -1, -0.6, -0.5, 4, 5, 6, 3, 1],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_red_strong)
        )
        self.assertEqual(result, {constd.OSC_RED_STRONG})

        data_osc_red_consolidation = {
            "OSC": [3, 1, -1, -3, -4, -1, -2, 4, 5, 6, 3, 1],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_red_consolidation)
        )
        self.assertEqual(result, {constd.OSC_RED_CONSOLIDATION})

        data_osc_red_consolidation = {
            "OSC": [
                3,
                1,
                -1,
                -3,
                -7,
                -1,
                -2,
                4,
                5,
                6,
                3,
                1,
                3,
                4,
                5,
                3,
                3,
                4,
                5,
                6,
                7,
                8,
                3,
                2,
                3,
                5,
                1,
                3,
            ],
        }
        result = self.macd_strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_red_consolidation)
        )
        self.assertEqual(
            result, {constd.OSC_RED_CONSOLIDATION, constd.OSC_RED_RANGE_LONG}
        )

    def test_check_uptrend_macd_do_not_touch_data(self):
        data_do_not_touch_array = [
            1,
            2,
            3,
            4,
            3,
            5,
            3,
            4,
            2,
            1,
            -1,
            -2,
            -2,
            -4,
            -4,
            -5,
            -7,
            -6,
            -7,
            -8,
            -6,
            -7,
            -8,
            -6,
            -7,
            -8,
            -11,
            -8,
            -12,
            -13,
            -14,
            -15,
        ]
        data_do_not_touch = {
            "MACD": data_do_not_touch_array,
            "OSC": data_do_not_touch_array,
            "DIF": data_do_not_touch_array,
        }
        is_up_trend, result = self.macd_strategy.check_macd_trend(
            _pd.DataFrame(data_do_not_touch)
        )
        self.assertEqual(len(data_do_not_touch_array), 32)
        self.assertEqual(is_up_trend, False)
        self.assertEqual(result, {constd.MACD_DO_NOT_TOUCH})

    def test_check_uptrend_macd_closing_from_bottom(self):
        pass

    def test_check_uptrend_macd_uptrend_backtest(self):
        backtest_in_uptrend_array = [
            -0.071,
            -0.6,
            -0.051,
            -0.045,
            -0.04,
            -0.035,
            -0.032,
            -0.03,
            -0.029,
            -0.027,
            -0.023,
            -0.018,
            -0.014,
            -0.01,
            -0.006,
            -0.003,
            0.001,
            0.003,
            0.004,
            0.005,
            0.007,
            0.013,
            0.019,
            0.022,
            0.025,
            0.022,
            0.016,
            0.009,
            0.003,
            -0.003,
            -0.006,
            -0.008,
            -0.009,
        ]
        data_do_not_touch = {
            "MACD": backtest_in_uptrend_array,
            "OSC": backtest_in_uptrend_array,
            "DIF": backtest_in_uptrend_array,
        }
        is_up_trend, result = self.macd_strategy.check_macd_trend(
            _pd.DataFrame(data_do_not_touch)
        )
        self.assertEqual(is_up_trend, True)
        self.assertEqual(
            result,
            {
                constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM,
                constd.MACD_UPTREND_BACKTEST,
                constd.MACD_LATEST_DOWNTREND,
                constd.MACD_BELOW_MIDDLE,
            },
        )

    def test_check_uptrend_macd_duck(self):
        pass
