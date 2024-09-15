from  twstockanalyzer.scrapers.base import BaseFetcher


def run():
    fetcher = BaseFetcher()
    fetcher.download_csv()
