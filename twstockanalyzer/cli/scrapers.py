#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.base import BaseFetcher


def run():
    fetcher = BaseFetcher()
    # fetcher.download_stocks_prices_history_csv()
    fetcher.cal_statistic()
