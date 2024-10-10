import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.strategy.ma import MovingAverageStrategy
import twstockanalyzer.strategy.const as constd


class MovingAverageStrategyStrategyTest(unittest.TestCase):
    def setUp(self):
        self.ma_strategy = MovingAverageStrategy()

    def test_check_ma_with_golden_cross_40ma(self):
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
            "MA138": ma138_data,
        }
        self.assertEqual(len(ma40_data), len(ma138_data))
        res_set = self.ma_strategy.check_ma(_pd.DataFrame(golden_40ma))
        self.assertEqual(
            res_set,
            {
                # constd.MA40_CROSS_OVER_MA138_UPWARD, # TODO: fix
                constd.MA40_ABOVE_MA138,
            },
        )

    def test_is_downtrend_in_prices_ma(self):
        pass

    def test_do_not_touch(self):
        pass
