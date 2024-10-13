#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

from typing import Optional
import pandas as _pd
import twstockanalyzer.strategy.const as constd

# for child can access parent method
from twstockanalyzer.strategy.base import *


class MovingAverageStrategy(Strategy):
    def __init__(self):
        pass

    # 向下趨勢股票[MA5向下 + 收盤<MA5 + 黑k]
    def do_not_touch(self, df: _pd.DataFrame) -> tuple[bool, str]:
        if not self.check_statistic_column(df):
            return True, "Error: Missing columns when do_not_touch"

        #  check if stock is too new
        if df["Close"].dropna().count() < 50:
            return True, f"not enough data: less than 50 close prices"

        # check valid prices trend
        if (
            df["High"].iloc[-1] < df["MA5"].iloc[-1]
            and df["MA5"].iloc[-1] < df["MA5"].iloc[-2]
            and df["Close"].iloc[-1] < df["MA10"].iloc[-1]
            and df["Close"].iloc[-1] < df["Open"].iloc[-1]
            and df["Close"].iloc[-1] < df["Close"].iloc[-2]
        ):
            return True, "向下趨勢股票[MA5向下 + 最高價<MA5 + 黑k]"

        return False, ""

    def check_ma(self, df: _pd.DataFrame) -> Optional[set[str]]:
        if not self.check_columns_exist(
            df,
            [
                "MA5",
                "MA40",
                "MA138",
            ],
        ):
            print(f"Missing column in check_ma")
            return None

        res_set = set()

        # check 40ma and 138 ma
        ma40_data = df["MA40"].dropna().to_numpy()
        ma138_data = df["MA138"].dropna().to_numpy()
        min_len = min(len(ma40_data), len(ma138_data))
        if min_len < 1:
            print("failed to check_ma due to empty data")
            return res_set

        if df["MA40"].iloc[-1] >= df["MA138"].iloc[-1]:
            res_set.add(constd.MA40_ABOVE_MA138)
        else:
            res_set.add(constd.MA40_BELOW_MA138)

        return res_set

        ma40_is_closing, ma40_res_set, cal_res = False, set(), dict()
        if min_len < 40:
            ma40_is_closing, ma40_res_set, cal_res = self.trend_closer_to_golden_cross(
                src_array=ma40_data, target_array=ma138_data, window=min_len
            )
        else:
            ma40_is_closing, ma40_res_set, cal_res = self.trend_closer_to_golden_cross(
                src_array=ma40_data, target_array=ma138_data, window=40
            )

        if ma40_res_set is None:
            print(
                f"empty res when calculate trend_closer_to_golden_cross between 40ma and 138ma in check_ma: {ma40_is_closing, ma40_res_set, cal_res}"
            )

        if ma40_is_closing:
            if constd.LINE_TREND_LATEST_UPWARD in ma40_res_set:
                if (
                    constd.LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER in ma40_res_set
                    or constd.LINE_SRC_TREND_WEEK_CLOSING_TO_CROSSOVER in ma40_res_set
                ):
                    if constd.LINE_SRC_CROSSOVER_TARGET_UPWARD in ma40_res_set:
                        res_set.add(constd.MA40_CROSS_OVER_MA138_UPWARD)
                    else:
                        res_set.add(constd.MA40_CLOSING_TO_MA138_FROM_BOTTOM)
        else:
            if constd.LINE_TREND_LATEST_UPWARD in ma40_res_set:
                res_set.add(constd.MA40_ABOVE_LEAVING_MA138)

        # # check 5ma and 138 ma
        # if df["MA5"].iloc[-1] >= df["MA138"].iloc[-1]:
        #     res_set.add(constd.MA5_ABOVE_MA138)
        # else:
        #     res_set.add(constd.MA5_BELOW_MA138)

        # is_closing, res_set, _ = self.trend_closer_to_golden_cross(
        #     df["MA5"].dropna().to_numpy(), df["MA138"].dropna().to_numpy()
        # )
        # if is_closing:
        #     pass

        return res_set

    # Ｎ均線扣抵值向上(未來均線向下), Ｎ均線扣抵值向下(未來均線向上彎)
    def find_last_n_pivot_in_previous(self, df: _pd.DataFrame, n_peek: int = 3):
        pass
