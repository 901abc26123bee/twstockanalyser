#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

from typing import Optional
import pandas as _pd
import numpy as _np
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
            # 黑k + high below ma
            df["High"].iloc[-1] < df["MA5"].iloc[-1]
            and df["High"].iloc[-1] < df["MA10"].iloc[-1]
            and df["Close"].iloc[-1] < df["Open"].iloc[-1]
            # 底底低
            and df["Close"].iloc[-1] < df["Close"].iloc[-2]
            and df["Close"].iloc[-2] < df["Close"].iloc[-3]
            and df["Close"].iloc[-3] < df["Close"].iloc[-4]
            and df["Open"].iloc[-1] < df["Open"].iloc[-2]
            and df["Open"].iloc[-2] < df["Open"].iloc[-3]
            and df["Open"].iloc[-3] < df["Open"].iloc[-4]
            and df["High"].iloc[-1] < df["High"].iloc[-2]
            and df["High"].iloc[-2] < df["High"].iloc[-3]
            and df["High"].iloc[-3] < df["High"].iloc[-4]
            # macd
            and df["MACD"].iloc[-1] < 0
        ):
            return True, "向下趨勢股票[MA5向下 + 最高價<MA5 + 黑k + macd < 0]"

        return False, ""

    def check_ma_relation(self, df: _pd.DataFrame) -> Optional[set[str]]:
        if not self.check_columns_exist(
            df,
            [
                "MA5",
                "MA40",
                "MA60",  # TODO
                "MA138",
            ],
        ):
            raise ValueError(f"Missing column in check_ma_relation")

        res_set = set()

        # check 40ma and 138 ma
        ma138_data = df["MA138"].dropna().to_numpy()
        ma40_data = df["MA40"].iloc[-len(ma138_data) :].dropna().to_numpy()
        ma5_data = df["MA5"].iloc[-len(ma138_data) :].dropna().to_numpy()

        # check relative positive
        if df["MA40"].iloc[-1] >= df["MA138"].iloc[-1]:
            res_set.add(constd.MATrendEnum.MA40_ABOVE_MA138)
        else:
            res_set.add(constd.MATrendEnum.MA40_BELOW_MA138)
        if df["MA5"].iloc[-1] >= df["MA138"].iloc[-1]:
            res_set.add(constd.MATrendEnum.MA5_ABOVE_MA138)
        else:
            res_set.add(constd.MATrendEnum.MA5_BELOW_MA138)
        if df["MA5"].iloc[-1] >= df["MA40"].iloc[-1]:
            res_set.add(constd.MATrendEnum.MA5_ABOVE_MA40)
        else:
            res_set.add(constd.MATrendEnum.MA5_BELOW_MA40)

        # check ma line trend
        ma5_ma138_res = self.check_ma5_to_ma138_cross(ma5_data, ma138_data)
        ma5_ma40_res = self.check_ma5_to_ma40_cross(ma5_data, ma40_data)
        ma40_ma138_res = self.check_ma40_to_ma138_cross(ma40_data, ma138_data)

        # add elements to res_set
        res_set.update(ma5_ma138_res)
        res_set.update(ma5_ma40_res)
        res_set.update(ma40_ma138_res)
        return res_set

    def check_ma5_to_ma138_cross(
        self, ma5_data: _np.ndarray, ma138_data: _np.ndarray
    ) -> Optional[set[str]]:
        min_len = min(len(ma5_data), len(ma138_data))
        if min_len <= 3:
            print("failed to check_ma5_to_ma138_cross due too less data")
            return set()

        valid_closing_from_bottom = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_CLOSING_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_CLOSING_TO_TARGET,
        ]
        valid_leaving_from_above = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_LEAVING_FROM_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_LEAVING_FROM_TARGET,
        ]

        window = min_len
        if window >= 40:
            window = 40
        is_closing, closing_set, _ = self.trend_closer_to_golden_cross(
            src_array=ma5_data, target_array=ma138_data, window=window
        )
        if closing_set is None:
            print(
                f"empty res when calculate trend_closer_to_golden_cross between 5ma and 138ma in check_ma_relation"
            )
            return None

        res_set = set()

        difference = ma5_data[-window:] - ma138_data[-window:]
        positive_count = _np.sum(difference > 0)
        negative_count = _np.sum(difference < 0)
        if is_closing:
            if any(item in closing_set for item in valid_closing_from_bottom):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_CLOSING_TO_MA138_FROM_ABOVE)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_CLOSING_TO_MA138_FROM_BELOW)
            if constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_UPWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA5_CROSS_OVER_MA138_UPWARD)
            elif constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_DOWNWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA5_CROSS_OVER_MA138_DOWNWARD)
        else:
            if any(item in closing_set for item in valid_leaving_from_above):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_ABOVE_LEAVING_MA138)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_BELOW_LEAVING_MA138)

        return res_set

    def check_ma5_to_ma40_cross(self, ma5_data: _np.ndarray, ma40_data: _np.ndarray):
        min_len = min(len(ma5_data), len(ma40_data))
        if min_len <= 3:
            print("failed to check_ma5_to_ma138_cross due too less data")
            return set()

        valid_closing_from_bottom = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_CLOSING_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_CLOSING_TO_TARGET,
        ]
        valid_leaving_from_above = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_LEAVING_FROM_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_LEAVING_FROM_TARGET,
        ]

        window = min_len
        if window >= 40:
            window = 40
        is_closing, closing_set, _ = self.trend_closer_to_golden_cross(
            src_array=ma5_data, target_array=ma40_data, window=window
        )
        if closing_set is None:
            print(
                f"empty res when calculate trend_closer_to_golden_cross between 5ma and 40ma in check_ma_relation"
            )
            return None

        res_set = set()
        difference = ma5_data[-window:] - ma40_data[-window:]
        positive_count = _np.sum(difference > 0)
        negative_count = _np.sum(difference < 0)
        if is_closing:
            if any(item in closing_set for item in valid_closing_from_bottom):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_CLOSING_TO_MA40_FROM_ABOVE)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_CLOSING_TO_MA40_FROM_BELOW)
            if constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_UPWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA5_CROSS_OVER_MA40_UPWARD)
            elif constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_DOWNWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA5_CROSS_OVER_MA40_DOWNWARD)
        else:
            if any(item in closing_set for item in valid_leaving_from_above):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_ABOVE_LEAVING_MA40)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA5_BELOW_LEAVING_MA40)

        return res_set

    def check_ma40_to_ma138_cross(
        self, ma40_data: _np.ndarray, ma138_data: _np.ndarray
    ) -> Optional[set[str]]:
        min_len = min(len(ma40_data), len(ma138_data))
        if min_len <= 3:
            print("failed to check_ma40_to_ma138_cross due too less data")
            return set()

        valid_closing_from_bottom = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_CLOSING_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_CLOSING_TO_TARGET,
        ]
        valid_leaving_from_above = [
            constd.LineCrossOverTrendEnum.SRC_STRONG_LEAVING_FROM_TARGET,
            constd.LineCrossOverTrendEnum.SRC_WEEK_LEAVING_FROM_TARGET,
        ]

        window = min_len
        if window >= 40:
            window = 40
        is_closing, closing_set, _ = self.trend_closer_to_golden_cross(
            src_array=ma40_data, target_array=ma138_data, window=window
        )
        if closing_set is None:
            print(
                f"empty res when calculate trend_closer_to_golden_cross between 40ma and 138ma in check_ma_relation"
            )
            return None

        res_set = set()
        difference = ma40_data[-window:] - ma138_data[-window:]
        positive_count = _np.sum(difference > 0)
        negative_count = _np.sum(difference < 0)
        if is_closing:
            if any(item in closing_set for item in valid_closing_from_bottom):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA40_CLOSING_TO_MA138_FROM_ABOVE)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA40_CLOSING_TO_MA138_FROM_BELOW)
            if constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_UPWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA40_CROSS_OVER_MA138_UPWARD)
            elif constd.LineCrossOverTrendEnum.SRC_CROSS_TARGET_DOWNWARD in closing_set:
                res_set.add(constd.MATrendEnum.MA40_CROSS_OVER_MA138_DOWNWARD)
        else:
            if any(item in closing_set for item in valid_leaving_from_above):
                if positive_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA40_ABOVE_LEAVING_MA138)
                elif negative_count == len(difference):
                    res_set.add(constd.MATrendEnum.MA40_BELOW_LEAVING_MA138)

        return res_set

    def check_ma_trend(self, df: _pd.DataFrame):
        if not self.check_columns_exist(
            df,
            [
                "MA5",
                "MA40",
                "MA60",  # TODO
                "MA138",
            ],
        ):
            raise ValueError(f"Missing column in check_ma_relation")
        pass

    # Ｎ均線扣抵值向上(未來均線向下), Ｎ均線扣抵值向下(未來均線向上彎)
    def find_last_n_pivot_in_previous(self, df: _pd.DataFrame, n_peek: int = 3):
        pass
