#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: strategy for filter out stock buy point
#

import pandas as _pd
import numpy as _np
import matplotlib.pyplot as plt


class Analysis:
    def moving_average(self, df: _pd.DataFrame, header: str, window: int):
        """
        This method computes the moving average of the 'Close' prices over a specified
        window of time and stores the result in a new column within the DataFrame.

        :param header: The name of the column to store the moving average result.
        :param window: The number of periods to use for calculating the moving average.
                        For example, a window of 20 will compute the average over the last
                        20 closing prices.
        """
        df[header] = df["Close"].rolling(window=window).mean()

    def macd(
        self,
        df: _pd.DataFrame,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
    ):
        """
        Calculate the Moving Average Convergence Divergence (MACD) indicator.

        Parameters:
        short_window (int): The span for the short-term EMA (default is 12).
        long_window (int): The span for the long-term EMA (default is 26).
        signal_window (int): The span for the signal line EMA (default is 9).
        """
        df["EMA_SHORT"] = df["Close"].ewm(span=short_window, adjust=False).mean()
        df["EMA_LONG"] = df["Close"].ewm(span=long_window, adjust=False).mean()

        df["DIF"] = df["EMA_SHORT"] - df["EMA_LONG"]
        df["MACD"] = df["DIF"].ewm(span=signal_window, adjust=False).mean()
        df["OSI"] = df["MACD"] - df["DIF"]

    def stochastic(
        self, df: _pd.DataFrame, n: int = 9, k_period: int = 3, d_period: int = 3
    ):
        """
        Calculate the Stochastic Oscillator values (RSV, K9, D9) for a given DataFrame.

        Parameters:
        df : DataFrame
            A pandas DataFrame containing stock df with 'Close', 'High', and 'Low' columns.
        n : int, optional
            The number of periods to consider for calculating the Lowest Low and Highest High (default is 14).
        k_period : int, optional
            The number of periods for the K9 smoothed average of the RSV (default is 3).
        d_period : int, optional
            The number of periods for the D9 smoothed average of K9 (default is 3).

        Returns:
        DataFrame
            A DataFrame containing the Close price, Lowest Low, Highest High, RSV, K9, and D9.
        """
        df["Lowest Low"] = df["Low"].rolling(window=n).min()
        df["Highest High"] = df["High"].rolling(window=n).max()

        df["RSV"] = (
            (df["Close"] - df["Lowest Low"]) / (df["Highest High"] - df["Lowest Low"])
        ) * 100
        df["K9"] = df["RSV"].rolling(window=k_period).mean()
        df["D9"] = df["K9"].rolling(window=d_period).mean()

    def bbands(self, df: _pd.DataFrame, window: int = 16, num_std_dev: int = 2):
        """
        This method calculate Bollinger Bands.
        df : DataFrame
            A pandas DataFrame containing stock df with 'Close', 'High', and 'Low' columns.
        :param window: The number of periods for the moving average and standard deviation.
        :param num_std_dev: The number of standard deviations for the upper and lower bands.
        """
        # Calculate moving average
        self.moving_average(df, "BBAND_MA", window)

        df["StdDev"] = df["Close"].rolling(window=window).std()
        df["BBAND_UpperBand"] = df["BBAND_MA"] + (df["StdDev"] * num_std_dev)
        df["BBAND_LowerBand"] = df["BBAND_MA"] - (df["StdDev"] * num_std_dev)
