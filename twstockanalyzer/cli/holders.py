#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.holder import StockHolderFetcher


def run():
    fetcher = StockHolderFetcher()
    fetcher.fetch_holders("4540")
