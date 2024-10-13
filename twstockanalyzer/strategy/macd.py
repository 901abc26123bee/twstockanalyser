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


class MACDIndicatorStrategy(Strategy):
    def __init__(self):
        pass

    #  MACD 呈上升趨勢
    def check_macd_trend(self, df: _pd.DataFrame) -> tuple[bool, Optional[set[str]]]:
        if not self.check_columns_exist(
            df,
            ["MACD", "OSC", "DIF"],
        ):
            raise ValueError("Error: missing column in check_macd_trend.")
        elif df["MACD"].dropna().count() <= 3:
            print("Error: macd data less then 3")
            return None

        # convert macd curve to line
        x_index, y_macd_line, gradient = _np.ndarray, _np.ndarray, _np.ndarray
        if df["MACD"].dropna().count() < 100:
            x_index, y_macd_line, gradient = self.smooth_with_polyfit(
                df=df, column_name="MACD"
            )
        else:
            x_index, y_macd_line, gradient = self.smooth_to_line(
                df=df, column_name="MACD"
            )

        # check return res
        if x_index is None or y_macd_line is None or gradient is None:
            print(
                "Error: One of the returned variables is None when convert macd curve to line."
            )
            return None
        elif (
            (isinstance(x_index, _np.ndarray) and x_index.size == 0)
            or (isinstance(y_macd_line, _np.ndarray) and y_macd_line.size == 0)
            or gradient.size < 1
        ):
            print(
                "Error: One of the res arrays is empty when convert macd curve to line."
            )
            return None

        macd_trend_set = set()
        is_up_trend = False

        # 檢查 MACD 靠近軸線
        latest_macd_data = df["MACD"].dropna().to_numpy()
        middle_array = _np.zeros(df["MACD"].dropna().count())

        if len(latest_macd_data) > 60:
            latest_macd_data = latest_macd_data[-60:]
            middle_array = middle_array[-60:]

        is_closing_middle, closing_middle_trend_set, _ = (
            self.trend_closer_to_golden_cross(
                latest_macd_data, middle_array, window=len(latest_macd_data)
            )
        )
        if closing_middle_trend_set is None:
            print(
                "Error: failed to trend_closer_to_golden_cross between macd and middle line."
            )
            return None

        # 檢查 MACD 柱狀圖(OSC)
        osc_trend_set = self.check_osc_stick_heigh(df)
        if osc_trend_set is None:
            print("Error: failed to check_osc_stick_heigh.")
            return None

        # 檢查 MACD 線型趨勢
        line_trend_set = self.find_line_pattern_and_trend(
            x_index, y_macd_line, gradient
        )
        if line_trend_set is None:
            print("Error: failed to find_line_pattern_and_trend.")
            return None

        # do not touch condition
        # OSC 強綠柱 + OSC 綠柱範圍長 + macd零軸下 範圍長 + MACD 下降趨勢
        fit_count = 0
        osc_cond_to_check = [constd.OSC_GREEN_STRONG, constd.OSC_GREEN_RANGE_LONG]
        for value in osc_cond_to_check:
            if value in osc_trend_set:
                fit_count += 1
        crossover_cond_check = [constd.LINE_SRC_TREND_STRONG_LEAVING_FROM_TARGET]
        for value in closing_middle_trend_set:
            if value in crossover_cond_check:
                fit_count += 1
        line_trend_check = [
            constd.LINE_TREND_LATEST_DOWNWARD,
            constd.LINE_TREND_DECREASING_BOTTOM,
        ]
        if any(item in line_trend_set for item in line_trend_check):
            fit_count += 1

        last_five_values = df["MACD"].tail(5)
        if fit_count == 4 and (last_five_values < 0).all():
            macd_trend_set.add(constd.MACD_DO_NOT_TOUCH)
            return False, macd_trend_set

        # MACD 零軸上/下
        if df["MACD"].iloc[-1] >= 0:
            macd_trend_set.add(constd.MACD_ABOVE_MIDDLE)
        elif df["MACD"].iloc[-1] < 0:
            macd_trend_set.add(constd.MACD_BELOW_MIDDLE)

        # 從上方/下方靠近軸線
        if is_closing_middle and df["MACD"].iloc[-1] <= 0:
            macd_trend_set.add(constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM)
        if is_closing_middle and df["MACD"].iloc[-1] > 0:
            macd_trend_set.add(constd.MACD_CLOSING_MIDDLE_FROM_ABOVE)

        # 檢查 MACD 趨勢
        if constd.LINE_TREND_LATEST_UPWARD in line_trend_set:
            macd_trend_set.add(constd.MACD_LATEST_UPTREND)
            is_up_trend = True
        elif constd.LINE_TREND_LATEST_DOWNWARD in line_trend_set:
            macd_trend_set.add(constd.MACD_LATEST_DOWNTREND)
        # gradient increase/decease
        if constd.LINE_TREND_UPWARD_AGGRESSIVE in line_trend_set:
            macd_trend_set.add(constd.MACD_UPTREND_AGGRESSIVE)
            is_up_trend = True
        if constd.LINE_TREND_DOWNWARD_AGGRESSIVE in line_trend_set:
            macd_trend_set.add(constd.MACD_DOWNTREND_AGGRESSIVE)
        # backtest
        if constd.LINE_TREND_UPWARD_BACKTEST in line_trend_set:
            macd_trend_set.add(constd.MACD_UPTREND_BACKTEST)
            is_up_trend = True
        elif constd.LINE_TREND_DOWNWARD_BACKTEST in line_trend_set:
            macd_trend_set.add(constd.MACD_DOWNTREND_BACKTEST)

        # find duck
        if self.find_upward_duck(df, "DIF", "MACD"):
            macd_trend_set.add(constd.MACD_DUCK_UP_TREND)

        # unknown
        if len(macd_trend_set) == 0:
            macd_trend_set.add(constd.MACD_UNKNOWN)

        return is_up_trend, macd_trend_set

    # 檢查 MACD 柱狀圖(OSC) 強勢、弱勢、盤整
    def check_osc_stick_heigh(
        self, df: _pd.DataFrame, threshold: int = 2
    ) -> Optional[set[str]]:
        if df["OSC"].dropna().size < 3:
            return None

        local_abs_max = df["OSC"].iloc[-1]
        local_abs_max_previous = 0
        cur = 0
        cur_count = 0
        switch = 0
        local_range_count = 0
        res_set = set()

        # loop through the OSC column backward
        for i in range(
            len(df["OSC"]) - 1, 0, -1
        ):  # Start from the last index to the first
            current_value = df["OSC"].iloc[i]
            previous_value = df["OSC"].iloc[i - 1]
            cur_count += 1
            # check for sign change
            if (previous_value > 0 and current_value < 0) or (
                previous_value < 0 and current_value > 0
            ):
                if switch == 0:
                    local_abs_max = cur
                    local_range_count = cur_count
                    switch = switch + 1
                    cur = 0
                    cur_count = 0
                    continue
                elif switch == 1:
                    local_abs_max_previous = cur
                    switch = switch + 1
                    cur = 0
                    continue
                else:
                    break
            else:
                if abs(cur) < abs(previous_value):
                    cur = previous_value
            # incase only one pivot exist
            if switch == 1:
                local_abs_max_previous = cur

        if local_abs_max < 0:
            if abs(local_abs_max) <= abs(local_abs_max_previous) / threshold:
                res_set.add(constd.OSC_GREEN_WEEK)
            elif abs(local_abs_max) >= abs(local_abs_max_previous) * threshold:
                res_set.add(constd.OSC_GREEN_STRONG)
            else:
                res_set.add(constd.OSC_GREEN_CONSOLIDATION)
            if local_range_count > 20:
                res_set.add(constd.OSC_GREEN_RANGE_LONG)
        elif local_abs_max > 0:
            if abs(local_abs_max) <= abs(local_abs_max_previous) / threshold:
                res_set.add(constd.OSC_RED_WEEK)
            elif abs(local_abs_max) >= abs(local_abs_max_previous) * threshold:
                res_set.add(constd.OSC_RED_STRONG)
            else:
                res_set.add(constd.OSC_RED_CONSOLIDATION)
            if local_range_count > 20:
                res_set.add(constd.OSC_RED_RANGE_LONG)
        return res_set
