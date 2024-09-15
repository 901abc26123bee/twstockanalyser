from  twstockanalyzer.scrapers.history import PriceHistoryFetcher


def run():
    fetcher = PriceHistoryFetcher()
    fetcher.fetch_latest_data()
