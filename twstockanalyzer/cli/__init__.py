# -*- coding: utf-8 -*-
import argparse
from twstockanalyzer.codes import __update_codes
from twstockanalyzer.cli import scrapers


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-A", "--initial-fetch", action="store_true", help="Fetch stock prices history")
    parser.add_argument("-P", "--update-fetch", nargs="+", help="Patch stock prices history with start date")
    parser.add_argument(
        "-U", "--upgrade-codes", action="store_true", help="Update entities codes"
    )
    args = parser.parse_args()

    if args.initial_fetch:
        print("Start to fetch all stock prices history")
        scrapers.run()
        print("Done!")
    elif args.update_fetch:
        print("Start to fetch stock prices history")
        print("Done!")
    elif args.upgrade_codes:
        print("Start to update codes")
        __update_codes()
        print("Done!")
    else:
        parser.print_help()
