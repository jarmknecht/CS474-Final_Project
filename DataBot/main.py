import argparse
import json
from threading import Thread

from DataBot.downloaders.stock_prices import AlphaVantage
from DataBot.preprocessors.news import News
from DataBot.downloaders.news import NewsAPIDotOrg
from DataBot.preprocessors.stock import Stock
from DataBot.config import init_datapaths


def main():
    init_datapaths()

    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='DataBot for downloading stock data.')
    parser.add_argument('-q', '--quotes', choices=['all', 'today', 'recalculate'], help='Download historical stock market prices.')
    parser.add_argument('-n', '--news', choices=['all', 'last-week'], help='Download news articles for stocks.')
    parser.add_argument('-s', '--social', choices=['all', 'last-week'], help='Download tweets for stocks.')
    parser.add_argument('-p', '--path', help='Path to store data.')
    args = parser.parse_args()

    # Use ticker data to load all fortune 500 this is a dictionary with key as name of company and value as symbol
    with open('./data/fortune500/fortune500n_s.json', 'r') as json_file:
        ticker_data = json.load(json_file)

    # Start
    tickers = ["AAPL", "GOOG", "FB", "F", "GE", "SNAP"]
    tickers = []
    for key, value in ticker_data.items():
        tickers.append(value)

    if args.path is not None:
        CONFIG.DATA_DIR = args.path

    if args.quotes is not None:
        stock_downloader = Thread(target=stock_price_workflow(args.quotes, tickers), daemon=True)
        stock_downloader.start()

    if args.news is not None:
        news_downloader = Thread(target=stock_news_workflow(args.news, tickers), daemon=True)
        news_downloader.start()

    if args.social is not None:
        social_downloader = Thread(target=stock_social_workflow(args.social, tickers), daemon=True)
        social_downloader.start()


def stock_price_workflow(quote_args, tickers):
    if quote_args == 'download':
        AlphaVantage.download(tickers=tickers)
    Stock.process(window=5)    # Shorter windows for short term, longer windows for long term.


def stock_news_workflow(news_args, tickers):
    if news_args == 'all':
        HistoricNews.download(tickers=tickers)  # May want to break this up into chuncks on systems with low memory.
        News.process()
    elif news_args == 'last-week':
        NewsAPIDotOrg.download(tickers=tickers)
        News.process()


def stock_social_workflow(social_args, tickers):
    if social_args == 'all':
        pass
    elif social_args == 'last-week':
        pass

if __name__ == "__main__":
    main()

