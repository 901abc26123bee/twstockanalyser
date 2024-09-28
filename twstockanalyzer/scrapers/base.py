#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

from twstockanalyzer.scrapers.stock import Stock
from twstockanalyzer.scrapers.history import PriceHistoryLoader
from twstockanalyzer.scrapers.const import TWSE_STOCK_SUFFIX_TW, TPEX_STOCK_SUFFIX_TWO

try:
    from twstockanalyzer.codes import tpex, twse
except ImportError as e:
    if e.name == "lxml":
        raise e
    from codes import tpex, twse


class BaseFetcher:
    def __init__(self):
        pass

    def download_stocks_prices_history_csv(self):
        for code in tpex:
            stock = Stock(code, TPEX_STOCK_SUFFIX_TWO)
            stock.download_prices_history_csv(filter_on=True, download_csv=True)
        for code in twse:
            # if 1000 <= int(code) <= 1200:
            stock = Stock(code, TWSE_STOCK_SUFFIX_TW)
            stock.download_prices_history_csv(filter_on=True, download_csv=True)

    def _test(self, code: str):
        suffix_type = TWSE_STOCK_SUFFIX_TW
        for c in tpex:
            if code == c:
                suffix_type = TPEX_STOCK_SUFFIX_TWO
                break

        stock = Stock(code, suffix_type)
        stock._test("day")

    def load_stocks_prices_from_csv_files(self):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        print(stock_prices_dict.keys())

        day_4540 = stock_prices_dict["4540_day"]
        stock = Stock("4540")
        stock.cal_statistic(day_4540)
