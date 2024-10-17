import unittest
import pandas as _pd
import numpy as _np
from twstockanalyzer.strategy.base import Strategy
from twstockanalyzer.strategy.plot import StrategyPlot
from twstockanalyzer.strategy.macd import MACDIndicatorStrategy
from twstockanalyzer.strategy.pattern import StrategyPattern
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.scrapers.analytics import Analysis

import twstockanalyzer.strategy.const as constd


class StrategyPatternTest(unittest.TestCase):
    def setUp(self):
        self.strategy = Strategy()
        self.plotter = StrategyPlot()
        self.loader = PriceHistoryLoader()
        self.analytics = Analysis()
        self.macdstratrgy = MACDIndicatorStrategy()
        self.pattern = StrategyPattern()
        # run "python -m unittest discover -s tests/strategy" at the root of project twstockanalyzer
        folder_path = "./tests/strategy/data/周主升段/"
        df_dict = self.loader.load_from_downloaded_csv(folder_path)
        # 4576_week
        self.week_4576 = df_dict["4576_week"]
        self.analytics.macd(self.week_4576)
        self.analytics.stochastic(self.week_4576)
        self.analytics.moving_average(self.week_4576, "MA5", 5)
        self.analytics.moving_average(self.week_4576, "MA40", 40)
        self.analytics.moving_average(self.week_4576, "MA60", 60)
        self.analytics.moving_average(self.week_4576, "MA138", 138)
        # 1595_week
        self.week_1595 = df_dict["1595_week"]
        self.analytics.macd(self.week_1595)
        self.analytics.stochastic(self.week_1595)

    # 有初升段 data
    def test_match_macd_first_uptrend_phase_pattern_with_pattern_match_data(self):
        pass

    # 無初升段 data
    def test_match_macd_first_uptrend_phase_pattern_with_pattern_mismatch_data(self):
        pass

    # 有主升段 data
    def test_match_macd_second_main_uptrend_phase_pattern_with_pattern_match_data(self):
        pass

    # 無主升段 data
    def test_match_macd_second_main_uptrend_phase_pattern_with_pattern_mismatch_data(
        self,
    ):
        pass

    def test_valid_long_period_pattern_to_protect_short_period(self):
        pass
