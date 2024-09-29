#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

from twstockanalyzer.scrapers.history import PriceHistoryFetcher
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.scrapers.analytics import Analysis
from twstockanalyzer.scrapers.strategy import Strategy
import pandas as _pd


class Stock:
    def __init__(self, code: str, suffix: str):
        self.code = code
        self.fetcher = PriceHistoryFetcher(code, suffix)
        self.analysis = Analysis()
        self.strategy = Strategy()

    def cal_statistic(self, df: _pd.DataFrame):
        self.analysis.macd(df=df)
        self.analysis.stochastic(df=df)
        self.analysis.bbands(df=df)
        self.analysis.moving_average(df, "MA5", 5)
        self.analysis.moving_average(df, "MA10", 10)
        self.analysis.moving_average(df, "MA20", 20)
        self.analysis.moving_average(df, "MA40", 40)
        self.analysis.moving_average(df, "MA60", 60)
        self.analysis.moving_average(df, "MA138", 138)

    def download_prices_history_csv(
        self, filter_on: bool = True, download_csv: bool = True
    ):
        if not filter_on:
            self.fetcher.download_csv_with_all_period()

        day_df = self.fetcher.fetch_day_max()
        # check valid volume
        if day_df is None:
            print("day_df is None")
            return
        if day_df["Volume"].count() < 5:
            print("prices data < 5")
            return
        elif day_df["Volume"].tail(5).sum() < 800:
            print("sum latest 5 volume < 800")
            return
        # check price affordable
        if not self.is_in_price_range(day_df["Close"].iloc[-1]):
            close_price = day_df["Close"].iloc[-1]
            print(f"Stock {self.code} ot of price range: {close_price}")
            return

        # filter stock before download
        week_df = self.fetcher.fetch_week_max()
        month_df = self.fetcher.fetch_month_max()
        if week_df is None or month_df is None or day_df is None:
            print(f"Something wrong when fetch data for stock {self.code}")
            return
        self.cal_statistic(day_df)
        self.cal_statistic(week_df)
        self.cal_statistic(month_df)
        is_safe_1, reason1 = self.check_day_week_month_safe_to_buy(
            day_df=day_df, week_df=week_df, month_df=month_df
        )
        if not is_safe_1:
            print(f"Stock {self.code} is unsafe to buy in day, week, month: {reason1}")
            return

        m60_df = self.fetcher.fetch_60_min_series_max()
        m30_df = self.fetcher.fetch_30_min_series_max()
        m15_df = self.fetcher.fetch_15_min_series_max()
        self.cal_statistic(m60_df)
        self.cal_statistic(m30_df)
        self.cal_statistic(m15_df)
        is_safe_2, reason2 = self.check_minute_exist_buy_point(
            m15_df=m15_df, m30_df=m30_df, m60_df=m60_df
        )
        if not is_safe_2:
            print(f"Stock {self.code} is unsafe to buy in 60m, 30m, 15m: {reason2}")
            # return

        self.fetcher.download_csv(
            monthData=month_df,
            weekData=week_df,
            dayData=day_df,
            sixtyMData=m60_df,
            thirtyMData=m30_df,
            fifteenMData=m15_df,
        )
        print(f"finish download {self.code}")

    def check_day_week_month_safe_to_buy(
        self, day_df: _pd.DataFrame, week_df: _pd.DataFrame, month_df: _pd.DataFrame
    ) -> tuple[bool, str]:
        n1, reason_day = self.strategy.do_not_touch(day_df)
        n2, reason_week = self.strategy.do_not_touch(week_df)
        n3, reason_month = self.strategy.do_not_touch(month_df)
        if n1 and n2 and n3:
            return False, (
                f"do_not_touch: day{reason_day}, "
                f"week{reason_week}, "
                f"month{reason_month}"
            )

        if month_df["K9"].iloc[-1] > 86:
            return False, "K9 too high in month"
        if week_df["K9"].iloc[-1] > 86:
            return False, "K9 too high in week"
        elif day_df["K9"].iloc[-1] > 86:
            return False, "K9 too high in day"
        else:
            return True, ""

    def check_minute_exist_buy_point(
        self, m15_df: _pd.DataFrame, m30_df: _pd.DataFrame, m60_df: _pd.DataFrame
    ) -> tuple[bool, str]:
        if (
            m60_df["K9"].dropna().count() <= 0
            or m30_df["K9"].dropna().count() <= 0
            or m15_df["K9"].dropna().count() <= 0
        ):
            return False, "not enough data to check_minute_exist_buy_point"

        if m60_df["K9"].iloc[-1] > 90:
            return False, "K9 too high in 60 min"
        elif m30_df["K9"].iloc[-1] > 86:
            return False, "K9 too high in 30 min"
        elif m15_df["K9"].iloc[-1] > 86:
            return False, "K9 too high in 15 min"
        else:
            return True, ""

    def _test_macd(self, period: str):
        # day_df = self.fetcher.fetch_day_max()
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        file_name = f"{self.code}_{period}"
        period_df = stock_prices_dict[file_name]
        self.cal_statistic(period_df)
        # print(period_df["MACD"])

        # Filter for rows where 'col1' has values
        # creates a new DataFrame df_filtered that contains only the rows from df where the value in column 'col1' is not null.
        filtered_copy = period_df[period_df["MACD"].notnull()].copy()
        self.strategy._draw_macd_curve_to_line(filtered_copy, "MACD")

    def _test_price_line(self, period: str):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        file_name = f"{self.code}_{period}"
        period_60mdf = stock_prices_dict[file_name]
        self.cal_statistic(period_60mdf)
        self.strategy._draw_two_line_closing_to_cross(period_60mdf)

    def is_in_price_range(self, value: int, top: int = 300, bottom: int = 10) -> bool:
        return bottom <= value < top
