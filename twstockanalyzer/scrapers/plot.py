#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: plot strategy view
#

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt

from twstockanalyzer.scrapers.strategy import Strategy


class StrategyPlot(Strategy):
    def __init__(self):
        pass

    def _draw_macd_curve_to_line(self, df: _pd.DataFrame, column_name: str):
        x, y = df.index, df[column_name]
        #  Convert the curve to line with a certain tolerance and get gradients
        line_x, line_y, gradients = self.smooth_to_line(df, "MACD", tolerance=0.4)
        line_x_1, line_y_1, gradients_1 = self.smooth_with_polyfit(
            df, "MACD", degree=120, tolerance=0.2
        )
        # print(line_x_1)
        # print(line_y_1)
        # print(gradients_1)
        is_closing, reason = self.check_macd_trend(df)
        print(is_closing, reason)

        # angles_deg = _np.degrees(_np.arctan(gradients))
        # print(angles_deg)

        # Plot the original curve and the simplified line
        _plt.plot(x, y, label="Original Curve")
        _plt.plot(line_x, line_y, label="Simplified Line curve to line", marker="o")
        _plt.plot(line_x_1, line_y_1, label="Simplified Line with polyfit", marker="o")

        # Annotate the plot with the gradient for each line segment
        for i in range(len(gradients)):
            mid_x = (line_x[i] + line_x[i + 1]) / 2
            mid_y = (line_y[i] + line_y[i + 1]) / 2
            _plt.text(mid_x, mid_y, f"{gradients[i]:.2f}", color="red", fontsize=10)

        # Find the latest W pattern according to curve to line
        w_pattern = self.find_latest_w_pattern(line_x_1, line_y_1, threshold=0.2)
        if w_pattern is not None:
            if len(w_pattern) > 0:
                pattern_last_pos_before = w_pattern[-1]
                print(
                    f"W底的第二隻腳在{len(df.index) - pattern_last_pos_before[0] - 1}跟k棒前"
                )
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

        # Find the latest W pattern according to curve to line with polyfit
        w_pattern_1 = self.find_latest_w_pattern(line_x_1, line_y_1, threshold=0.2)
        if w_pattern_1 is not None:
            if len(w_pattern_1) > 0:
                pattern_last_pos_before = w_pattern_1[-1]
                print(
                    f"W底的第二隻腳在{len(df.index) - pattern_last_pos_before[0] - 1}跟k棒前"
                )
        # Mark the W pattern
        if w_pattern_1:
            for point in w_pattern_1:
                _plt.scatter(point[0], point[1], color="blue", zorder=5)
                _plt.text(
                    point[0],
                    point[1],
                    "W",
                    color="blue",
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
        for column in ["MA5", "MA10", "MA40", "MA60", "MA138"]:
            _plt.plot(df.index, df[column], label=column)

        # compute line trend cross
        is_closing, desc, res = self.trend_closer_to_golden_cross(
            df["MA40"].dropna().to_numpy(), df["MA138"].dropna().to_numpy()
        )
        print(is_closing, desc, res)

        # Customize the plot
        _plt.title("Multi-Column Plot")
        _plt.xlabel("Index")
        _plt.ylabel("Values")
        _plt.legend()  # Show the legend
        _plt.grid()  # Show grid
        _plt.show()
