from DataBot.downloaders.stock_prices import AlphaVantage
from DataBot.downloaders.news import NewsAPIDotOrg
from DataBot.config import init_datapaths
from threading import Thread


def main():
    init_datapaths()

    # TODO: Create list of which stocks to target.

    # Start
    tickers = ["AAPL", "GOOG", "FB", "F", "GE", "SNAP"]
    stock_downloader = Thread(target=AlphaVantage.download(tickers=tickers))  # TODO: ADD preprocess to this thread.
    stock_downloader.start()

    news_downloader = Thread(target=NewsAPIDotOrg.download(tickers=tickers))  # TODO: ADD preprocess to this thread.
    news_downloader.start()

    # TODO: Social media download bot.

if __name__ == "__main__":
    main()
