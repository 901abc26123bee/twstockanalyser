import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.strategy.base import Strategy
from twstockanalyzer.strategy.plot import StrategyPlot
from twstockanalyzer.strategy.macd import MACDIndicatorStrategy
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.scrapers.analytics import Analysis

import twstockanalyzer.strategy.const as constd


class StrategyTest(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy()
        self.plotter = StrategyPlot()
        self.loader = PriceHistoryLoader()
        self.analytics = Analysis()
        self.macdstratrgy = MACDIndicatorStrategy()
        # run "python -m unittest discover -s tests/strategy" at the root of project twstockanalyzer
        folder_path = "./tests/strategy/data/周主升段/"
        df_dict = self.loader.load_from_downloaded_csv(folder_path)
        self.week_4576 = df_dict["4576_week"]
        self.analytics.macd(self.week_4576)
        self.week_1595 = df_dict["1595_week"]
        self.analytics.macd(self.week_1595)

    def test_smooth_to_line_with_empty_data(self):
        empty_df = _pd.DataFrame({"test": []})
        with self.assertRaises(ValueError) as context:
            self.strategy.smooth_to_line(empty_df, "test")
        self.assertEqual(
            str(context.exception), "Error: empty data for test column in df."
        )

    def test_smooth_to_line_with_few_data(self):
        few_data_df = _pd.DataFrame({"test": [1, 3, 4, 3, 5, 6]})
        line_x, line_y, gradient = self.strategy.smooth_to_line(few_data_df, "test")
        self.assertEqual(line_x.tolist(), [0, 3, 5])
        self.assertEqual(line_y.tolist(), [1, 3, 6])
        self.assertEqual(gradient.tolist(), [0.666667, 1.5])

    def test_smooth_to_line_with_0_pivot(self):
        pass

    def test_smooth_to_line_with_1_pivot(self):
        pass

    def test_smooth_to_line_with_4_pivot(self):
        pass

    def test_smooth_with_polyfit_with_empty_data(self):
        empty_df = _pd.DataFrame({"test": []})
        with self.assertRaises(ValueError) as context:
            self.strategy.smooth_with_polyfit(empty_df, "test")
        self.assertEqual(
            str(context.exception), "Error: empty data for test column in df."
        )

    def test_smooth_with_polyfit_with_few_data(self):
        pass

    def test_smooth_with_polyfit_with_2_pivot(self):
        pass

    def test_smooth_with_polyfit_with_5_pivot(self):
        pass

    # 40均大於138均，開口向上
    def test_trend_closer_to_golden_cross_with_diff_increase_case(self):
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
        self.assertEqual(desc, {constd.LINE_SRC_TREND_STRONG_LEAVING_FROM_TARGET})
        self.assertEqual(res, expected_res)

    # 40均大於138均，向下交叉
    def test_trend_closer_to_golden_cross_with_diff_in_decrease_case(self):
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
            {constd.LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER},
        )
        self.assertEqual(res, expected_res)

    # 向上、向下交叉
    def test_trend_closer_to_golden_cross_with_cross_upward_and_downward_case(self):
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

        # 向上交叉
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
                constd.LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER,
                constd.LINE_SRC_CROSSOVER_TARGET_UPWARD,
            },
        )
        self.assertEqual(res, expected_res)

        # 向下交叉
        is_closing, desc, res = self.strategy.trend_closer_to_golden_cross(
            src_array=target_uptrend_week_138ma,
            target_array=src_uptrend_week_5ma,
            window=min_len,
        )
        self.assertEqual(is_closing, True)
        self.assertEqual(
            desc,
            {
                constd.LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER,
                constd.LINE_SRC_CROSSOVER_TARGET_DOWNWARD,
            },
        )

    def test_find_latest_w_pattern_with_basic_w_pattern(self):
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

    def test_find_latest_pivots(self):
        array_1 = _np.array([1, 3, 2, 4, 3, 5, 4, 6, 5])

        array_2 = _np.array([4, 2, 3, 1, 2, -1, 0, -2, -1, 1])

        array_no_pivot = _np.array([1, 2, 3, 4, 5, 6, 7, 8])

        result = self.strategy.find_latest_pivots(array_1, "peak", count=2)
        expected = (5, 6)  # Last two peaks in (3,4,5,6)
        self.assertEqual(result, expected)

        result = self.strategy.find_latest_pivots(array_2, "bottom", count=4)
        expected = (2, 1, -1, -2)  # Last two bottoms
        self.assertEqual(result, expected)

        result = self.strategy.find_latest_pivots(array_2, "peak", count=10)
        expected = (3, 2, 0, 1)  # exceed all peaks
        self.assertEqual(result, expected)

        result = self.strategy.find_latest_pivots(array_no_pivot, "peak", count=10)
        expected = (
            8,
        )  # peak is the latest one, add comma at that to ensure type is tuple
        self.assertEqual(result, expected)

    def test_find_line_pattern_and_trend_with_upward_and_downward_backtest(self):
        # upward backtest
        line_x = [0, 40, 61, 90, 99]
        line_y = [-3.76937961, -0.545905, -2.86110231, 2.10143704, 1.99982711]
        gradients = [0.080587, -0.110247, 0.171122, -0.01129]
        result = self.strategy.find_line_pattern_and_trend(line_x, line_y, gradients)
        self.assertEqual(
            result,
            {
                constd.LINE_TREND_INCREASING_BOTTOM,
                constd.LINE_TREND_UPWARD_BACKTEST,
                constd.LINE_TREND_LATEST_DOWNWARD,
            },
        )

        # downward backtest
        line_x_1 = [0, 18, 30, 47, 58, 80, 108, 131, 151]
        line_y_1 = [
            -0.000154955751,
            0.335040982,
            -4.23877982,
            1.04810715,
            -0.304706691,
            18.9963800,
            -5.36329941,
            -0.6746890,
        ]
        gradients_1 = [
            0.018622,
            -0.381152,
            0.310993,
            -0.122983,
            0.877322,
            -0.869989,
            0.203853,
        ]

        result = self.strategy.find_line_pattern_and_trend(
            line_x_1, line_y_1, gradients_1
        )
        self.assertEqual(
            result,
            {
                constd.LINE_TREND_DECREASING_BOTTOM,
                constd.LINE_TREND_DOWNWARD_BACKTEST,
                constd.LINE_TREND_LATEST_UPWARD,
            },
        )

    def test_find_line_pattern_and_trend_with_uptrend_and_downtrend_aggressive(self):
        pass

    def test_find_line_pattern_and_trend_with_uptrend_and_downtrend_slowdown(self):
        pass

    def test_find_duck_with_duck_exist_data(self):
        d9_data = [18.543, 15.931, 17.949, 23.62, 26.858, 31.347]
        k9_data = [11.917, 10.7, 21.98, 34.96, 33.36, 40.323]
        data_with_duck = {
            "K9": k9_data,
            "D9": d9_data,
        }
        res = self.strategy.find_upward_duck(_pd.DataFrame(data_with_duck), "K9", "D9")
        self.assertEqual(res, True)

    def test_find_duck_with_no_duck_data(self):
        pass

    # python -m unittest tests.strategy.test_base.StrategyTest.test_plot_macd
    # def test_plot_macd(self):
    #     # self.plotter._draw_macd_curve_to_line(self.week_4576, "MACD")
    #     # trimmed_df = self.week_4576.tail(100).reset_index(drop=True)
    #     # self.plotter._draw_macd_curve_to_line(trimmed_df, "MACD")

    #     # self.plotter._draw_macd_curve_to_line(self.week_1595, "MACD")
    #     trimmed_df = self.week_4576.tail(60).reset_index(drop=True)
    #     self.plotter._draw_macd_curve_to_line(trimmed_df, "MACD")
