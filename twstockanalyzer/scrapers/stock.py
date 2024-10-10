#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

import pandas as _pd
from twstockanalyzer.scrapers.history import PriceHistoryFetcher
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.scrapers.analytics import Analysis
from twstockanalyzer.strategy.ma import MovingAverageStrategy
from twstockanalyzer.strategy.macd import MACDIndicatorStrategy
from twstockanalyzer.strategy.plot import StrategyPlot
import twstockanalyzer.strategy.const as constd


class Stock:
    def __init__(self, code: str, suffix: str):
        self.code = code
        self.fetcher = PriceHistoryFetcher(code, suffix)
        self.analysis = Analysis()
        self.ma_strategy = MovingAverageStrategy()
        self.macd_strategy = MACDIndicatorStrategy()
        self._strategy_plot = StrategyPlot()

    def cal_statistic(self, df: _pd.DataFrame):
        self.analysis.macd(df=df)
        self.analysis.stochastic(df=df)
        self.analysis.bbands(df=df)
        self.analysis.moving_average(df, "MA5", 5)
        self.analysis.moving_average(df, "MA10", 10)
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
        is_safe_2, reason2 = self.check_minute_safe_to_buy(
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
        # step1: filter out stocks with down trend prices(日週月日落)
        n1, reason_day = self.ma_strategy.do_not_touch(day_df)
        n2, reason_week = self.ma_strategy.do_not_touch(week_df)
        n3, reason_month = self.ma_strategy.do_not_touch(month_df)
        if n1 and n2 and n3:
            return False, (
                f"do_not_touch: day{reason_day}, "
                f"week{reason_week}, "
                f"month{reason_month}"
            )

        # step2: filter out stocks with excessively high KDs
        if (
            month_df["K9"].dropna().count() <= 0
            or week_df["K9"].dropna().count() <= 0
            or day_df["K9"].dropna().count() <= 0
        ):
            return False, "not enough data to check_minute_exist_buy_point"
        for period, df in zip(["month", "week", "day"], [month_df, week_df, day_df]):
            last_k9 = df["K9"].iloc[-1]
            last_D9 = df["D9"].iloc[-1]
            if last_k9 > 88 or last_D9 > 89:
                return (
                    False,
                    f"K9, D9 too high in {period}: K9: {last_k9}, D9: {last_D9}",
                )

        # step3: filter out macd strong download
        week_macd_up, week_macd_res = self.macd_strategy.check_macd_trend(week_df)
        day_macd_up, day_macd_res = self.macd_strategy.check_macd_trend(day_df)
        unsafe_macd_cond = [
            constd.MACD_BELOW_MIDDLE,
            constd.MACD_SHOW_DOWN_DOWN_TREND,
        ]

        if constd.MACD_DO_NOT_TOUCH in week_macd_res:
            return False, f"failed macd check for week_df: {week_macd_res}"
        elif set(unsafe_macd_cond).issubset(week_macd_res) and set(
            unsafe_macd_cond
        ).issubset(day_macd_res):
            return False, f"failed macd check for week_df: {week_macd_res}"

        # if constd.MACD_DO_NOT_TOUCH in day_macd_res:
        #     return False, f"failed macd check for day_macd_res: {day_df}"
        # elif (
        #     constd.MACD_SHOW_DOWN_TREND in day_macd_res
        #     and constd.MACD_SHOW_DOWN_TREND in day_macd_res
        # ):
        #     return (
        #         False,
        #         f"failed macd check for day_macd_res: {constd.MACD_SHOW_DOWN_TREND} in both day and week",
        #     )

        # step4: check ma
        # osc柱狀圖 < 0（比之前紅著還要長） 且 macd 下降趨勢（長） 且 價格底底低 ，沒有 w底 ，或是(kd > 90)
        # 且 (上一級osc柱狀圖<0 且 且 沒收腳 macd < 0 且 macd 下降趨勢（長）) ，或是(kd > 90)
        # 且 (上一級osc柱狀圖<0 且 沒收腳 且 macd < 0 且 macd 下降趨勢（長）) ，或是(kd > 90)

        # step5: tag stocks with buy point

        return (
            week_macd_up and day_macd_up
        ), f"day: {day_macd_res}, week: {week_macd_res}"

    def check_minute_safe_to_buy(
        self, m15_df: _pd.DataFrame, m30_df: _pd.DataFrame, m60_df: _pd.DataFrame
    ) -> tuple[bool, str]:
        # filter out stocks with excessively high KDs
        if (
            m60_df["K9"].dropna().count() <= 0
            or m30_df["K9"].dropna().count() <= 0
            or m15_df["K9"].dropna().count() <= 0
        ):
            return False, "not enough data to check_minute_exist_buy_point"
        for period, df in zip(["60m", "30m", "15m"], [m60_df, m30_df, m15_df]):
            last_k9 = df["K9"].iloc[-1]
            last_D9 = df["D9"].iloc[-1]
            if last_k9 > 88 or last_D9 > 88:
                return (
                    False,
                    f"K9, D9 too high in {period}: K9: {last_k9}, D9: {last_D9}",
                )

        safe_to_buy = False
        # step3: filter out macd strong download
        m60_macd_up, m60_macd_res = self.macd_strategy.check_macd_trend(m60_df)
        m30_macd_up, m30_macd_res = self.macd_strategy.check_macd_trend(m30_df)
        bad_cond_1 = [
            constd.MACD_BELOW_MIDDLE,
            constd.MACD_SHOW_DOWN_DOWN_TREND,
        ]
        bad_cond_2 = [
            constd.MACD_SHOW_DOWN_TREND,
            constd.MACD_BELOW_MIDDLE,
        ]
        if constd.MACD_DO_NOT_TOUCH in m60_macd_res:
            return False, f"failed macd check for 60 min: {m60_macd_res}"
        elif set(bad_cond_1).issubset(m60_macd_res):
            return False, f"failed macd check for 60 min: {m60_macd_res}"

        if constd.MACD_DO_NOT_TOUCH in m30_macd_res:
            return False, f"failed macd check for 30 min: {m30_macd_res}"
        elif set(bad_cond_2).issubset(m30_macd_res) and set(bad_cond_2).issubset(
            m60_macd_res
        ):
            return (
                False,
                f"failed macd check for 30 min: {constd.MACD_SHOW_DOWN_TREND} in 60 min and 30 min",
            )

        # check ma
        m60_ma_set = self.ma_strategy.check_ma(m60_df)
        m30_ma_set = self.ma_strategy.check_ma(m30_df)
        if (
            constd.MA40_ABOVE_MA138 in m60_ma_set
            # or constd.MA40_ABOVE_LEAVING_MA138 in m60_ma_set
            # or constd.MA40_CROSS_OVER_MA138_UPWARD in m60_ma_set
            or constd.MA40_ABOVE_MA138 in m30_ma_set
            # or constd.MA40_ABOVE_LEAVING_MA138 in m30_ma_set
            # or constd.MA40_CROSS_OVER_MA138_UPWARD in m30_ma_set
        ):
            safe_to_buy = True

        return (
            (safe_to_buy and m60_macd_up and m30_macd_up),
            f"60min macd: {m60_macd_res}, 30min macd: {m30_macd_res}, 60min 40ma: {m60_ma_set}, 30min 40ma {m30_ma_set}",
        )

    # def check_day_exist_buy_point():
    #     pass

    # def check_minute_exist_buy_point():
    #     pass

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
        self._strategy_plot._draw_macd_curve_to_line(filtered_copy, "MACD")

    def _test_price_line(self, period: str):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        file_name = f"{self.code}_{period}"
        period_60mdf = stock_prices_dict[file_name]
        self.cal_statistic(period_60mdf)
        self._strategy_plot._draw_two_line_closing_to_cross(period_60mdf)

    def is_in_price_range(self, value: int, top: int = 300, bottom: int = 10) -> bool:
        return bottom <= value < top

    # minute(do not touch condition)
    # macd臨軸下且綠柱,且(macd沒有上升趨勢 or 價格底底低 or 沒有 w底)，或是(kd > 90)
    # 且 (上一級osc柱狀圖<0且macd < 0) or (40 ma < 138 ma and 40 ma 扣高)
    # macd臨軸上且綠柱且下降趨勢，綠柱,或是(kd > 90)，
    # 且 (上一級osc柱狀圖<0 且 macd < 0 且 macd 下降趨勢（長）) or (40 ma < 138 ma and 40 ma 扣高)
