#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

from twstockanalyzer.scrapers.history import PriceHistoryFetcher
from twstockanalyzer.scrapers.analytics import Analysis
from twstockanalyzer.scrapers.strategy import Strategy
import pandas as _pd


class Stock:
    def __init__(self, code: str):
        self.code = code
        self.fetcher = PriceHistoryFetcher(code)
        self.analysis = Analysis()
        self.strategy = Strategy()

    def download_prices_history_csv(self):
        self.fetcher.download_csv_with_all_period()

    def check_week_day_month_safe_to_buy(self):
        month_df = self.fetcher.fetch_month_max()
        week_df = self.fetcher.fetch_week_max()
        day_df = self.fetcher.fetch_day_max()

    def check_minute_exist_buy_point(self):
        m60_df = self.fetcher.fetch_60_min_series_max()
        m30_df = self.fetcher.fetch_30_min_series_max()
        m15_df = self.fetcher.fetch_15_min_series_max()

    def cal_statistic(self, df: _pd.DataFrame):
        self.analysis.macd(df=df)
        self.analysis.stochastic(df=df)
        self.analysis.bbands(df=df)
        self.analysis.moving_average(df, "MA5", 5)
        self.analysis.moving_average(df, "MA10", 10)
        self.analysis.moving_average(df, "MA40", 40)
        self.analysis.moving_average(df, "MA60", 60)
        self.analysis.moving_average(df, "MA138", 138)

    def _test(self):
        day_df = self.fetcher.fetch_day_max()
        self.analysis.macd(df=day_df)
        print(day_df["MACD"])

        # Filter for rows where 'col1' has values
        # creates a new DataFrame df_filtered that contains only the rows from df where the value in column 'col1' is not null.
        filtered_copy = day_df[day_df["MACD"].notnull()].copy()
        self.strategy._draw_curve_to_line(filtered_copy, "MACD")
