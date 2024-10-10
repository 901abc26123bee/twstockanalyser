#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

import warnings
from typing import Optional
import pandas as _pd
import numpy as _np
from typing import List
from scipy.signal import find_peaks, butter, filtfilt, sosfiltfilt
from fastdtw import fastdtw
from numpy.exceptions import RankWarning
import twstockanalyzer.strategy.const as constd


class Strategy:
    def __init__(self):
        pass

    def find_line_pattern_and_trend(self):
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
                and (prev_peak - peak) > threshold * peak
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

    # # 40均線向上，以及角度
    # def uptrend_line_gradient(
    #     self, line_info: tuple[_np.ndarray, _np.ndarray, _np.ndarray], max_lan: int
    # ):
    #     pass

    def trend_closer_to_golden_cross(
        self,
        src_array: _np.ndarray,
        target_array: _np.ndarray,
        window: int = 20,
    ) -> tuple[bool, Optional[set[str]], Optional[dict]]:
        min_len = min(len(src_array), len(target_array))
        if min_len < window:
            print(f"input data less than window {window}: {min_len}")
            return False, None, None

        src_array, target_array = src_array[-window:], target_array[-window:]

        # https://stackoverflow.com/questions/77277096/error-in-calculating-dynamic-time-warping
        # do not use scipy.euclidean to avoid: ValueError: Input vector should be 1-D.
        dist = 2
        res_set = set()
        is_closing = False

        # compare DTW distance for all window and half segments
        dist_all, _ = fastdtw(src_array, target_array, dist=dist)
        dist_all /= min_len
        midpoint = window // 2
        dist_first_half, _ = fastdtw(
            src_array[:midpoint], target_array[:midpoint], dist=dist
        )
        dist_first_half /= midpoint
        dist_last_half, _ = fastdtw(
            src_array[midpoint:], target_array[midpoint:], dist=dist
        )
        dist_last_half /= min_len - midpoint

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
        dist_last_2_3 /= seg_2_3
        dist_last_1_3, _ = fastdtw(
            src_array[-seg_1_3:], target_array[-seg_1_3:], dist=dist
        )
        dist_last_1_3 /= seg_1_3

        dist_last_2_4, _ = fastdtw(
            src_array[-seg_2_4:], target_array[-seg_2_4:], dist=dist
        )
        dist_last_2_4 /= seg_2_4
        dist_last_1_4, _ = fastdtw(
            src_array[-seg_1_4:], target_array[-seg_1_4:], dist=dist
        )
        dist_last_1_4 /= seg_1_4

        res_dist = {
            "dist_all": round(float(dist_all), 5),
            "dist_first_half": round(float(dist_first_half), 5),
            "dist_last_half": round(float(dist_last_half), 5),
            "dist_last_2_3": round(float(dist_last_2_3), 5),
            "dist_last_1_3": round(float(dist_last_1_3), 5),
            "dist_last_2_4": round(float(dist_last_2_4), 5),
            "dist_last_2_4": round(float(dist_last_1_4), 5),
        }

        # TODO: refine condition
        # Return True if both conditions are satisfied, indicating closing intent
        if (
            dist_first_half >= dist_last_half
            and dist_all >= dist_last_half
            # Check if the last 1/3 is closer than the last 2/3
            and dist_last_1_3 <= dist_last_2_3
            # Check if the last 1/4 is closer than the last 2/4
            and dist_last_1_4 <= dist_last_2_4
        ):
            res_set.add(constd.LINE_SRC_TREND_STRONG_CLOSING_TO_CROSSOVER)
            is_closing = True
        elif dist_first_half >= dist_last_half and dist_last_half <= dist_all:
            res_set.add(constd.LINE_SRC_TREND_WEEK_CLOSING_TO_CROSSOVER)
            is_closing = True
        elif (
            dist_first_half <= dist_last_half
            and dist_all <= dist_last_half
            # Check if the last 1/3 is closer than the last 2/3
            and dist_last_1_3 >= dist_last_2_3
            # Check if the last 1/4 is closer than the last 2/4
            and dist_last_1_4 >= dist_last_2_4
        ):
            res_set.add(constd.LINE_SRC_TREND_STRONG_LEAVING_FROM_TARGET)
        elif dist_first_half <= dist_last_half and dist_last_half >= dist_all:
            res_set.add(constd.LINE_SRC_TREND_WEEK_LEAVING_FROM_TARGET)
        else:
            res_set.add(constd.LINE_CLOSER_TREAD_UNKNOWN)

        # check cross over exist
        diff = src_array - target_array
        # Identify the points where the sign of the difference changes from negative to positive
        golden_cross_indices = _np.where((diff[:-1] < 0) & (diff[1:] > 0))[0] + 1
        death_cross_indices = _np.where((diff[:-1] > 0) & (diff[1:] < 0))[0] + 1
        if len(golden_cross_indices) == 1 and len(death_cross_indices) == 0:
            res_set.add(constd.LINE_SRC_CROSSOVER_TARGET_UPWARD)
        elif len(death_cross_indices) == 1 and len(golden_cross_indices) == 0:
            res_set.add(constd.LINE_SRC_CROSSOVER_TARGET_DOWNWARD)
        elif len(golden_cross_indices) > 1 or len(death_cross_indices):
            res_set.add(constd.LINE_SRC_CROSSOVER_TARGET)

        return is_closing, res_set, res_dist

    # 旗型，三角收斂，雙底，平台塗破
    def pattern_matcher(self, df: _pd.DataFrame):
        pass

    # smooth a signal by removing high-frequency noise
    def low_pass_filter(
        self, y: _np.ndarray, cutoff: float = 0.1, order: int = 3
    ) -> _np.ndarray:
        # avoid: ValueError: The length of the input vector x must be greater than padlen, which is 12.
        if len(y) <= 12:
            return y
        nyquist = 0.5  # Nyquist frequency
        normal_cutoff = cutoff / nyquist  # Normalize cutoff frequency
        b, a = butter(order, normal_cutoff, btype="low", analog=False)
        y_filtered = filtfilt(b, a, y)
        return y_filtered

    def smooth_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.3, window: int = 0
    ) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray]:
        x, y = _np.ndarray, _np.ndarray
        if window != 0:
            df_window = df.tail(window)
            x, y = df_window.index.to_numpy(), df_window[column_name].to_numpy()
        else:
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
        gradients_rounded = _np.round(gradients, 6)

        return _np.array(line_x), _np.array(line_y), gradients_rounded

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
        gradients_rounded = _np.round(gradients, 6)

        return _np.array(line_x), _np.array(line_y), gradients_rounded

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
                "OSC",
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
