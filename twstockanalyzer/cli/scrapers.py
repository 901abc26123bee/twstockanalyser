#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.base import BaseFetcher


def run(argv: str):
    fetcher = BaseFetcher()
    if argv == "d":
        fetcher.download_stocks_prices_history_csv()
    elif argv == "l":
        fetcher.load_stocks_prices_from_csv_files()
    elif argv == "t":
        fetcher._test("4540")
