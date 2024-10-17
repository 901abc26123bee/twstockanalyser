import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.strategy.ma import MovingAverageStrategy
import twstockanalyzer.strategy.const as constd


class MovingAverageStrategyStrategyTest(unittest.TestCase):
    def setUp(self):
        self.ma_strategy = MovingAverageStrategy()

    def test_check_ma_with_ma5_cross_ma138(self):
        ma40_data = [
            77.8,
            77.9,
            78,
            78.2,
            78.4,
            78.5,
            78.65,
            78.82,
            78.9,
            79,
            79.21,
            79.42,
            79.7,
            79.9,
            80,
        ]
        ma138_data = [
            79.04,
            79.05,
            79.05,
            79.04,
            79,
            79.07,
            79,
            79.11,
            79.14,
            79.16,
            79.19,
            79.27,
            79.34,
            79.4,
            79.5,
        ]
        golden_40ma = {
            "MA5": ma40_data,
            "MA40": ma40_data,
            "MA60": ma40_data,
            "MA138": ma138_data,
        }
        self.assertEqual(len(ma40_data), len(ma138_data))
        res_set = self.ma_strategy.check_ma_relation(_pd.DataFrame(golden_40ma))
        self.assertEqual(
            res_set,
            {
                # ma5 ma138
                constd.MATrendEnum.MA5_ABOVE_MA138,
                constd.MATrendEnum.MA5_CROSS_OVER_MA138_UPWARD,
                # ma5 ma40(same array, ignore)
                constd.MATrendEnum.MA5_ABOVE_MA40,
                # ma40 ma138
                constd.MATrendEnum.MA40_ABOVE_MA138,
                constd.MATrendEnum.MA40_CROSS_OVER_MA138_UPWARD,
            },
        )

    def test_check_ma_with_ma5_closing_ma138_without_cross(self):
        ma40_data = [
            77.5,
            77.8,
            77.9,
            78,
            78.2,
            78.4,
            78.5,
            78.65,
            78.82,
            78.9,
            79,
        ]
        ma138_data = [
            79,
            79.04,
            79.05,
            79.05,
            79.04,
            79,
            79.07,
            79,
            79.11,
            79.14,
            79.16,
        ]
        golden_40ma = {
            "MA5": ma40_data,
            "MA40": ma40_data,
            "MA60": ma40_data,
            "MA138": ma138_data,
        }
        self.assertEqual(len(ma40_data), len(ma138_data))
        res_set = self.ma_strategy.check_ma_relation(_pd.DataFrame(golden_40ma))
        self.assertEqual(
            res_set,
            {
                # ma5 ma138
                constd.MATrendEnum.MA5_BELOW_MA138,
                constd.MATrendEnum.MA5_CLOSING_TO_MA138_FROM_BELOW,
                # ma5 ma40(same array, ignore)
                constd.MATrendEnum.MA5_ABOVE_MA40,
                # constd.MATrendEnum.MA5_CLOSING_TO_MA138_FROM_BELOW,
                # ma40 ma138
                constd.MATrendEnum.MA40_BELOW_MA138,
                constd.MATrendEnum.MA40_CLOSING_TO_MA138_FROM_BELOW,
            },
        )

    def test_check_ma_with_ma5_below_leaving_ma138(self):
        ma40_data = [
            77,
            76.04,
            75.5,
            75.1,
            74.04,
            74,
            73.7,
            73.5,
            73.11,
            72.4,
            71.16,
        ]
        ma138_data = [
            77.5,
            77.8,
            77.9,
            78,
            78.2,
            78.4,
            78.5,
            78.65,
            78.82,
            78.9,
            79,
        ]
        golden_40ma = {
            "MA5": ma40_data,
            "MA40": ma40_data,
            "MA60": ma40_data,
            "MA138": ma138_data,
        }
        self.assertEqual(len(ma40_data), len(ma138_data))
        res_set = self.ma_strategy.check_ma_relation(_pd.DataFrame(golden_40ma))
        self.assertEqual(
            res_set,
            {
                # ma5 ma138
                constd.MATrendEnum.MA5_BELOW_MA138,
                constd.MATrendEnum.MA5_BELOW_LEAVING_MA138,
                # ma5 ma40(same array, ignore)
                constd.MATrendEnum.MA5_ABOVE_MA40,
                # ma40 ma138
                constd.MATrendEnum.MA40_BELOW_MA138,
                constd.MATrendEnum.MA40_BELOW_LEAVING_MA138,
            },
        )

    def test_check_ma_with_ma5_above_leaving_ma138(self):
        ma40_data = [
            77.5,
            77.8,
            77.9,
            78,
            78.2,
            78.4,
            78.5,
            78.65,
            78.82,
            78.9,
            79,
        ]
        ma138_data = [
            77,
            76.04,
            75.5,
            75.1,
            74.04,
            74,
            73.7,
            73.5,
            73.11,
            72.4,
            71.16,
        ]
        golden_40ma = {
            "MA5": ma40_data,
            "MA40": ma40_data,
            "MA60": ma40_data,
            "MA138": ma138_data,
        }
        self.assertEqual(len(ma40_data), len(ma138_data))
        res_set = self.ma_strategy.check_ma_relation(_pd.DataFrame(golden_40ma))
        self.assertEqual(
            res_set,
            {
                # ma5 ma138
                constd.MATrendEnum.MA5_ABOVE_MA138,
                constd.MATrendEnum.MA5_ABOVE_LEAVING_MA138,
                # ma5 ma40(same array, ignore)
                constd.MATrendEnum.MA5_ABOVE_MA40,
                # ma40 ma138
                constd.MATrendEnum.MA40_ABOVE_MA138,
                constd.MATrendEnum.MA40_ABOVE_LEAVING_MA138,
            },
        )

    def test_is_downtrend_in_prices_ma(self):
        pass

    def test_do_not_touch(self):
        pass
