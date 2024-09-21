#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twstockanalyzer.scrapers.analytics import Analysis


def run(argv):
    if argv == "s1":
        anal = Analysis()
        anal._is_downtrend_in_month_and_week()
