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
        pass

    # 月線低檔爆量
    def high_volume_at_low_level_in_month(self, df: _pd.DataFrame):
        pass

    # 60m or 30m or 15m MACD 呈上升趨勢
    def is_buy_point_in_minute_macd(self, df: _pd.DataFrame):
        if ():
            return True
        return False

    # 強勢股拉回(日)
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column():
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

    # 向下趨勢股票[MA5向下 + 收盤<MA5 + MA5<MA10 + 黑k + osi綠柱 ＋ osi綠柱遞增]
    def is_downtrend_in_prices(self, df: _pd.DataFrame) -> bool:
        if not self.check_statistic_column():
            print(f"Error: Missing columns when is_downtrend_in_prices")
        if (
            df["MA5"].iloc[-1] < df["MA5"].iloc[-2]
            and df["High"].iloc[-1] < df["MA5"].iloc[-1]
            and df["MA5"].iloc[-1] < df["MA10"].iloc[-1]
            and df["Close"].iloc[-1] < df["Open"].iloc[-1]
            and df["OSI"].iloc[-1] < 0
            and df["OSI"].iloc[-1] < df["OSI"].iloc[-2]
        ):
            return True
        return False

    # Ｎ均線扣抵值向上(未來均線向下), Ｎ均線扣抵值向下(未來均線向上彎)
    def find_pivot(self, df: _pd.DataFrame):
        pass

    # 40均線向上，以及角度
    def uptrend_forty_ma(self, df: _pd.DataFrame):
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

    def horizontal_lines(self, df: _pd.DataFrame):
        # TODO: 繪製所有箱型
        # Plot Horizontal Lines
        _plt.figure(figsize=(20, 10))
        _plt.hlines(
            df["Close"].mean(),
            xmin=df.index[0],
            xmax=df.index[-1],
            linewidth=2,
            label="Mean",
            linestyle="--",
        )
        _plt.hlines(
            df["Close"].median(),
            xmin=df.index[0],
            xmax=df.index[-1],
            color="y",
            label="Median",
            linestyle="--",
        )
        _plt.hlines(
            df["Close"].mode(),
            xmin=df.index[0],
            xmax=df.index[-1],
            color="orange",
            label="Mode",
            linestyle="--",
        )
        _plt.plot(df["Close"].idxmax(), df["Close"].max(), "ro", label="Highest Point")
        _plt.plot(df["Close"].idxmin(), df["Close"].min(), "go", label="Lowest Point")
        _plt.plot(df["Close"], color="blue")
        _plt.title("Stock Price")
        _plt.xlabel("Date")
        _plt.ylabel("Price")
        _plt.legend(loc="best")
        _plt.show()

    def curve_to_line(
        self, df: _pd.DataFrame, column_name: str, tolerance: int = 0.1
    ) -> tuple[_np.ndarray, _np.ndarray]:
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

        return _np.array(line_x), _np.array(line_y)

    def _draw_curve_to_line(self, df: _pd.DataFrame, column_name: str):
        x, y = df.index, df[column_name]
        # Convert the curve to line with a certain tolerance
        line_x, line_y = self.curve_to_line(df, column_name, tolerance=0.5)

        # Plot the original curve and the simplified line
        _plt.plot(x, y, label="Original Curve")
        _plt.plot(line_x, line_y, label="Simplified Line", marker="o")
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
