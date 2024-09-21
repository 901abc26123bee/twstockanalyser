#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage:
#

from twstockanalyzer.scrapers.history import PriceHistoryFetcher
from twstockanalyzer.scrapers.analytics import Analysis


class Stock:
    def __init__(self, code: str):
        self.code = code
        self.fetcher = PriceHistoryFetcher(code)
        self.analysis = Analysis(self.fetcher.fetch_month_max())

    def calculate_ma(self, header: str, window: int):
        self.analysis.moving_average("5MA", 5)

    def download_prices_history_csv(self):
        self.fetcher.download_csv_with_all_period()

    def troubleshot(self):
        self.analysis.macd()
        self.analysis.kdj()
        self.analysis.bbands()
        self.analysis.moving_average("MA5", 5)