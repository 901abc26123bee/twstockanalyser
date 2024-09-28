#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Usage: Download all stock information related to stockholders
#

import twstockanalyzer.scrapers.const as scraperConst


class StockHolderFetcher:
    def __init__(self):
        pass

    def fetch_holders(self, code: str):
        self.code = code
        # defines the taiwan stock symbol ex: '2330.TW'
        self._symbol = code + scraperConst.TWSE_STOCK_SUFFIX_TW
