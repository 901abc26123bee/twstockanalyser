#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt
from typing import List
from scipy.signal import find_peaks, butter, filtfilt
from fastdtw import fastdtw
import warnings
from numpy.exceptions import RankWarning
import twstockanalyzer.scrapers.const as constd


class Strategy:
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

    # 月線低檔爆量，上影線
    def high_volume_at_low_prices_level(self, df: _pd.DataFrame):
        max_volume = 0
        max_index = 0
        for i, row in df:
            if row["Volume"] > max_volume:
                max_volume = row["Volume"]
                max_index = i

        # if max_index > 5 and max_index < df["Volume"].dropna().count():

    def check_ma(self, df: _pd.DataFrame) -> tuple:
        if not self.check_statistic_column(df):
            return False, f"Error: Missing columns when check_uptrend_macd"

    #  MACD 呈上升趨勢
    def check_uptrend_macd(self, df: _pd.DataFrame) -> tuple[bool, str]:
        if not self.check_statistic_column(df):
            return False, f"Error: Missing columns when check_uptrend_macd"

        # convert line to curve
        x_index, y_macd_line, gradient = self.smooth_to_line(df, "MACD", 0.4)

        # check return res
        if x_index is None or y_macd_line is None or gradient is None:
            return (
                False,
                f"One of the returned variables is None when convert macd curve to line.",
            )
        elif (
            (isinstance(x_index, _np.ndarray) and x_index.size == 0)
            or (isinstance(y_macd_line, _np.ndarray) and y_macd_line.size == 0)
            or gradient.size < 1
        ):
            return (
                False,
                f"One of the res arrays is empty when convert macd curve to line.",
            )

        desc_set = set()
        # 檢查 MACD 柱狀圖(OSC)
        # 檢查 MACD 靠近軸線
        latest_macd_data = df["MACD"].dropna().to_numpy()
        if len(latest_macd_data) <= 3:
            return False, f"not enough macd data: {len(latest_macd_data)}"

        zeros_array = _np.zeros(df["MACD"].dropna().count())
        if len(latest_macd_data) > 60:
            latest_macd_data = latest_macd_data[-60:]
            zeros_array = zeros_array[-60:]
        is_closing, reason = self.trend_closer_to_golden_cross(
            latest_macd_data, zeros_array
        )
        print(is_closing, reason)
        if is_closing and df["MACD"].iloc[-1] < 0:
            desc_set.add(constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM)
        elif is_closing and df["MACD"].iloc[-1] > 0:
            desc_set.add(constd.MACD_CLOSING_MIDDLE_FROM_ABOVE)

        # 檢查 MACD 趨勢
        if gradient.size == 1:
            if gradient[-1] > 0:
                desc_set.add(constd.MACD_SHOW_UP_TREND)
            else:
                desc_set.add(constd.MACD_SHOW_DOWN_TREND)
        else:
            if gradient[-1] > 0:
                if x_index[-1] - x_index[-2] >= 5:
                    desc_set.add(constd.MACD_SHOW_UP_TREND)
                elif gradient[-1] > gradient[-2]:
                    # 下降趨勢趨緩
                    pass
            elif (
                gradient[-1] < 0
                and gradient[-2] > 0
                and x_index[-1] - x_index[-2] > x_index[-2] - x_index[-3]
            ):
                pass
                return True, "MACD 呈上升趨勢中回測"
            else:
                pass
                return False, "MACD 趨勢不明"

        return False, print(desc_set)
        # uptrend_macd_cross_middle_line_with_N
        # uptrend_macd_cross_middle_line

    # 檢查 MACD 柱狀圖(OSC) 強勢、弱勢、盤整
    def check_osc_stick_heigh(self, df: _pd.DataFrame) -> str:
        local_abs_max = df["OSC"].iloc[-1]
        local_abs_max_previous = 0
        cur = 0
        switch = 0

        # loop through the OSC column backward
        for i in range(
            len(df["OSC"]) - 1, 0, -1
        ):  # Start from the last index to the first
            current_value = df["OSC"].iloc[i]
            previous_value = df["OSC"].iloc[i - 1]
            # check for sign change
            if (previous_value > 0 and current_value < 0) or (
                previous_value < 0 and current_value > 0
            ):
                if switch == 0:
                    local_abs_max = cur
                    switch = switch + 1
                    cur = 0
                    continue
                if switch == 1:
                    local_abs_max_previous = cur
                    switch = switch + 1
                    cur = 0
                    continue
                else:
                    break
            else:
                if abs(cur) < abs(previous_value):
                    cur = previous_value

        if local_abs_max < 0:
            if abs(local_abs_max) <= abs(local_abs_max_previous) / 4:
                return constd.OSC_GREEN_WEEK
            elif abs(local_abs_max) >= abs(local_abs_max_previous) * 4:
                return constd.OSC_GREEN_STRONG
            else:
                return constd.OSC_GREEN_CONSOLIDATION
        elif local_abs_max > 0:
            if abs(local_abs_max) <= abs(local_abs_max_previous) / 4:
                return constd.OSC_RED_WEEK
            elif abs(local_abs_max) >= abs(local_abs_max_previous) * 4:
                return constd.OSC_RED_STRONG
            else:
                return constd.OSC_RED_CONSOLIDATION

    # 強勢股拉回(日)：MACD 紅柱＋零軸上
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

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

    # Ｎ均線扣抵值向上(未來均線向下), Ｎ均線扣抵值向下(未來均線向上彎)
    def find_last_n_pivot_in_previous(self, df: _pd.DataFrame, n_peek: int = 3):
        pass

    # 尋找w底
    def find_latest_w_pattern(
        self, line_x: _np.ndarray, line_y: _np.ndarray, threshold: int = 0.2
    ) -> list[tuple[int, int]]:
        w_pattern = []

        # Iterate over the turning points and look for a W pattern
        i = 2  # Start at 2 to ensure we have at least one peak before the first valley
        while i < len(line_x) - 2:
            prev_peak = line_y[i - 2]  # Peak before the first valley
            first_valley = line_y[i - 1]
            peak = line_y[i]
            second_valley = line_y[i + 1]
            # Check if it forms a W pattern (first valley, peak, second valley)
            if (
                prev_peak > first_valley
                and prev_peak > peak
                and abs(first_valley - second_valley)
                <= threshold * abs(peak - first_valley)
                and peak > first_valley
                # first_valley < peak and second_valley <= first_valley
            ):
                w_pattern = [
                    (line_x[i - 1], first_valley),
                    (line_x[i], peak),
                    (line_x[i + 1], second_valley),
                ]
            i += 1

        if w_pattern:
            # Return the most recent W pattern found
            return w_pattern
        else:
            return None  # No W pattern found

    # 40均線向上，以及角度
    def uptrend_line_gradient(
        self, line_info: tuple[_np.ndarray, _np.ndarray, _np.ndarray], max_lan: int
    ):
        pass

    def trend_closer_to_golden_cross(
        self,
        src_array: _np.ndarray,
        target_array: _np.ndarray,
        window: int = 40,
    ) -> tuple[bool, str]:
        min_len = min(len(src_array), len(target_array))
        if min_len <= window:
            return False, f"input data less than window {window}: {min_len}"

        src_array, target_array = src_array[-window:], target_array[-window:]

        # https://stackoverflow.com/questions/77277096/error-in-calculating-dynamic-time-warping
        # do not use scipy.euclidean to avoid: ValueError: Input vector should be 1-D.
        dist = 2

        # compare DTW distance for all window and half segments
        initial_distance, _ = fastdtw(src_array, target_array, dist=dist)
        midpoint = window // 2
        first_half_distance, _ = fastdtw(
            src_array[:midpoint], target_array[:midpoint], dist=dist
        )
        second_half_distance, _ = fastdtw(
            src_array[midpoint:], target_array[midpoint:], dist=dist
        )

        # Calculate DTW distance for last 1/3 and last 2/3 segments
        seg_2_3 = window * 2 // 3
        seg_1_3 = window // 3

        # Calculate DTW distance for last 1/4 and last 2/4 segments
        seg_2_4 = window // 2  # equivalent to 2/4
        seg_1_4 = window // 4

        # Compute DTW distances for the defined segments
        dist_last_2_3, _ = fastdtw(
            src_array[-seg_2_3:], target_array[-seg_2_3:], dist=dist
        )
        dist_last_1_3, _ = fastdtw(
            src_array[-seg_1_3:], target_array[-seg_1_3:], dist=dist
        )

        dist_last_2_4, _ = fastdtw(
            src_array[-seg_2_4:], target_array[-seg_2_4:], dist=dist
        )
        dist_last_1_4, _ = fastdtw(
            src_array[-seg_1_4:], target_array[-seg_1_4:], dist=dist
        )

        print(
            "trend_closer_to_golden_cross compute res: ",
            initial_distance,
            first_half_distance,
            second_half_distance,
            dist_last_2_3,
            dist_last_1_3,
            dist_last_2_4,
            dist_last_1_4,
        )

        # TODO: refine condition
        # Return True if both conditions are satisfied, indicating closing intent
        if (
            first_half_distance > second_half_distance
            and second_half_distance < initial_distance
            # Check if the last 1/3 is closer than the last 2/3
            and dist_last_1_3 < dist_last_2_3
            # Check if the last 1/4 is closer than the last 2/4
            and dist_last_1_4 < dist_last_2_4
        ):
            return True, "strong closing"
        elif (
            first_half_distance > second_half_distance
            and second_half_distance < initial_distance
        ):
            return True, "week closing"
        return False, ""

    # 旗型，三角收斂，雙底，平台塗破
    def pattern_matcher(self, df: _pd.DataFrame):
        pass

    # 打N(突破零軸回測)
    def zero_line_breakout_backtest(self, df: _pd.DataFrame):
        pass

    # smooth a signal by removing high-frequency noise
    def low_pass_filter(
        self, y: _np.ndarray, cutoff: float = 0.1, order: int = 3
    ) -> _np.ndarray:
        nyquist = 0.5  # Nyquist frequency
        normal_cutoff = cutoff / nyquist  # Normalize cutoff frequency
        b, a = butter(order, normal_cutoff, btype="low", analog=False)
        y_filtered = filtfilt(b, a, y)
        return y_filtered

    def smooth_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.4
    ) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray]:
        x, y = df.index, df[column_name]

        # Step 1: Apply smoothing method (e.g., moving average)
        # y_smooth = _np.convolve(y, _np.ones(3) / 3, mode='same')
        # Step 2: Optionally apply a low-pass filter for additional smoothing
        y_smooth = self.low_pass_filter(y, cutoff=0.1)
        y = y_smooth

        # Find the peaks and valleys using the find_peaks function from scipy
        peaks, _ = find_peaks(y)
        valleys, _ = find_peaks(-y)

        # Combine peaks and valleys to get turning points
        # Sorts the combined array ensuring they are in the correct order along the x-axis.
        turning_points = _np.sort(_np.concatenate((peaks, valleys)))

        # Initialize the simplified x and y for the line graph
        line_x = [x[0]]  # Start with the first point
        line_y = [y[0]]

        # Simplify the curve based on tolerance
        for i in range(1, len(turning_points)):
            prev_idx = turning_points[i - 1]
            curr_idx = turning_points[i]

            # Calculate the difference in y to check if it's significant
            if abs(y[curr_idx] - y[prev_idx]) > tolerance * y[curr_idx]:
                line_x.append(x[curr_idx])
                line_y.append(y[curr_idx])

        # Append the last point
        line_x.append(x[-1])
        line_y.append(y[-1])
        # Compute the gradient (slope) for each line segment
        gradients = _np.diff(line_y) / _np.diff(line_x)

        return _np.array(line_x), _np.array(line_y), gradients

    def smooth_with_polyfit(
        self,
        df: _pd.DataFrame,
        column_name: str,
        degree: int = 50,
        tolerance: float = 0.2,
    ) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray]:
        if not isinstance(df, _pd.DataFrame):
            raise ValueError(
                f"Expected df to be a pandas DataFrame, got {type(df)} instead."
            )

        x = _np.array(df.index.values)
        y = _np.array(df[column_name])

        # Step 1: Fit a polynomial to the data
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RankWarning)  # Suppress RankWarning
            poly_coefficients = _np.polyfit(
                x, y, degree
            )  # Fit a polynomial of the specified degree

        # poly_coefficients = _np.polyfit(x, y, degree)  # Fit a polynomial of the specified degree
        y_smooth = _np.polyval(
            poly_coefficients, x
        )  # Calculate y values based on the polynomial fit

        # Step 2: Find peaks and valleys using the smoothed data
        peaks, _ = find_peaks(y_smooth)
        valleys, _ = find_peaks(-y_smooth)

        # Step 3: Combine peaks and valleys to get turning points
        turning_points = _np.sort(_np.concatenate((peaks, valleys)))

        # Step 4: Initialize the simplified x and y for the line graph
        line_x = [x[0]]  # Start with the first point
        line_y = [y_smooth[0]]

        # Step 5: Simplify the curve based on tolerance
        for i in range(1, len(turning_points)):
            prev_idx = turning_points[i - 1]
            curr_idx = turning_points[i]

            # Calculate the difference in y to check if it's significant
            if (
                abs(y_smooth[curr_idx] - y_smooth[prev_idx])
                > tolerance * y_smooth[curr_idx]
            ):
                line_x.append(x[curr_idx])
                line_y.append(y_smooth[curr_idx])

        # Append the last point
        line_x.append(x[-1])
        line_y.append(y_smooth[-1])

        # Step 6: Compute the gradient (slope) for each line segment
        gradients = _np.diff(line_y) / _np.diff(line_x)

        return _np.array(line_x), _np.array(line_y), gradients

    def check_statistic_column(self, df: _pd.DataFrame) -> bool:
        if not self.check_columns_exist(
            df,
            [
                "MA5",
                "MA10",
                "MA40",
                "MA60",
                "MA138",
                "DIF",
                "MACD",
                "OSI",
                "RSV",
                "K9",
                "D9",
                "BB_Middle",
                "BB_Upper",
                "BB_Lower",
            ],
        ):
            return False
        return True

    def check_columns_exist(
        self, df: _pd.DataFrame, expected_columns: List[str]
    ) -> bool:
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing columns: {missing_columns}")
            return False
        return True
