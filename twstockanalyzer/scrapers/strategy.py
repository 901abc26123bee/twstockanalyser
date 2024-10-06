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
from scipy.signal import find_peaks, butter, filtfilt
from fastdtw import fastdtw
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

    def check_ma(self, df: _pd.DataFrame) -> tuple[bool, str]:
        if not self.check_statistic_column(df):
            return False, f"Error: Missing columns when check_macd_trend"

        is_closing, desc, res = self.trend_closer_to_golden_cross(
            df["MA40"].dropna().to_numpy(), df["MA138"].dropna().to_numpy()
        )
        if is_closing:
            _, _, ma40_gradient = self.smooth_to_line(
                df=df, column_name="MA40", window=60
            )
            _, _, ma138_gradient = self.smooth_to_line(
                df=df, column_name="MA138", window=60
            )
            if df["MA40"].iloc[-1] >= df["MA138"].iloc[-1]:
                if ma40_gradient[-1] >= 0:
                    return True, constd.MA40_ABOVE_MA138
                else:
                    return True, ""

    #  MACD 呈上升趨勢
    def check_macd_trend(self, df: _pd.DataFrame) -> tuple[bool, Optional[set[str]]]:
        if not self.check_columns_exist(
            df,
            [
                "MACD",
                "OSC",
            ],
        ):
            print("Error: missing column in check_macd_trend.")
            return False, None

        # convert macd curve to line
        x_index, y_macd_line, gradient = self.smooth_to_line(df, "MACD", 0.4)

        # check return res
        if x_index is None or y_macd_line is None or gradient is None:
            print(
                "Error: One of the returned variables is None when convert macd curve to line."
            )
            return False, None
        elif (
            (isinstance(x_index, _np.ndarray) and x_index.size == 0)
            or (isinstance(y_macd_line, _np.ndarray) and y_macd_line.size == 0)
            or gradient.size < 1
        ):
            print(
                "Error: One of the res arrays is empty when convert macd curve to line."
            )
            return False, None

        macd_trend_set = set()
        is_up_trend = False

        # 檢查 MACD 靠近軸線
        latest_macd_data = df["MACD"].dropna().to_numpy()
        if len(latest_macd_data) <= 3:
            print(f"Error: not enough macd data: {len(latest_macd_data)}")
            return False, None

        middle_array = _np.zeros(df["MACD"].dropna().count())
        if len(latest_macd_data) > 60:
            latest_macd_data = latest_macd_data[-60:]
            middle_array = middle_array[-60:]

        is_closing_middle, closing_middle_trend_desc, _ = (
            self.trend_closer_to_golden_cross(
                latest_macd_data, middle_array, window=len(latest_macd_data)
            )
        )

        # 檢查 MACD 柱狀圖(OSC)
        osc_trend_set = self.check_osc_stick_heigh(df)
        if osc_trend_set is None:
            print("Error: failed to check_osc_stick_heigh.")
            return False, None

        # do not touch condition
        # OSC 強綠柱 + OSC 綠柱範圍長 + macd零軸下 範圍長 + MACD 下降趨勢
        fit_count = 0
        osc_cond_to_check = [constd.OSC_GREEN_STRONG, constd.OSC_GREEN_RANGE_LONG]
        for value in osc_cond_to_check:
            if value in osc_trend_set:
                fit_count += 1
        macd_line_cond_to_check = [
            constd.LINE_TREND_DOWNWARD,
            constd.LINE_TREND_STRONG_LEAVING,
        ]
        for value in closing_middle_trend_desc:
            if value in macd_line_cond_to_check:
                fit_count += 1

        last_five_values = df["MACD"].tail(5)
        if fit_count == 4 and gradient[-1] < 0 and (last_five_values < 0).all():
            macd_trend_set.add(constd.MACD_DO_NOT_TOUCH)
            return False, macd_trend_set

        # MACD 零軸上/下
        if (last_five_values > 0).all():
            macd_trend_set.add(constd.MACD_ABOVE_MIDDLE)
        if (last_five_values < 0).all():
            macd_trend_set.add(constd.MACD_BELOW_MIDDLE)

        # 從上方/下方靠近軸線
        if is_closing_middle and constd.LINE_TREND_UPWARD in closing_middle_trend_desc:
            macd_trend_set.add(constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM)
            is_up_trend = True
        if (
            is_closing_middle
            and constd.LINE_TREND_DOWNWARD in closing_middle_trend_desc
        ):
            macd_trend_set.add(constd.MACD_CLOSING_MIDDLE_FROM_ABOVE)

        # 檢查 MACD 趨勢
        validate_ratio = 1.2
        if gradient[-1] > gradient[-2] and gradient[-2] > 0:
            macd_trend_set.add(constd.MACD_SHOW_UP_UP_TREND)
            is_up_trend = True
        if gradient[-1] < gradient[-2] and gradient[-2] < 0:
            macd_trend_set.add(constd.MACD_SHOW_DOWN_DOWN_TREND)
        elif (
            gradient[-1] < 0
            and gradient[-2] > 0
            and (
                abs(y_macd_line[-1] - y_macd_line[-2]) * validate_ratio
                < abs(y_macd_line[-2] - y_macd_line[-3])
                or (x_index[-1] - x_index[-2]) * validate_ratio
                < (x_index[-2] - x_index[-3])
            )
        ):
            macd_trend_set.add(constd.MACD_BACKTEST_IN_UP_TREND)
            is_up_trend = True
        elif (
            gradient[-1] > 0
            and gradient[-2] < 0
            and (
                abs(y_macd_line[-1] - y_macd_line[-2]) * validate_ratio
                < abs(y_macd_line[-2] - y_macd_line[-3])
                or (x_index[-1] - x_index[-2]) * validate_ratio
                < (x_index[-2] - x_index[-3])
            )
        ):
            macd_trend_set.add(constd.MACD_BACKTEST_IN_DOWN_TREND)
        else:
            if gradient[-1] > 0 and x_index[-1] - x_index[-2] >= 5:
                macd_trend_set.add(constd.MACD_SHOW_UP_TREND)
                is_up_trend = True
            elif gradient[-1] < 0 and x_index[-1] - x_index[-2] >= 5:
                macd_trend_set.add(constd.MACD_SHOW_DOWN_TREND)

        # if (gradient[-1] < 0 and x_index[-1]-x_index[-2] >= 5) or (gradient[-2] < 0 and (x_index[-2]-x_index[-3]) > (x_index[-1]-x_index[-2])*2):
        #     res_set.add(constd.LINE_TREND_DOWNWARD)
        # if (gradient[-1] > 0 and x_index[-1]-x_index[-2] >= 5) or (gradient[-2] > 0 and (x_index[-2]-x_index[-3]) > (x_index[-1]-x_index[-2])*2):
        #     res_set.add(constd.LINE_TREND_UPWARD)

        if len(macd_trend_set) == 0:
            macd_trend_set.add(constd.MACD_UNKNOWN)

        return is_up_trend, macd_trend_set

    # 檢查 MACD 柱狀圖(OSC) 強勢、弱勢、盤整
    def check_osc_stick_heigh(
        self, df: _pd.DataFrame, threshold: int = 2
    ) -> Optional[set[str]]:
        if df["OSC"].dropna().size < 3:
            print("not enough OSC data in check_osc_stick_heigh")
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
            res_set.add(constd.LINE_TREND_STRONG_CLOSING_TO_CROSS)
            is_closing = True
        elif dist_first_half >= dist_last_half and dist_last_half <= dist_all:
            res_set.add(constd.LINE_TREND_WEEK_CLOSING_TO_CROSS)
            is_closing = True
        elif (
            dist_first_half <= dist_last_half
            and dist_all <= dist_last_half
            # Check if the last 1/3 is closer than the last 2/3
            and dist_last_1_3 >= dist_last_2_3
            # Check if the last 1/4 is closer than the last 2/4
            and dist_last_1_4 >= dist_last_2_4
        ):
            res_set.add(constd.LINE_TREND_STRONG_LEAVING)
        elif dist_first_half <= dist_last_half and dist_last_half >= dist_all:
            res_set.add(constd.LINE_TREND_WEEK_LEAVING)
        else:
            res_set.add(constd.LINE_TREND_TREAD_UNKNOWN)

        src_df = _pd.DataFrame(src_array, columns=["src"])
        _, _, gradient = self.smooth_to_line(src_df, "src", window=20)
        if len(gradient) == 1:
            if gradient[-1] < 0:
                res_set.add(constd.LINE_TREND_DOWNWARD)
                if src_array[0] > target_array[0] and src_array[-1:] < target_array[-1]:
                    res_set.add(constd.LINE_TREND_CROSS_OVER_DOWNWARD)
            elif gradient[-1] > 0:
                res_set.add(constd.LINE_TREND_UPWARD)
                if src_array[0] < target_array[0] and src_array[-1:] > target_array[-1]:
                    res_set.add(constd.LINE_TREND_CROSS_OVER_UPWARD)
        elif len(gradient) == 2:
            if gradient[0] > 0 and gradient[-1:] < 0:
                res_set.add(constd.LINE_TREND_NEGATIVE_V)
            elif gradient[0] < 0 and gradient[-1:] > 0:
                res_set.add(constd.LINE_TREND_POSITIVE_V)
            elif gradient[0] > 0 and gradient[1] > 0:
                res_set.add(constd.LINE_TREND_UPWARD)
                if gradient[-1:] > gradient[0]:
                    res_set.add(constd.LINE_TREND_UPWARD_UP)
            elif gradient[0] < 0 and gradient[1] < 0:
                res_set.add(constd.LINE_TREND_DOWNWARD)
                if gradient[-1:] < gradient[0]:
                    res_set.add(constd.LINE_TREND_DOWNWARD_DOWN)
            elif gradient[-1] > 0:
                res_set.add(constd.LINE_TREND_UPWARD)
            elif gradient[-1] < 0:
                res_set.add(constd.LINE_TREND_UPWARD)
            # TODO: 穿越回測, 打Ｎ

        return is_closing, res_set, res_dist

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
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.4, window: int = 0
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
