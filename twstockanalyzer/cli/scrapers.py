#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.base import BaseFetcher


def run():
    fetcher = BaseFetcher()
    # fetcher.download_csv()
    fetcher.troubleshot()
