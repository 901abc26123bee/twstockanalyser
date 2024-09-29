#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.base import BaseFetcher


def run(argv: str):
    fetcher = BaseFetcher()
    if argv == "d":
        fetcher.download_stocks_prices_history_csv()
    elif argv == "l":
        fetcher.load_stocks_prices_from_csv_files()
    elif argv == "tp":
        fetcher._test_ma_lines("4540", "60m")
    elif argv == "tm":
        fetcher._test_macd("4540", "day")
    elif argv == "is_iptrend_macd":
        fetcher.apply_macd_uptrend_condition()
