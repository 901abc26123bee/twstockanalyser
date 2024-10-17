#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

import pandas as _pd
import numpy as _np

# for child can access parent method
from twstockanalyzer.strategy.base import *
from twstockanalyzer.strategy.macd import MACDIndicatorStrategy


class StrategyPattern(Strategy):
    def __init__(self):
        self.macd_strategy = MACDIndicatorStrategy()

    # 月、週 呈高檔鈍化
    def high_end_stagnation_in_month_and_week_kd(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(
                f"Error: Missing columns when high_end_stagnation_in_month_and_week_kd"
            )
            return

        df[""] = _np.abs(df["K9"] - df["D9"])

    # 強勢股拉回(日)：MACD 紅柱＋零軸上
    def is_pullback_in_a_uptrend_stock_day(self, df: _pd.DataFrame):
        if not self.check_statistic_column(df):
            print(f"Error: Missing columns when is_pullback_in_a_uptrend_stock_day")

    # 月線低檔爆量，上影線
    def high_volume_at_low_prices_level(self, df: _pd.DataFrame):
        max_volume = 0
        max_index = 0
        for i, row in df:
            if row["Volume"] > max_volume:
                max_volume = row["Volume"]
                max_index = i

        # if max_index > 5 and max_index < df["Volume"].dropna().count():

    # macd主升段(過零軸回測再攻)
    def apply_pattern_matcher(
        self,
        day_df: _pd.DataFrame,
        week_df: _pd.DataFrame,
        month_df: _pd.DataFrame,
        m30_df: _pd.DataFrame,
        m60_df: _pd.DataFrame,
    ) -> tuple[bool, set[str]]:
        if not self.check_statistic_column(day_df):
            raise ValueError(f"Error: missing column in day_df.")
        elif not self.check_statistic_column(week_df):
            raise ValueError(f"Error: missing column in week_df.")
        elif not self.check_statistic_column(month_df):
            raise ValueError(f"Error: missing column in month_df.")
        elif not self.check_statistic_column(m60_df):
            raise ValueError(f"Error: missing column in m60_df.")
        elif not self.check_statistic_column(m30_df):
            raise ValueError(f"Error: missing column in m30_df.")

        # check KD
        kd_threshold = 80
        for period, df in zip(
            ["month", "week", "day", "m60_df"], [month_df, week_df, day_df, m60_df]
        ):
            last_k9 = df["K9"].iloc[-1]
            last_D9 = df["D9"].iloc[-1]
            if last_k9 > kd_threshold and last_D9 > kd_threshold:
                return (
                    False,
                    f"K9, D9 too high in {period}, K9: {last_k9}, D9: {last_D9}",
                )

        # check macd
        pass

    # macd/dif 初升段(零軸下接近零軸)
    # 當前級別：macd or dif 零軸下接近零軸且虛線呈上升趨勢，
    #         osc紅柱或弱綠柱或盤整中(趨勢不明)，
    #         kd小於 80，前面有上影線過bband上軌更好(撐開布林通道)
    # 上一級別：macd or dif 零軸下呈上升趨勢，或是在零軸上，
    #         osc紅柱或弱綠柱或盤整中(趨勢不明),
    #         kd小於 80，前面有上影線過bband上軌更好(撐開布林通道)
    def match_macd_first_uptrend_phase_pattern(
        self,
        df: _pd.DataFrame,
        window: int = 20,
    ) -> bool:
        # check for short period
        # 當前級別：macd or dif 零軸下接近零軸且虛線呈上升趨勢，osc紅柱或弱綠柱或盤整中(趨勢不明)，kd小於 80，前面有上影線過bband上軌更好

        # check kd
        if df["K9"] > 80 or df["D9"] > 80:
            return False

        # check macd
        dif = df["DIF"].tail(window).to_numpy()
        macd = df["MACD"].tail(window).to_numpy()
        osc = df["OSC"].tail(window).to_numpy()
        _, macd_trend_set = self.macd_strategy.check_macd_trend(df)
        macd_required_list = [
            constd.MACDTrendEnum.MACD_BELOW_MIDDLE,
            constd.MACDTrendEnum.MACD_CLOSING_MIDDLE_FROM_BELOW,
        ]
        if not all(item in macd_trend_set for item in macd_required_list):
            return False
        if df["MACD"].iloc[-1] > 0:
            return False

        # check osc
        osc_invalid_list = [
            constd.MACDTrendEnum.OSC_GREEN_STRONG,
            constd.MACDTrendEnum.OSC_GREEN_RANGE_LONG,
        ]
        if all(item in macd_trend_set for item in macd_required_list):
            return False

        return True

    # macd/dif 主升段(過零軸回測再攻)
    # 當前級別：macd or dif 零軸上，呈上升趨勢或是由上往下接近零軸，且最新點/低點需高於前一個低點，
    #         osc紅柱或弱綠柱或盤整中(趨勢不明)，
    #         kd小於 80，前面有上影線過bband上軌更好(撐開布林通道)
    # 上一級別：macd or dif 零軸下呈上升趨勢，或是在零軸上，
    #         osc紅柱或弱綠柱或盤整中(趨勢不明),
    #         kd小於 80，前面有上影線過bband上軌更好(撐開布林通道)
    def match_macd_second_main_uptrend_phase_pattern(
        self,
        df: _pd.DataFrame,
        window: int = 40,
    ) -> bool:
        dif = df["DIF"].tail(window).to_numpy()
        macd = df["MACD"].tail(window).to_numpy()
        osc = df["OSC"].tail(window).to_numpy()
        # Find the index where the transition occurs
        # return a list of index right before sign change
        transition_macd = _np.where(_np.diff(_np.sign(macd)) > 0)[0]

        # If there's a transition, get the first index
        macd_cross_index = -1
        if transition_macd.size > 0:
            macd_cross_index = transition_macd[-1]

        # Check all elements after macd_cross_index are > 0
        macd_positive_after_sign_change = _np.all(macd[macd_cross_index + 1 :] > 0)
        if not macd_positive_after_sign_change:
            return False
        _, macd_trend_set = self.macd_strategy.check_macd_trend(df)
        macd_required_list = [
            constd.MACDTrendEnum.MACD_BELOW_MIDDLE,
            constd.MACDTrendEnum.MACD_LATEST_UPTREND,
        ]
        if not any(item in macd_trend_set for item in macd_required_list):
            return False
        if df["MACD"].iloc[-1] > 0:
            return False

        #

    # 上一級別：
    # required:
    #     macd or dif 零軸下呈上升趨勢，或是底底高，或是在零軸上
    #     osc紅柱或弱綠柱或盤整中(趨勢不明，需 latest 紅綠柱範圍和高度差不多),
    #     kd小於 80，有黃金交叉或是K9>D9
    # better to have:
    #     前面有上影線過bband上軌更好(撐開布林通道)
    #     布林有開口，或是布林縮口
    def valid_long_period_pattern_to_protect_short_period(
        self,
        df: _pd.DataFrame,
    ) -> bool:
        pass

    # 前面有上影線突破 bband 上軌
    def find_high_prices_exceed_bband_upper_bound(
        self, df: _pd.DataFrame, window: int = 20
    ) -> bool:
        candlestick_body = (
            df["Close"].tail(window) - df["Open"].tail(window)
        ).to_numpy()
        candlestick_upper_shadow = (
            df["High"].tail(window) - df["Close"].tail(window)
        ).to_numpy()
        bband_upper = df["BB_Upper"].tail(window).to_numpy()

        pass

    # 上升趨勢中中，拉回買點
    # 當前級別:
    #   macd上升趨勢(需底底高)時，出現:
    #       1. kd死叉
    #       2. DIF 向下
    #       3. OSC弱綠柱或是紅著縮腳
    # 上一級別：find_macd_second_main_uptrend_phase
    def find_backtrack_buy_point_during_uptrend(self):
        pass
