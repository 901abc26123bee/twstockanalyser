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
from scipy.spatial.distance import euclidean
import warnings
from numpy.exceptions import RankWarning


class Strategy:
    # 月、週 呈高檔鈍化
    def high_end_stagnation_in_month_and_week_kd(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(
                f"Error: Missing columns when high_end_stagnation_in_month_and_week_kd"
            )
            return

        df[""] = _np.abs(df["K9"] - df["D9"])

    # 月線低檔爆量，上影線
    def high_volume_at_low_level_in_month(self, df: _pd.DataFrame):
        pass

    #  MACD 呈上升趨勢
    def check_uptrend_macd(self, df: _pd.DataFrame) -> tuple[bool, str]:
        if not self.check_statistic_column(df):
            return False, f"Error: Missing columns when check_uptrend_macd"

        # convert line to curve
        x_index, y_macd_line, gradient = None, None, None
        if df["MACD"].dropna().count() < 3:
            return False, f"not enough data for check_uptrend_macd"
        elif df["MACD"].dropna().count() > 10:
            x_index, y_macd_line, gradient = self.smooth_with_polyfit(
                df=df, column_name="MACD"
            )
        else:
            x_index, y_macd_line, gradient = self.smooth_to_line(df, "MACD", 0.5)

        # check return res
        if x_index is None or y_macd_line is None or gradient is None:
            return False, f"One of the variables is None."
        elif (isinstance(x_index, _np.ndarray) and x_index.size == 0) or (
            isinstance(y_macd_line, _np.ndarray) and y_macd_line.size == 0
        ):
            return False, f"One of the arrays is empty."

        # TODO: refine verification
        if gradient[-1] > 0:
            return True, "MACD 呈上升趨勢"
        elif (
            gradient[-1] < 0
            and gradient[-2] > 0
            and x_index[-1] - x_index[-2] > x_index[-2] - x_index[-3]
        ):
            return True, "MACD 呈上升趨勢中回測"
        else:
            return False, "MACD 趨勢不明"

    #  MACD 穿過軸線
    def uptrend_macd_cross_middle_line(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(
                f"Error: Missing columns when high_end_stagnation_in_month_and_week_kd"
            )
            return

        if ():
            return True
        return False

    #  MACD 穿過軸線(打Ｎ)
    def uptrend_macd_cross_middle_line_with_N(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(
                f"Error: Missing columns when high_end_stagnation_in_month_and_week_kd"
            )
            return

        if ():
            return True
        return False

    # 強勢股拉回(日)：MACD 紅柱＋零軸上
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

    # 向下趨勢股票[MA5向下 + 收盤<MA5 + 黑k]
    def do_not_touch(self, df: _pd.DataFrame) -> tuple[bool, str]:
        if not self.check_statistic_column(df):
            return True, "Error: Missing columns when do_not_touch"

        #  check if stock is too new
        if (
            df["MA5"].dropna().count() < 3
            or df["MA10"].dropna().count() < 3
            or df["MA20"].dropna().count() < 3
        ):
            return True, "not enough data: MA5, MA10, MA20"

        # check valid prices trend
        if (
            df["High"].iloc[-1] < df["MA5"].iloc[-1]
            and df["MA5"].iloc[-1] < df["MA5"].iloc[-2]
            and df["Close"].iloc[-1] < df["Open"].iloc[-1]
            and df["Close"].iloc[-1] < df["Close"].iloc[-2]
        ):
            return True, "向下趨勢股票[MA5向下 + 最高價<MA5 + 黑k]"

        return False, ""

    # Ｎ均線扣抵值向上(未來均線向下), Ｎ均線扣抵值向下(未來均線向上彎)
    def find_last_n_pivot_in_previous(self, df: _pd.DataFrame, n_peek: int = 3):
        pass

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
        window: int = 150,
    ) -> bool:
        # Ensure arrays are 1-D
        src_array = _np.asarray(src_array).flatten()
        target_array = _np.asarray(target_array).flatten()

        min_len = min(len(src_array), len(target_array))
        if min_len <= window:
            return False

        src_array, target_array = src_array[-window:], target_array[-window:]

        # compare DTW distance for all window and half segments
        initial_distance, _ = fastdtw(src_array, target_array, dist=euclidean)
        midpoint = window // 2
        first_half_distance, _ = fastdtw(
            src_array[:midpoint], target_array[:midpoint], dist=euclidean
        )
        second_half_distance, _ = fastdtw(
            src_array[midpoint:], target_array[midpoint:], dist=euclidean
        )

        # Calculate DTW distance for last 1/3 and last 2/3 segments
        seg_2_3 = window * 2 // 3
        seg_1_3 = window // 3

        # Calculate DTW distance for last 1/4 and last 2/4 segments
        seg_2_4 = window // 2  # equivalent to 2/4
        seg_1_4 = window // 4

        # Compute DTW distances for the defined segments
        dist_last_2_3, _ = fastdtw(
            src_array[-seg_2_3:], target_array[-seg_2_3:], dist=euclidean
        )
        dist_last_1_3, _ = fastdtw(
            src_array[-seg_1_3:], target_array[-seg_1_3:], dist=euclidean
        )

        dist_last_2_4, _ = fastdtw(
            src_array[-seg_2_4:], target_array[-seg_2_4:], dist=euclidean
        )
        dist_last_1_4, _ = fastdtw(
            src_array[-seg_1_4:], target_array[-seg_1_4:], dist=euclidean
        )

        # Check if the last 1/3 is closer than the last 2/3
        is_closing_1_3_vs_2_3 = dist_last_1_3 < dist_last_2_3
        # Check if the last 1/4 is closer than the last 2/4
        is_closing_1_4_vs_2_4 = dist_last_1_4 < dist_last_2_4

        # Return True if both conditions are satisfied, indicating closing intent
        is_closer_1 = (
            first_half_distance > second_half_distance
            and second_half_distance < initial_distance
        )
        is_closer_2 = is_closing_1_3_vs_2_3 and is_closing_1_4_vs_2_4
        return is_closer_1 or is_closer_2

    # 旗型，三角收斂，雙底，平台塗破
    def pattern_matcher(self, df: _pd.DataFrame):
        pass

    # 打N(突破零軸回測)
    def zero_line_breakout_backtest(self, df: _pd.DataFrame):
        pass

    def low_pass_filter(
        self, y: _np.ndarray, cutoff: float = 0.1, order: int = 3
    ) -> _np.ndarray:
        nyquist = 0.5  # Nyquist frequency
        normal_cutoff = cutoff / nyquist  # Normalize cutoff frequency
        b, a = butter(order, normal_cutoff, btype="low", analog=False)
        y_filtered = filtfilt(b, a, y)
        return y_filtered

    def smooth_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.5
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

    def _draw_macd_curve_to_line(self, df: _pd.DataFrame, column_name: str):
        x, y = df.index, df[column_name]
        #  Convert the curve to line with a certain tolerance and get gradients
        line_x_1, line_y_1, gradients = self.smooth_to_line(
            df, column_name, tolerance=0.5
        )
        line_x, line_y, gradients = self.smooth_with_polyfit(
            df, column_name, degree=60, tolerance=0.5
        )
        print(line_x)
        print(line_y)
        print(gradients)
        b, s = self.check_uptrend_macd(df)
        print(b, s)

        # angles_deg = _np.degrees(_np.arctan(gradients))
        # print(angles_deg)

        # Plot the original curve and the simplified line
        _plt.plot(x, y, label="Original Curve")
        _plt.plot(line_x, line_y, label="Simplified Line", marker="o")

        # Annotate the plot with the gradient for each line segment
        for i in range(len(gradients)):
            mid_x = (line_x[i] + line_x[i + 1]) / 2
            mid_y = (line_y[i] + line_y[i + 1]) / 2
            _plt.text(mid_x, mid_y, f"{gradients[i]:.2f}", color="red", fontsize=10)

        # Find the latest W pattern
        w_pattern = self.find_latest_w_pattern(line_x_1, line_y_1, threshold=0.2)
        if len(w_pattern) > 0:
            pattern_last_pos_before = w_pattern[-1]
            print(len(df.index) - pattern_last_pos_before[0] - 1)
        # Mark the W pattern
        if w_pattern:
            for point in w_pattern:
                _plt.scatter(point[0], point[1], color="green", zorder=5)
                _plt.text(
                    point[0],
                    point[1],
                    "W",
                    color="green",
                    fontsize=12,
                    fontweight="bold",
                )

        # Display the datetime values on the x-axis(replace x)
        # Set x-ticks to use the index, but use `df["Datetime"]` for labels
        x_ticks = _np.arange(
            0, len(df), max(1, len(df) // 15)
        )  # Adjust frequency of ticks
        _plt.xticks(
            ticks=x_ticks,
            labels=df["Datetime"].iloc[x_ticks].dt.strftime("%Y-%m-%d"),
            rotation=45,
            ha="right",
        )

        # Draw a horizontal line at y = 0 (black)
        _plt.axhline(y=0, color="k", linestyle="--", label="y = 0")

        _plt.legend()
        _plt.xlabel("Index")  # Set x-axis label to show that it's using index values
        _plt.ylabel(column_name)  # Set y-axis label to the column name
        _plt.title(f"Curve to Line for {column_name}")  # Optional title
        _plt.show()

    def _draw_two_line_closing_to_cross(self, df: _pd.DataFrame):
        # Plotting
        _plt.figure(figsize=(10, 6))  # Set the figure size

        # Plot each column
        for column in ["MA5", "MA10", "MA20", "MA40", "MA60", "MA138"]:
            _plt.plot(df.index, df[column], label=column)

        # compute line trend cross
        res = self.trend_closer_to_golden_cross(
            df["MA40"].dropna().to_numpy(), df["MA138"].dropna().to_numpy()
        )
        print(res)

        # Customize the plot
        _plt.title("Multi-Column Plot")
        _plt.xlabel("Index")
        _plt.ylabel("Values")
        _plt.legend()  # Show the legend
        _plt.grid()  # Show grid
        _plt.show()

    def check_statistic_column(self, df: _pd.DataFrame) -> bool:
        if not self.check_columns_exist(
            df,
            [
                "MA5",
                "MA10",
                "MA20",
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
