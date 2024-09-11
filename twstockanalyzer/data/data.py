#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: fetch stock data
#

import yfinance as yf


class Stock():
    def __init__(self):
        pass

class BaseFetcher(object):
    def fetch(self, year, month, sid, retry):
        pass

    def _convert_date(self, date):
        """Convert '106/05/01' to '2017/05/01'"""
        return "/".join([str(int(date.split("/")[0]) + 1911)] + date.split("/")[1:])

    def _make_datatuple(self, data):
        pass

    def purify(self, original_data):
        pass


class TWSEFetcher(object):
    def __init__(self):
        pass
    
    def fetch_2330(self, year: int, month: int, sid: str, retry: int = 5):
        # Define the ticker symbol
        ticker_symbol = '2330.TW'
        # Fetch the data
        stock = yf.Ticker(ticker_symbol)

        # Get historical market data
        hist = stock.history(period='1mo')  # You can adjust the period as needed

        # Display the historical data
        print(hist)


class TPEXFetcher(object):
    def __init__(self):
        pass

