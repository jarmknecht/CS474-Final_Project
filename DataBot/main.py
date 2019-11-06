from DataBot.downloaders.stock_prices import AlphaVantage
from DataBot.downloaders.news import NewsAPIDotOrg
from DataBot.config import init_datapaths
from threading import Thread

from DataBot.preprocessors.news import News
from DataBot.preprocessors.stock import Stock

import json

def main():
    init_datapaths()

    with open('./data/fortune500/fortune500.json', 'r') as json_file:
        ticker_data = json.load(json_file)

    print(ticker_data['Apple'])

    # Start
    tickers = ["AAPL", "GOOG", "FB", "F", "GE", "SNAP"]
    stock_downloader = Thread(target=stock_price_workflow(tickers))
    stock_downloader.start()

    news_downloader = Thread(target=stock_news_workflow(tickers))
    news_downloader.start()

    social_downloader = Thread(target=stock_social_workflow(tickers))
    social_downloader.start()


def stock_price_workflow(tickers):
    AlphaVantage.download(tickers=tickers)
    Stock.process(window=15)    # Shorter windows for short term, longer windows for long term.


def stock_news_workflow(tickers):
    NewsAPIDotOrg.download(tickers=tickers)
    News.process()


def stock_social_workflow(tickers):
    # TODO: Implement this!
    pass

if __name__ == "__main__":
    main()
