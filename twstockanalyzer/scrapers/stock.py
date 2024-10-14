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
    ) -> str:
        if not filter_on:
            self.fetcher.download_csv_with_all_period()

        day_df = self.fetcher.fetch_day_max()
        # check valid volume
        if day_df is None:
            return "day_df is None"
        if day_df["Volume"].count() < 5:
            return "prices data < 5"
        if day_df["Volume"].tail(5).sum() < 1000:
            return "sum latest 5 volume < 1000"
        # check price affordable
        if not self.is_in_price_range(day_df["Close"].iloc[-1]):
            close_price = day_df["Close"].iloc[-1]
            return f"Stock {self.code} ot of price range: {close_price}"

        # filter stock before download
        week_df = self.fetcher.fetch_week_max()
        month_df = self.fetcher.fetch_month_max()
        m60_df = self.fetcher.fetch_60_min_series_max()
        if week_df is None or month_df is None or day_df is None or m60_df is None:
            return f"Something wrong when fetch data for stock {self.code}"

        self.cal_statistic(m60_df)
        self.cal_statistic(day_df)
        self.cal_statistic(week_df)
        self.cal_statistic(month_df)
        is_safe, reason = self.check_stock_safe_to_buy(
            day_df=day_df, week_df=week_df, month_df=month_df, m60_df=m60_df
        )
        if not is_safe:
            return f"Stock {self.code} is unsafe to buy in day, week, month: {reason}"

        m30_df = self.fetcher.fetch_30_min_series_max()
        m15_df = self.fetcher.fetch_15_min_series_max()
        self.cal_statistic(m30_df)
        self.cal_statistic(m15_df)

        self.fetcher.download_csv(
            monthData=month_df,
            weekData=week_df,
            dayData=day_df,
            sixtyMData=m60_df,
            thirtyMData=m30_df,
            fifteenMData=m15_df,
        )

        return ""

    def check_stock_safe_to_buy(
        self,
        day_df: _pd.DataFrame,
        week_df: _pd.DataFrame,
        month_df: _pd.DataFrame,
        m60_df: _pd.DataFrame,
    ) -> tuple[bool, str]:
        # step1: filter out stocks with down trend prices(日週月日落)
        n1, reason_day = self.ma_strategy.do_not_touch(day_df)
        if n1:
            return False, f"do_not_touch, day: {reason_day}."
        n2, reason_week = self.ma_strategy.do_not_touch(week_df)
        if n2:
            return False, f"do_not_touch, day: {reason_week}."
        n3, reason_month = self.ma_strategy.do_not_touch(month_df)
        if n3:
            return False, f"do_not_touch, day: {reason_month}."

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
            if last_k9 > 90 or last_D9 > 90:
                return (
                    False,
                    f"K9, D9 too high in {period}, K9: {last_k9}, D9: {last_D9}",
                )

        # step3: filter out macd strong downward
        month_macd_up, month_macd_res = self.macd_strategy.check_macd_trend(month_df)
        week_macd_up, week_macd_res = self.macd_strategy.check_macd_trend(week_df)
        day_macd_up, day_macd_res = self.macd_strategy.check_macd_trend(day_df)
        m60_macd_up, m60_macd_res = self.macd_strategy.check_macd_trend(m60_df)
        if (
            constd.MACD_BELOW_MIDDLE in month_macd_res
            and constd.MACD_BELOW_MIDDLE in week_macd_res
            and constd.MACD_BELOW_MIDDLE in day_macd_res
        ):
            return (
                False,
                f"Unsafe in to buy because macd of month, week, day all below middle",
            )

        unsafe_macd_cond = [
            constd.MACD_BELOW_MIDDLE,
            constd.MACD_DOWNTREND_AGGRESSIVE,
        ]
        if (
            constd.MACD_DO_NOT_TOUCH in week_macd_res
            and constd.MACD_DO_NOT_TOUCH in day_macd_res
        ):
            return (
                False,
                f"Unsafe in week_macd_res and day_macd_res: week: {week_macd_res},  day: {day_macd_res}.",
            )
        elif (
            constd.MACD_DO_NOT_TOUCH in day_macd_res
            and constd.MACD_DO_NOT_TOUCH in m60_macd_res
        ):
            return (
                False,
                f"Unsafe in day_macd_res and m60_macd_res: day: {day_macd_res}, m60: {m60_macd_res}.",
            )
        elif set(unsafe_macd_cond).issubset(week_macd_res) and set(
            unsafe_macd_cond
        ).issubset(day_macd_res):
            return (
                False,
                f"Unsafe in week_macd_res and day_macd_res: week:{week_macd_res}, day:{day_macd_res}.",
            )
        elif not week_macd_up and not day_macd_up and not m60_macd_up:
            return False, f"DownTrend in both week, day and 60min."

        # step4: check ma
        week_ma_relation = self.ma_strategy.check_ma_relation(week_df)
        day_ma_relation = self.ma_strategy.check_ma_relation(day_df)
        m60_ma_relation = self.ma_strategy.check_ma_relation(m60_df)
        ma_unsafe_cond = [
            constd.MA40_BELOW_MA138,
            constd.MA5_BELOW_MA138,
            constd.MA5_BELOW_MA40,
            constd.MA5_BELOW_LEAVING_MA138,
            constd.MA5_BELOW_LEAVING_MA40,
            constd.MA40_BELOW_LEAVING_MA138,
        ]
        if set(ma_unsafe_cond).issubset(week_ma_relation):
            return False, f"Unsafe to buy due to week_ma_relation: {week_ma_relation}."
        elif set(ma_unsafe_cond).issubset(day_ma_relation):
            return False, f"Unsafe to buy due to day_ma_relation: {day_ma_relation}."
        elif set(ma_unsafe_cond).issubset(day_ma_relation):
            return False, f"Unsafe to buy due to m60_ma_relation: {m60_ma_relation}."

        # osc柱狀圖 < 0（比之前紅著還要長） 且 macd 下降趨勢（長） 且 價格底底低 ，沒有 w底 ，或是(kd > 90)
        # 且 (上一級osc柱狀圖<0 且 且 沒收腳 macd < 0 且 macd 下降趨勢（長）) ，或是(kd > 90)
        # 且 (上一級osc柱狀圖<0 且 沒收腳 且 macd < 0 且 macd 下降趨勢（長）) ，或是(kd > 90)

        # step5: tag stocks with buy point

        return True, f"day: {day_macd_res}, week: {week_macd_res}"

    def check_exist_buy_point(
        self,
        day_df: _pd.DataFrame,
        week_df: _pd.DataFrame,
        month_df: _pd.DataFrame,
        m15_df: _pd.DataFrame,
        m30_df: _pd.DataFrame,
        m60_df: _pd.DataFrame,
    ) -> tuple[dict]:

        res_dict = {}

        # step1: check close prices in week/day
        week_close_can_buy = False
        if (
            week_df["High"].iloc[-1] > week_df["MA10"].iloc[-1]
            or week_df["High"].iloc[-1] >= week_df["MA5"].iloc[-1]
            or week_df["MACD"].iloc[-1] > 0
        ):
            week_close_can_buy = True

        res_dict["week_close_can_buy"] = week_close_can_buy

        # step2: filter out stocks with excessively high KD in m60, m30
        kd_can_buy = True
        kd_threshold = 80
        for df in [m60_df, m30_df]:
            last_k9 = df["K9"].iloc[-1]
            last_D9 = df["D9"].iloc[-1]
            if last_k9 > kd_threshold and last_D9 > kd_threshold:
                kd_can_buy = False
        res_dict["kd_can_buy"] = kd_can_buy

        # step3: check macd in week/day/60m/30m (strict cond)
        macd_not_all_below_middle = True
        macd_long_protect_short_can_buy = False
        month_macd_up, month_macd_set = self.macd_strategy.check_macd_trend(month_df)
        week_macd_up, week_macd_set = self.macd_strategy.check_macd_trend(week_df)
        day_macd_up, day_macd_set = self.macd_strategy.check_macd_trend(day_df)
        m60_macd_up, m60_macd_set = self.macd_strategy.check_macd_trend(m60_df)
        m30_macd_up, m30_macd_set = self.macd_strategy.check_macd_trend(m30_df)
        if (
            constd.MACD_BELOW_MIDDLE in month_macd_set
            and constd.MACD_BELOW_MIDDLE in week_macd_set
            and constd.MACD_BELOW_MIDDLE in day_macd_set
        ):
            macd_not_all_below_middle = False
        res_dict["macd_not_all_below_middle"] = macd_not_all_below_middle

        macd_can_buy_if_any_match = [
            constd.MACD_ABOVE_MIDDLE,
            constd.MACD_LATEST_UPTREND,
            constd.MACD_UPTREND_BACKTEST,
            constd.MACD_CLOSING_MIDDLE_FROM_BOTTOM,
        ]
        if (
            constd.MACD_ABOVE_MIDDLE in week_macd_set
            or constd.MACD_ABOVE_MIDDLE in day_macd_set
        ) and (
            any(item in m60_macd_set for item in macd_can_buy_if_any_match)
            or any(item in m30_macd_set for item in macd_can_buy_if_any_match)
        ):
            macd_long_protect_short_can_buy = True
        res_dict["macd_long_protect_short_can_buy"] = macd_long_protect_short_can_buy

        # step4: check ma in week/day/60m/30m
        ma60_can_buy = False
        ma30_can_buy = False
        week_ma_set = self.ma_strategy.check_ma_relation(m60_df)
        day_ma_set = self.ma_strategy.check_ma_relation(m60_df)
        m60_ma_set = self.ma_strategy.check_ma_relation(m60_df)
        m30_ma_set = self.ma_strategy.check_ma_relation(m30_df)
        ma_valid_condition = [
            # closing from buttom
            constd.MA40_CLOSING_TO_MA138_FROM_BOTTOM,
            constd.MA5_CLOSING_TO_MA138_FROM_BOTTOM,
            constd.MA5_CLOSING_TO_MA40_FROM_BOTTOM,
            # golden cross
            constd.MA40_CROSS_OVER_MA138_UPWARD,
            constd.MA5_CROSS_OVER_MA138_UPWARD,
            constd.MA5_CROSS_OVER_MA40_UPWARD,
            # closing from above
            constd.MA40_CLOSING_TO_MA138_FROM_ABOVE,
            constd.MA5_CLOSING_TO_MA138_FROM_ABOVE,
            constd.MA5_CLOSING_TO_MA40_FROM_ABOVE,
            # above
            constd.MA5_ABOVE_MA138,
            constd.MA40_ABOVE_MA138,
        ]
        if any(item in m60_ma_set for item in ma_valid_condition):
            ma60_can_buy = True
        if any(item in m30_ma_set for item in ma_valid_condition):
            ma30_can_buy = True

        res_dict["ma60_can_buy"] = ma60_can_buy
        res_dict["ma30_can_buy"] = ma30_can_buy
        return res_dict

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
