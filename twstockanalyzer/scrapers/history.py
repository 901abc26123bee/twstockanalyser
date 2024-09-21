#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

import os
import yfinance as _yf
import pandas as _pd
from typing import Optional
from collections import namedtuple as _namedtuple
from twstockanalyzer.scrapers.const import (
    TW_STOCK_SUFFIX,
    STOCK_DATA_FOLDER,
    CSV_EXTENSION,
)

STOCK_DATA_MONTHS_SUFFIX = "_months"
STOCK_DATA_WEEKS_SUFFIX = "_weeks"
STOCK_DATA_DAYS_SUFFIX = "_days"
STOCK_DATA_60_M_SUFFIX = "_60m"
STOCK_DATA_30_M_SUFFIX = "_30m"
STOCK_DATA_15_M_SUFFIX = "_15m"


DATA_TUPLE = _namedtuple(
    "Data",
    [
        "Datetime",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ],
)


class PriceHistoryFetcher:
    def __init__(self, code: str, rounding: bool = True):
        self._rounding = rounding
        self.code = code
        # defines the taiwan stock symbol ex: '2330.TW'
        self._symbol = code + TW_STOCK_SUFFIX

    def troubleshot(self) -> Optional[_pd.DataFrame]:
        monthData = self.fetch_month_max()
        # print(monthData.columns)
        # print(self._make_datatuple(monthData))
        return monthData

    def download_csv_with_all_period(self):
        monthData = self.fetch_month_max()
        weekData = self.fetch_week_max()
        dayData = self.fetch_day_max()
        sixtyMData = self.fetch_60_min_series_max()
        thirtyMData = self.fetch_30_min_series_max()
        fifteenMData = self.fetch_15_min_series_max()
        self.download_csv(
            monthData=monthData,
            weekData=weekData,
            dayData=dayData,
            sixtyMData=sixtyMData,
            thirtyMData=thirtyMData,
            fifteenMData=fifteenMData,
        )

    def fetch_month_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="1mo", period="max"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 60m")
            return None
        return _pd.DataFrame(data)

    def fetch_week_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="1wk", period="5y"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 60m")
            return None
        return _pd.DataFrame(data)

    def fetch_day_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="1d", period="2y"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 60m")
            return None
        return _pd.DataFrame(data)

    def fetch_60_min_series_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="60m", period="3mo"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 60m")
            return None
        return _pd.DataFrame(data)

    def fetch_30_min_series_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="30m", period="1mo"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 30m")
            return None
        return _pd.DataFrame(data)

    def fetch_15_min_series_max(self) -> Optional[_pd.DataFrame]:
        data = _yf.download(
            self._symbol, rounding=self._rounding, interval="15m", period="1mo"
        )
        if data.empty:
            print("No data returned for the given {self._symbol} and interval 15m")
            return None
        return _pd.DataFrame(data)

    def download_csv(
        self,
        monthData: any,
        weekData: any,
        dayData: any,
        sixtyMData: any,
        thirtyMData: any,
        fifteenMData: any,
    ):
        if monthData.empty:
            print("Empty data for the given {self._symbol} and interval month")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_MONTHS_SUFFIX, CSV_EXTENSION)
            self._download_csv(monthData, fileName)

        if weekData.empty:
            print("Empty data for the given {self._symbol} and interval week")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_WEEKS_SUFFIX, CSV_EXTENSION)
            self._download_csv(weekData, fileName)

        if dayData.empty:
            print("Empty data for the given {self._symbol} and interval day")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_DAYS_SUFFIX, CSV_EXTENSION)
            self._download_csv(dayData, fileName)

        if sixtyMData.empty:
            print("Empty data for the given {self._symbol} and interval 60m")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_60_M_SUFFIX, CSV_EXTENSION)
            self._download_csv(sixtyMData, fileName)

        if thirtyMData.empty:
            print("Empty data for the given {self._symbol} and interval 30m")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_30_M_SUFFIX, CSV_EXTENSION)
            self._download_csv(thirtyMData, fileName)

        if fifteenMData.empty:
            print("Empty data for the given {self._symbol} and interval 15m")
        else:
            fileName = "%s%s%s" % (self.code, STOCK_DATA_15_M_SUFFIX, CSV_EXTENSION)
            self._download_csv(fifteenMData, fileName)

    def _download_csv(self, data, fileName):
        purifiedData = self._make_datatuple(data)
        # convert the list of tuples to a DataFrame
        df = _pd.DataFrame(purifiedData)
        outputFolder = os.path.join(STOCK_DATA_FOLDER, self.code)
        # create the directory if it doesn't exist
        os.makedirs(outputFolder, exist_ok=True)
        df.to_csv(os.path.join(outputFolder, fileName), index=False)

    # def _download_csv(self, data, fileName):
    #     df_list = []
    #     df_list.append(data)
    #     df = _pd.concat(df_list)
    #     outputFolder = os.path.join(STOCK_DATA_FOLDER, self.code)
    #     # create the directory if it doesn't exist
    #     os.makedirs(outputFolder, exist_ok=True)
    #     df.to_csv(os.path.join(outputFolder, fileName))

    # def _make_datatuple(self, data):
    #     return [
    #         DATA_TUPLE(
    #             Datetime=index,
    #             Open=row[0],
    #             High=row[1],
    #             Low=row[2],
    #             Close=row[3],
    #             Volume=row[5]
    #         )
    #         for index, row in data.iterrows()
    #     ]

    def _make_datatuple(self, data):
        return (
            _pd.DataFrame(data)
            .apply(
                lambda row: DATA_TUPLE(
                    Datetime=row.name,
                    Open=row["Open"],
                    High=row["High"],
                    Low=row["Low"],
                    Close=row["Close"],
                    Volume=row["Volume"],
                ),
                axis=1,
            )
            .tolist()
        )
