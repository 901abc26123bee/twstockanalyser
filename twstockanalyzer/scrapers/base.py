#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

import time
import pandas as _pd
from twstockanalyzer.scrapers.stock import Stock
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.strategy.const import TWSE_STOCK_SUFFIX_TW, TPEX_STOCK_SUFFIX_TWO

try:
    from twstockanalyzer.codes import tpex, twse
except ImportError as e:
    if e.name == "lxml":
        raise e
    from codes import tpex, twse


class BaseFetcher:
    def __init__(self):
        self._tpex_code_set = set()
        # self._twse_code_set = set()
        for c in tpex:
            self._tpex_code_set.add(c)
        # for c in twse:
        #     self._twse_code_set.add(c)

    def download_stocks_prices_history_csv(self, interval: int = 10, wait: int = 0.5):
        count = 0
        for code in tpex:
            # if int(code) > 6016:
            count += 1
            if count % interval == 0:
                time.sleep(wait)
            stock = Stock(code, TPEX_STOCK_SUFFIX_TWO)
            stock.download_prices_history_csv(filter_on=True, download_csv=True)

        count = 0
        for code in twse:
            # if 1000 <= int(code) <= 1200:
            count += 1
            if count % interval == 0:
                time.sleep(wait)
            stock = Stock(code, TWSE_STOCK_SUFFIX_TW)
            stock.download_prices_history_csv(filter_on=True, download_csv=True)

    def _test_macd(self, code: str, period: str):
        suffix_type = TWSE_STOCK_SUFFIX_TW
        if code in self._tpex_code_set:
            suffix_type = TPEX_STOCK_SUFFIX_TWO

        stock = Stock(code, suffix_type)
        stock._test_macd(period)

    def _test_ma_lines(self, code: str, period: str):
        suffix_type = TWSE_STOCK_SUFFIX_TW
        if code in self._tpex_code_set:
            suffix_type = TPEX_STOCK_SUFFIX_TWO

        stock = Stock(code, suffix_type)
        stock._test_price_line(period)

    def load_stocks_prices_from_csv_files(self):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        print(stock_prices_dict.keys())

        day_4540 = stock_prices_dict["4540_day"]
        stock = Stock("4540")
        stock.cal_statistic(day_4540)

    def apply_strategy_collections(self):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        # Create a set to collect the numbers
        number_set = set()
        period_set = {"day", "month", "week", "60m", "30m", "15m"}

        # Loop through each stock files in the dictionary stock_data
        for key in stock_prices_dict.keys():
            # Split the key to separate the number from the time frame
            parts = key.split("_")

            # Check if the key has the expected format
            if len(parts) == 2 and parts[1] in period_set:
                try:
                    # Convert the number part to a float or int and add it to the set
                    number_set.add(int(parts[0]))  # Use float() for decimal numbers
                except ValueError:
                    # Handle the case where conversion fails (if necessary)
                    print(f"Error: {ValueError}")
                    continue

        # Sort collected stock code
        sorted_numbers = sorted(number_set)

        # apply strategy for all collected stock and apply strategy
        period_dfs = {
            "day": _pd.DataFrame(),
            "week": _pd.DataFrame(),
            "month": _pd.DataFrame(),
            "60m": _pd.DataFrame(),
            "30m": _pd.DataFrame(),
            "15m": _pd.DataFrame(),
        }
        for code in sorted_numbers:
            suffix_type = TWSE_STOCK_SUFFIX_TW
            if code in self._tpex_code_set:
                suffix_type = TPEX_STOCK_SUFFIX_TWO

            stock = Stock(str(code), suffix_type)

            print("------------------------------")
            for period in period_set:
                file_name = f"{code}_{period}"
                period_df = stock_prices_dict[file_name]
                stock.cal_statistic(period_df)
                period_dfs[period] = period_df

            safe_to_buy_day, reason_day = stock.check_day_week_month_safe_to_buy(
                day_df=period_dfs["day"],
                week_df=period_dfs["week"],
                month_df=period_dfs["month"],
            )
            if not safe_to_buy_day:
                print(f"Unsafe to buy in day, week, month: {code} : {reason_day}")

            safe_to_buy_minute, reason_minute = stock.check_minute_safe_to_buy(
                m15_df=period_dfs["15m"],
                m30_df=period_dfs["30m"],
                m60_df=period_dfs["60m"],
            )
            if not safe_to_buy_minute:
                print(f"Unsafe to buy in minute: {code}: {reason_minute}")

            if safe_to_buy_day and safe_to_buy_minute:
                dd9 = period_dfs["day"]["D9"].iloc[-1]
                wd9 = period_dfs["week"]["D9"].iloc[-1]
                if dd9 < 82 and wd9 < 82:
                    print(
                        f"$$$ Safe to buy {file_name}: day: {reason_day}, minute: {reason_minute}, dd9: {dd9}, wd9: {wd9}"
                    )

            # macd
            # b, reason = stock.strategy.check_macd_trend(period_prices)
            # osc_desc = stock.strategy.check_osc_stick_heigh(period_prices)

            # # print(f"{file_name}: {b}, {reason}")
            # stock.strategy.check_ma(period_prices)
            # if period == "day" or period == "week" or period == "month":
            #     if b or period_prices["OSC"].iloc[-1] > 0:
            #         print(f"{file_name}: {b}, {reason}, {osc_desc}")
            # if period == "60m" or period == "30m" or period == "15m":
            #     if period_prices["MA40"].iloc[-1] > period_prices["MA138"].iloc[-1]:
            #         print(f"{file_name}: ma40 > ma138")
            #     if b:
            #         print(f"{file_name}: {b}, {reason}, {osc_desc}")
