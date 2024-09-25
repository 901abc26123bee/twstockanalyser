#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

from twstockanalyzer.scrapers.stock import Stock
from twstockanalyzer.scrapers.history import PriceHistoryLoader

try:
    from twstockanalyzer.codes import codes
except ImportError as e:
    if e.name == "lxml":
        raise e
    from codes import codes


class BaseFetcher:
    def __init__(self):
        self.raw_data = []
        self.data = []

    def download_stocks_prices_history_csv(self):
        for code in codes:
            if code == "4540":
                stock = Stock(code)
                stock.download_prices_history_csv()

    def _test(self):
        stock = Stock("4540")
        stock._test()

    def filter_stock_show_buy_point(self):
        for code in codes:
            if 6000 <= int(code) <= 8000:
                stock = Stock(code)
                print()

    def load_stocks_prices_from_csv_files(self):
        loader = PriceHistoryLoader()
        stock_prices_dict = loader.load_from_downloaded_csv()
        print(stock_prices_dict.keys)
