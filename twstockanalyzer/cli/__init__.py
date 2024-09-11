# -*- coding: utf-8 -*-
import argparse
from twstockanalyzer.codes import __update_codes

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--history", action="store_true", help="Fetch stock prices history")
    parser.add_argument(
        "-U", "--upgrade-codes", action="store_true", help="Update entities codes"
    )
    args = parser.parse_args()


    if args.history:
        print("Start to fetch stock prices history")
    elif args.upgrade_codes:
        print("Start to update codes")
        __update_codes()
        print("Done!")
    else:
        parser.print_help()
