#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as plt

class Strategy:
    def __init__(self, data: any):
        self.data = data

    # 月、週 呈高檔鈍化
    def high_end_stagnation_in_month_and_week(self):
        pass

    # 月線低檔爆量
    def high_volume_at_low_level_in_month(self):
        pass

    # 60m or 30m or 15m MACD 呈上升趨勢
    def is_buy_point_in_minute_macd(self):
        pass

    # 強勢股拉回(日)
    def is_pullback_in_a_uptrend_stock_day(self):
        pass

    # 月、週 呈向下趨勢股票
    def _is_downtrend_in_month_and_week(self):
        pass

    # Ｎ均線扣抵值向下(未來均線向上彎)
    def downtrend_deduction_value(self):
        pass

    # Ｎ均線扣抵值向上(未來均線向下)
    def uptrend_deduction_value(self):
        pass

    # 40均線向上，以及角度
    def uptrend_forty_ma(self):
        pass

    # 5,10,40均線向上小於138均，向上靠近
    def close_to_138ma_from_button(self):
        pass


class Analysis:
    def __init__(self, data: any = _pd.DataFrame):
        # data is a series of closing prices recorded at specific time intervals
        if not isinstance(data, _pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        self.data = data

    def moving_average(self, header: str, window: int):
        """
        This method computes the moving average of the 'Close' prices over a specified
        window of time and stores the result in a new column within the DataFrame.

        :param header: The name of the column to store the moving average result.
        :param window: The number of periods to use for calculating the moving average.
                        For example, a window of 20 will compute the average over the last
                        20 closing prices.
        """
        self.data[header] = self.data["Close"].rolling(window=window).mean()
        print(self.data[header])

    def macd(self, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
        """
        Calculate the Moving Average Convergence Divergence (MACD) indicator.

        Parameters:
        short_window (int): The span for the short-term EMA (default is 12).
        long_window (int): The span for the long-term EMA (default is 26).
        signal_window (int): The span for the signal line EMA (default is 9).
        """
        self.data["EMA_SHORT"] = self.data["Close"].ewm(span=short_window, adjust=False).mean()
        self.data["EMA_LONG"] = self.data["Close"].ewm(span=long_window, adjust=False).mean()

        self.data["DIF"] = self.data["EMA_SHORT"] - self.data["EMA_LONG"]
        self.data["MACD"] = self.data["DIF"].ewm(span=signal_window, adjust=False).mean()
        self.data["OSI"] = self.data["MACD"] - self.data["DIF"]

        # Print the MACD, OSI, and DIF values
        print(self.data["MACD"])
        print(self.data["OSI"])
        print(self.data["DIF"])

    def kdj(self, k_window: int = 20, d_window: int = 9, j_window: int = 9):
        """
        Calculate the KDJ indicator, which includes %K, %D, and J lines.

        Parameters:
        k_window (int): The window for the %K calculation (default is 20).
        d_window (int): The window for the %D calculation (default is 9).
        j_window (int): The window for the J calculation (default is 9).
        """
        high_max = self.data["High"].rolling(window=k_window).max()
        low_min = self.data["Low"].rolling(window=k_window).min()

        self.data["%K"] = 100 * ((self.data["Close"] - low_min) / (high_max - low_min))
        self.data["%D"] = self.data["%K"].rolling(window=d_window).mean()
        self.data["J"] = 3 * self.data["%K"] - 2 * self.data["%D"].rolling(window=j_window).mean()

        print(self.data["%K"])
        print(self.data["%D"])
        print(self.data["J"])


    def bbands(self, window: int = 16, num_std_dev: int = 2):
        """
        This method calculate Bollinger Bands.

        :param window: The number of periods for the moving average and standard deviation.
        :param num_std_dev: The number of standard deviations for the upper and lower bands.
        """
        # Calculate moving average
        self.moving_average("BBAND_MA", window)

        self.data["StdDev"] = self.data["Close"].rolling(window=window).std()
        self.data["UpperBand"] = self.data["BBAND_MA"] + (self.data["StdDev"] * num_std_dev)
        self.data["LowerBand"] = self.data["BBAND_MA"] - (self.data["StdDev"] * num_std_dev)

        print(self.data["StdDev"])
        print(self.data["UpperBand"])
        print(self.data["LowerBand"])
