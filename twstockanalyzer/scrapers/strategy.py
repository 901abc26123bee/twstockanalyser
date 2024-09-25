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
    def high_end_stagnation_in_month_and_week(self, df: _pd.DataFrame):
        if not self.check_columns_exist(list("K9", "D9")):
            print(f"Error: Missing columns when high_end_stagnation_in_month_and_week")
            return
        df[""] = _np.abs(df["K9"] - df["D9"])

    # 月線低檔爆量，上影線
    def high_volume_at_low_level_in_month(self, df: _pd.DataFrame):
        pass

    #  MACD 呈上升趨勢
    def uptrend_macd(self, df: _pd.DataFrame):
        x_datetime, y_macd_line, gradient = self.curve_to_line(df, "MACD", 0.5)
        if gradient > 0:
            return True
        return False

    #  MACD 穿過軸線(打Ｎ)
    def uptrend_macd_cross_middle_line(self, df: _pd.DataFrame):
        if ():
            return True
        return False

    #  MACD 穿過軸線(打Ｎ)
    def uptrend_macd_cross_middle_line_with_N(self, df: _pd.DataFrame):
        if ():
            return True
        return False

    # 強勢股拉回(日)：MACD 紅柱＋零軸上
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column():
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

    # 向下趨勢股票[MA5向下 + 收盤<MA5 + MA5<MA10 + MA10<MA20 + 黑k + 5d volume sum < 500]
    def is_downtrend_in_prices_ma(self, df: _pd.DataFrame) -> bool:
        if not self.check_statistic_column():
            print(f"Error: Missing columns when is_downtrend_in_prices_ma")
        if (
            df["High"].iloc[-1] < df["MA5"].iloc[-1]
            and df["MA5"].iloc[-1] < df["MA5"].iloc[-2]
            and df["MA5"].iloc[-1] < df["MA10"].iloc[-1]
            and df["MA10"].iloc[-1] < df["MA10"].iloc[-2]
            and df["MA10"].iloc[-1] < df["MA20"].iloc[-1]
            and df["MA20"].iloc[-1] < df["MA20"].iloc[-2]
            and df["Close"].iloc[-1] < df["Open"].iloc[-1]
            and df["Close"].iloc[-1] < df["Close"].iloc[-2]
            and df["Volume"].tail(5).sum() < 500
        ):
            return True
        return False

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
                and abs(abs(first_valley) - abs(second_valley))
                <= threshold * ((abs(first_valley) + abs(second_valley)) / 2)
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
    def uptrend_line_angle(self, df: _pd.DataFrame):
        pass

    # 5,10,40均線向上小於138均，向上靠近
    def trend_closer_to_golden_cross(
        self,
        df: _pd.DataFrame,
        src_column_name: str,
        target_column_name: str,
        window: int = 3,
        tolerance: int = 0.75,
    ) -> bool:
        df["distance"] = _np.abs(df[src_column_name] - df[target_column_name])
        # Calculate moving average of distances
        df["moving_avg_distance"] = df["distance"].rolling(window=window).mean()
        # 判断移动平均距离是否有下降趋势
        decreasing_count = sum(
            df["moving_avg_distance"].iloc[i] >= df["moving_avg_distance"].iloc[i + 1]
            for i in range(len(df["moving_avg_distance"]) - 1)
            if _pd.notna(df["moving_avg_distance"].iloc[i + 1])
        )

        # 计算70%的阈值
        threshold = tolerance * (len(df["moving_avg_distance"]) - (window - 1))

        if decreasing_count >= threshold:
            return True
        else:
            return False
        # TODO: test

    # 旗型，三角收斂，雙底，平台塗破
    def pattern_matcher(self, df: _pd.DataFrame):
        pass

    # 打N(突破零軸回測)
    def zero_line_breakout_backtest(self, df: _pd.DataFrame):
        pass

    def curve_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.1
    ) -> tuple[_np.ndarray, _np.ndarray, _np.ndarray]:
        x, y = df.index, df[column_name]

        # Find the peaks and valleys using the find_peaks function from scipy
        peaks, _ = find_peaks(y)
        valleys, _ = find_peaks(-y)

        # Combine peaks and valleys to get turning points
        turning_points = _np.sort(_np.concatenate((peaks, valleys)))

        # Initialize the simplified x and y for the line graph
        line_x = [x[0]]  # Start with the first point
        line_y = [y.iloc[0]]

        # Simplify the curve based on tolerance
        for i in range(1, len(turning_points)):
            prev_idx = turning_points[i - 1]
            curr_idx = turning_points[i]

            # Calculate the difference in y to check if it's significant
            if abs(y.iloc[curr_idx] - y.iloc[prev_idx]) > tolerance:
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
        line_x, line_y, gradients = self.curve_to_line(df, column_name, tolerance=0.5)

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

        _plt.legend()
        _plt.show()

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
                "BBAND_MA",
                "BBAND_UpperBand",
                "BBAND_LowerBand",
            ],
        ):
            print(f"Error: Missing columns")

    def check_columns_exist(df: _pd.DataFrame, expected_columns: List[str]) -> bool:
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing columns: {missing_columns}")
            return False
        return True
