#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.base import BaseFetcher


def run(argv: str):
    fetcher = BaseFetcher()
    if argv == "d":
        fetcher.download_stocks_prices_history_csv()
        # python -m twstockanalyzer -A d >> ./download_20241004_log.txt
    elif argv == "l":
        fetcher.load_stocks_prices_from_csv_files()
        # python -m twstockanalyzer -A l
    elif argv == "tp":
        fetcher._test_ma_lines("4540", "60m")
        # python -m twstockanalyzer -A tp
    elif argv == "tm":
        # fetcher._test_macd("8104", "30m")
        # fetcher._test_macd("2477", "30m")
        fetcher._test_macd("4540", "30m")
        # python -m twstockanalyzer -A tm
    elif argv == "apply_strategy":
        fetcher.apply_strategy_collections()
        # python -m twstockanalyzer -A apply_strategy >> ./apply_strategy.txt
