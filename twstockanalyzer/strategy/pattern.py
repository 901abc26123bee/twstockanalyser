#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

import pandas as _pd
import numpy as _np

# for child can access parent method
from twstockanalyzer.strategy.base import *


class StrategyPattern(Strategy):
    def __init__(self):
        pass

    # 月、週 呈高檔鈍化
    def high_end_stagnation_in_month_and_week_kd(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(
                f"Error: Missing columns when high_end_stagnation_in_month_and_week_kd"
            )
            return

        df[""] = _np.abs(df["K9"] - df["D9"])

    # 強勢股拉回(日)：MACD 紅柱＋零軸上
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

    # 打N(突破零軸回測)
    def zero_line_breakout_backtest(self, df: _pd.DataFrame):
        pass

    # 月線低檔爆量，上影線
    def high_volume_at_low_prices_level(self, df: _pd.DataFrame):
        max_volume = 0
        max_index = 0
        for i, row in df:
            if row["Volume"] > max_volume:
                max_volume = row["Volume"]
                max_index = i

        # if max_index > 5 and max_index < df["Volume"].dropna().count():
