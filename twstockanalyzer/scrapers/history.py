#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

import os
import yfinance as yf
import pandas as pd

TW_STOCK_SUFFIX = ".TW" 
STOCK_DATA_FOLDER = "./web/stock_data/"
STOCK_DATA_MONTHS_SUFFIX = "_months"
STOCK_DATA_WEEKS_SUFFIX = "_weeks"
STOCK_DATA_DAYS_SUFFIX = "_days"
STOCK_DATA_60_M_SUFFIX = "_60_m"
STOCK_DATA_30_M_SUFFIX = "_30_m"
STOCK_DATA_15_M_SUFFIX = "_15_m"
CSV_EXTENSION = ".csv"

class PriceHistoryFetcher(object):
    def __init__(self):
        pass

    def initial_csv_data(self, code: str):
        self.code = code
        # defines the taiwan stock symbol ex: '2330.TW'
        self._symbol = code + TW_STOCK_SUFFIX
        self.fetch_month_max()
        self.fetch_week_max()
        self.fetch_day_max()
        self.fetch_60_min_series()
        self.fetch_30_min_series()
        self.fetch_15_min_series()

    def fetch_month_max(self):
        data = yf.download(self._symbol, interval="1mo", period="max")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_MONTHS_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def fetch_week_max(self):
        data = yf.download(self._symbol, interval="1wk", period="2y")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_WEEKS_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def fetch_day_max(self):
        data = yf.download(self._symbol, interval="1d", period="2y")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_DAYS_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def fetch_60_min_series(self):
        data = yf.download(self._symbol, interval="60m", period="1mo")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_60_M_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def fetch_30_min_series(self):
        data = yf.download(self._symbol, interval="30m", period="1mo")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_30_M_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def fetch_15_min_series(self):
        data = yf.download(self._symbol, interval="15m", period="5d")
        fileName = "%s%s%s" % (self.code, STOCK_DATA_15_M_SUFFIX, CSV_EXTENSION)
        self._download_csv(data, fileName)

    def _download_csv(self, data, fileName):
        df_list = []
        df_list.append(data)
        df = pd.concat(df_list)
        outputFolder = os.path.join(STOCK_DATA_FOLDER, self.code)
        # create the directory if it doesn't exist
        os.makedirs(outputFolder, exist_ok=True)
        df.to_csv(os.path.join(outputFolder, fileName))

    def _make_datatuple(self, data):
        pass

    def purify(self, original_data):
        pass
