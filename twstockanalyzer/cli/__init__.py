# -*- coding: utf-8 -*-
import argparse
from twstockanalyzer.codes import __update_codes
from twstockanalyzer.cli import holders, scrapers


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-A", "--fetch-prices", action="store_true", help="Fetch stock prices history"
    )
    parser.add_argument(
        "-H", "--fetch-holders", action="store_true", help="Patch stock holder infos"
    )
    parser.add_argument(
        "-U", "--upgrade-codes", action="store_true", help="Update entities codes"
    )
    args = parser.parse_args()

    if args.fetch_prices:
        print("Start to fetch stock prices history")
        scrapers.run()
        print("Done!")
    elif args.fetch_holders:
        print("Start to fetch stock holder infos")
        holders.run()
        print("Done!")
    elif args.upgrade_codes:
        print("Start to update codes")
        __update_codes()
        print("Done!")
    else:
        parser.print_help()
