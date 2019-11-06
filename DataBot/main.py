from DataBot.downloaders.stock_prices import AlphaVantage
from DataBot.downloaders.news import NewsAPIDotOrg
from DataBot.config import init_datapaths
from threading import Thread

from DataBot.preprocessors.stock import Stock


def main():
    init_datapaths()

    # TODO: Create list of which stocks to target.

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
    # Stock price Preprocess.


def stock_social_workflow(tickers):
    # TODO: Implement this!
    pass

if __name__ == "__main__":
    main()
