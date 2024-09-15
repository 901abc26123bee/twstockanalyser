#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: fetch stock prices history to cev files
#

from twstockanalyzer.scrapers.history import PriceHistoryFetcher

try:
    from twstockanalyzer.codes import codes
except ImportError as e:
    if e.name == "lxml":
        raise e
    from codes import codes


class BaseFetcher(object):
  def __init__(self):
    self.price_fetcher = PriceHistoryFetcher()
    self.raw_data = []
    self.data = []

  def download_csv(self):
    for code in codes:
      if code == "4540":
        self.price_fetcher.initial_csv_data(code)

