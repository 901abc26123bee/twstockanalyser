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

    def download_stocks_prices_history_csv(self):
        for code in tpex:
            # if int(code) == 1336:
            stock = Stock(code, TPEX_STOCK_SUFFIX_TWO)
            err = stock.download_prices_history_csv(filter_on=True, download_csv=True)
            if err == "":
                print(f"finish download {code}")
            else:
                print(f"failed to download {code}, err: {err}")

        for code in twse:
            # if 1000 <= int(code) <= 1200:
            stock = Stock(code, TWSE_STOCK_SUFFIX_TW)
            stock.download_prices_history_csv(filter_on=True, download_csv=True)
            if err == "":
                print(f"finish download {code}")
            else:
                print(f"failed to download {code}, err: {err}")

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

            res_dict = stock.check_exist_buy_point(
                day_df=period_dfs["day"],
                week_df=period_dfs["week"],
                month_df=period_dfs["month"],
                m60_df=period_dfs["60m"],
                m30_df=period_dfs["30m"],
                m15_df=period_dfs["15m"],
            )

            if all(res_dict.values()):
                print(f"{code} has buy point: {res_dict}")
