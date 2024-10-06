import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.scrapers.strategy import Strategy
import twstockanalyzer.scrapers.const as constd


class StrategyTest(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy()

    def test_curve_to_line(self):
        pass

    def test_trend_closer_to_golden_cross_with_diff_increase_case(self):
        # 40均大於138均，開口向上
        src_uptrend_40ma = _np.array(
            [
                39.17,
                39.34,
                39.50,
                39.67,
                39.84,
                40.02,
                40.22,
                40.38,
                40.54,
                40.72,
                40.9,
                41.06,
                41.2,
                41.37,
                41.55,
                41.37,
                41.55,
                41.74,
                41.91,
                42.18,
                42.47,
                42.775,
                43,
            ]
        )
        target_uptrend_138ma = _np.array(
            [
                38.977,
                39.01,
                39.05,
                39.08,
                39.13,
                39.17,
                39.21,
                39.25,
                39.28,
                39.32,
                39.36,
                39.40,
                39.43,
                39.47,
                39.51,
                39.55,
                39.59,
                39.65,
                39.7,
                39.8,
                39.89,
            ]
        )
        expected_res = {
            "dist_all": 1.61786,
            "dist_first_half": 1.269,
            "dist_last_half": 2.175,
            "dist_last_2_3": 2.24038,
            "dist_last_1_3": 2.64917,
            "dist_last_2_4": 2.741,
        }

        is_closing, desc, res = self.strategy.trend_closer_to_golden_cross(
            src_array=src_uptrend_40ma, target_array=target_uptrend_138ma, window=20
        )
        self.assertEqual(is_closing, False)
        self.assertEqual(desc, {constd.LINE_TREND_STRONG_LEAVING})
        self.assertEqual(res, expected_res)

    def test_trend_closer_to_golden_cross_with_diff_increase_case(self):
        # 40均大於138均，向下交叉
        src_uptrend_40ma = _np.array(
            [
                39.526,
                39.675,
                39.685,
                39.54,
                39.53,
                39.55,
                39.56,
                39.58,
                39.59,
                39.6,
                39.6,
                39.59,
                39.61,
                39.72,
                39.69,
                39.64,
                39.63,
                39.62,
                39.61,
                39.625,
                39.52,
                39.5,
                39.4,
                39.45,
                39.42,
                39.39,
                39.37,
            ]
        )
        target_uptrend_138ma = _np.array(
            [
                37.27,
                37.36,
                37.38,
                37.39,
                37.41,
                37.43,
                37.45,
                37.48,
                37.53,
                37.62,
                37.66,
                37.7,
                37,
                8,
                37.81,
                37.83,
                37.88,
                37.9,
                37.91,
                37.95,
                38,
                38.04,
                38.08,
                38.12,
                38.16,
                38.19,
                38.22,
            ]
        )
        expected_res = {
            "dist_all": 2.37315,
            "dist_first_half": 4.974,
            "dist_last_half": 0.84324,
            "dist_last_2_3": 1.52115,
            "dist_last_1_3": 1.28667,
            "dist_last_2_4": 1.252,
        }

        is_closing, desc, res = self.strategy.trend_closer_to_golden_cross(
            src_array=src_uptrend_40ma, target_array=target_uptrend_138ma, window=20
        )
        self.assertEqual(is_closing, True)
        self.assertEqual(
            desc,
            {constd.LINE_TREND_STRONG_CLOSING_TO_CROSS, constd.LINE_TREND_DOWNWARD},
        )
        self.assertEqual(res, expected_res)

    def test_trend_closer_to_golden_cross_with_cross_upward_case(self):
        # 向上交叉
        src_uptrend_week_5ma = _np.array(
            [
                34.48,
                34,
                34.12,
                33.29,
                32.98,
                33.79,
                33.63,
                34.11,
                34.77,
                34.47,
                34.26,
                33.33,
                33.75,
                34.14,
                35.22,
                35.64,
                36.66,
                37.86,
                39.89,
                41.41,
            ]
        )
        target_uptrend_week_138ma = _np.array(
            [
                40.18,
                40.07,
                39.95,
                39.8,
                39.71,
                39.64,
                39.53,
                39.46,
                39.34,
                39.23,
                39.12,
                39.04,
                38.96,
                38.8,
                38.78,
                38.7,
                38.66,
                38.64,
                38.6,
                38,
            ]
        )
        expected_res = {
            "dist_all": 4.5905,
            "dist_first_half": 5.727,
            "dist_last_half": 3.454,
            "dist_last_2_3": 3.78615,
            "dist_last_1_3": 2.35,
            "dist_last_2_4": 2.108,
        }

        min_len = min(len(src_uptrend_week_5ma), len(target_uptrend_week_138ma))
        is_closing, desc, res = self.strategy.trend_closer_to_golden_cross(
            src_array=src_uptrend_week_5ma,
            target_array=target_uptrend_week_138ma,
            window=min_len,
        )
        self.assertEqual(is_closing, True)
        self.assertEqual(
            desc,
            {
                constd.LINE_TREND_STRONG_CLOSING_TO_CROSS,
                constd.LINE_TREND_CROSS_OVER_UPWARD,
                constd.LINE_TREND_UPWARD,
            },
        )
        self.assertEqual(res, expected_res)

    def test_basic_w_pattern(self):
        line_x = _np.array([1, 2, 3, 4, 5, 6, 7])
        line_y = _np.array([7, 1, 3, 1, 4, 1, 5])
        expected = [(2, 1), (3, 3), (4, 1)]
        result = self.strategy.find_latest_w_pattern(line_x, line_y)
        # convert result to tuples of int for comparison
        result = [(int(x), int(y)) for x, y in result]
        self.assertEqual(result, expected)

    def test_find_latest_w_pattern_with_no_w_pattern(self):
        line_x = _np.array([1, 2, 3, 4, 5, 6])
        line_y = _np.array([3, 4, 3, 2, 1, 0])
        result = self.strategy.find_latest_w_pattern(line_x, line_y)
        self.assertIsNone(result)

    def test_find_latest_w_pattern_with_threshold_effect(self):
        line_x = _np.array([1, 2, 3, 4, 5, 6, 7, 8])
        line_y = _np.array([6, 1, 3, -2, 4, 1, 5])
        result = self.strategy.find_latest_w_pattern(line_x, line_y)
        self.assertIsNone(result)

    def test_is_downtrend_in_prices_ma(self):
        pass

    def test_do_not_touch(self):
        pass

    def test_check_osc_stick_heigh(self):
        data_osc_green_week = {
            "OSC": [-3, -1, 4, 5, 6, 3, 1, -0.4, -1, -0.6, -0.5],
        }
        result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_green_week))
        self.assertEqual(result, {constd.OSC_GREEN_WEEK})

        data_osc_green_strong = {
            "OSC": [-3, -1, 4, 5, 2, 3, 1, -3, -9, -20, -11, -2],
        }
        result = self.strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_strong)
        )
        self.assertEqual(result, {constd.OSC_GREEN_STRONG})

        data_osc_green_consolidation = {
            "OSC": [-3, -1, 4, 5, 6, 3, 1, -1, -3, -4, -1, -2],
        }
        result = self.strategy.check_osc_stick_heigh(
            _pd.DataFrame(data_osc_green_consolidation)
        )
        self.assertEqual(result, {constd.OSC_GREEN_CONSOLIDATION})

        data_osc_red_week = {
            "OSC": [3, 1, -3, -9, -20, -11, -2, 4, 5, 5, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_red_week))
        self.assertEqual(result, {constd.OSC_RED_WEEK})

        data_osc_red_strong = {
            "OSC": [3, 1, -0.4, -1, -0.6, -0.5, 4, 5, 6, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(_pd.DataFrame(data_osc_red_strong))
        self.assertEqual(result, {constd.OSC_RED_STRONG})

        data_osc_red_consolidation = {
            "OSC": [3, 1, -1, -3, -4, -1, -2, 4, 5, 6, 3, 1],
        }
        result = self.strategy.check_osc_stick_heigh(
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
        result = self.strategy.check_osc_stick_heigh(
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
        }
        is_up_trend, result = self.strategy.check_macd_trend(
            _pd.DataFrame(data_do_not_touch)
        )
        self.assertEqual(is_up_trend, False)
        self.assertEqual(result, {constd.MACD_DO_NOT_TOUCH})

    def test_check_uptrend_macd_closing_from_bottom(self):
        pass

    def test_check_uptrend_macd_backtest_in_uptrend(self):
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
        }
        is_up_trend, result = self.strategy.check_macd_trend(
            _pd.DataFrame(data_do_not_touch)
        )
        self.assertEqual(is_up_trend, True)
        self.assertEqual(
            result,
            {constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM, constd.MACD_BACKTEST_IN_UP_TREND},
        )
