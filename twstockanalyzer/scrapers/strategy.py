#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt
from typing import List
from scipy.signal import find_peaks


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
    def uptrend_macd(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(f"Error: Missing columns when uptrend_macd")
            return

        x_datetime, y_macd_line, gradient = self.smooth_to_line(
            df, "Datetime", "MACD", 0.5
        )
        if gradient[-1:] > 0.2 and x_datetime:
            return True
        return False

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

    # 向下趨勢股票[MA5向下 + 收盤<MA5 + 黑k + 5d volume sum < 500]
    def do_not_touch(self, df: _pd.DataFrame) -> tuple:
        if not self.check_statistic_column(df):
            return True, "Error: Missing columns when do_not_touch"

        # check valid volume
        if df["Volume"].notna().count() < 5:
            return True, "prices data < 5"
        elif df["Volume"].tail(5).sum() < 800:
            return True, "sum latest 5 volume < 800"

        #  check if stock is too new
        if (
            df["MA5"].notna().count() < 3
            or df["MA10"].notna().count() < 3
            or df["MA20"].notna().count() < 3
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
    ) -> tuple:
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
        src_array: _np.ndarray,
        target_array: _np.ndarray,
        window: int = 3,
        latest_count: int = 60,
    ) -> float:
        # get latest_count of diff among src and target array
        difference = target_array - src_array
        mean_difference = _pd.Series(difference).rolling(window=window).mean()
        latest_diff = mean_difference[-latest_count:]

        # calculate the count of points where a decreasing trend is observed
        decreasing_count = sum(
            latest_diff.iloc[i] >= latest_diff.iloc[i + 1]
            for i in range(len(latest_diff) - 1)
            if _pd.notna(latest_diff.iloc[i + 1])  # Ensure the next point is not NaN
        )

        # calculate the percentage of points showing a closing trend
        closing_trend_percentage = (decreasing_count / (len(latest_diff) - 1)) * 100
        diff_percentage = latest_diff.iloc[-1] / src_array[-1:]
        return closing_trend_percentage, diff_percentage

    # 旗型，三角收斂，雙底，平台塗破
    def pattern_matcher(self, df: _pd.DataFrame):
        pass

    # 打N(突破零軸回測)
    def zero_line_breakout_backtest(self, df: _pd.DataFrame):
        pass

    def smooth_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.3
    ) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray]:
        x, y = df.index, df[column_name]

        # Find the peaks and valleys using the find_peaks function from scipy
        peaks, _ = find_peaks(y)
        valleys, _ = find_peaks(-y)

        # Combine peaks and valleys to get turning points
        # Sorts the combined array ensuring they are in the correct order along the x-axis.
        turning_points = _np.sort(_np.concatenate((peaks, valleys)))

        # Initialize the simplified x and y for the line graph
        line_x = [x[0]]  # Start with the first point
        line_y = [y.iloc[0]]

        # Simplify the curve based on tolerance
        for i in range(1, len(turning_points)):
            prev_idx = turning_points[i - 1]
            curr_idx = turning_points[i]

            # Calculate the difference in y to check if it's significant
            if abs(y.iloc[curr_idx] - y.iloc[prev_idx]) > tolerance * y.iloc[curr_idx]:
                line_x.append(x[curr_idx])
                line_y.append(y.iloc[curr_idx])

        # Append the last point
        line_x.append(x[-1])
        line_y.append(y.iloc[-1])
        # Compute the gradient (slope) for each line segment
        gradients = _np.diff(line_y) / _np.diff(line_x)

        return _np.array(line_x), _np.array(line_y), gradients

    def _draw_curve_to_line(self, df: _pd.DataFrame, column_name: str):
        x, y = df.index, df[column_name]
        #  Convert the curve to line with a certain tolerance and get gradients
        line_x, line_y, gradients = self.smooth_to_line(df, column_name, tolerance=0.3)
        # print(line_x)
        # print(line_y)
        # print(gradients)

        angles_deg = _np.degrees(_np.arctan(gradients))
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
        w_pattern = self.find_latest_w_pattern(line_x, line_y, threshold=0.2)
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

        # Display the datetime values on the x-axis
        # Set x-ticks to use the index, but use `df["Datetime"]` for labels
        x_ticks = _np.arange(
            0, len(df), max(1, len(df) // 10)
        )  # Adjust frequency of ticks
        _plt.xticks(
            ticks=x_ticks,
            labels=df["Datetime"].iloc[x_ticks].dt.strftime("%Y-%m-%d"),
            rotation=45,
            ha="right",
        )

        _plt.legend()
        _plt.xlabel("Index")  # Set x-axis label to show that it's using index values
        _plt.ylabel(column_name)  # Set y-axis label to the column name
        _plt.title(f"Curve to Line for {column_name}")  # Optional title
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
