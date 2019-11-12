import json
import os
import pandas as pd
import requests
import shutil
import threading
import time
from abc import abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from tqdm import tqdm

from DataBot.config import CONFIG
from DataBot.util import query_ticker_term


# https://stocknewsapi.com

class News:
    DATA_PATH = CONFIG["downloaders"]["news"]["path"]
    DATE_FORMAT = CONFIG["all"]["date_format"]

    def __init__(self):
        News.init()

    @abstractmethod
    def download(self, tickers):
        raise NotImplementedError("The method not implemented")

    @staticmethod
    def init():
        var = Path(News.DATA_PATH)
        if not var.is_dir():
            os.mkdir(News.DATA_PATH)
        else:
            shutil.rmtree(News.DATA_PATH)
            os.mkdir(News.DATA_PATH)


class NewsAPIDotOrg(News):
    """
        Courtesy of https://newsapi.org/
    """

    API_KEY = CONFIG["downloaders"]["news"]["news_key"]
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://newsapi.org/v2/everything?q=%s&from=%s&pageSize=100&language=en&apiKey=' + API_KEY

    """
        Method for real time stock test articles.
    """

    @staticmethod
    def download(tickers):

        loop = tqdm(total=len(list(tickers)))

        # Download News Data.
        for ticker in tickers:
            loop.set_description('Downloading stock news for {}'.format(ticker))

            flag = True
            while flag:
                r = requests.get(NewsAPIDotOrg.URL % (query_ticker_term(ticker), datetime.now() - timedelta(days=7)))

                try:
                    obj = json.loads(r.text)
                    if obj["status"] == "ok":
                        val = obj["articles"]
                    else:
                        raise KeyError(obj["code"])
                    loop.update(1)
                    flag = False
                except KeyError:
                    loop.set_description('Sleeping for an hour. Too many requests')
                    time.sleep(3600)

            with open(os.path.join(News.DATA_PATH, ticker + '.json'), "w") as file:
                file.write(r.text)

        loop.close()


class HistoricNews(News):
    """
        Courtesy of https://newsapi.org/
    """

    NY_API_KEY = CONFIG["downloaders"]["news"]["nyt_key"]
    GUARDIAN_API_KEY = CONFIG["downloaders"]["news"]["guardian_key"]
    FT_API_KEY = CONFIG["downloaders"]["news"]["ft_key"]
    HISTORICAL = 'TIME_SERIES_DAILY'
    NYT_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q="%s"&page=%s&api-key=' + NY_API_KEY
    GUARDIAN_URL = 'https://content.guardianapis.com/search?q="%s"&page-size=50&page=%s&api-key=' + GUARDIAN_API_KEY
    FT_URL = 'https://api.ft.com/content/search/v1'

    """
        Get news articles for training. (Slow)
    """

    @staticmethod
    def download(tickers):
        News.init()
        NewsAPIDotOrg.download(tickers)
        news_articles = {}

        # NYT News Data, don't wait for GUARDIAN API timeouts..
        def new_york_times():
            print("NYT Thread Running...")
            for ticker in tickers:
                print("NYT % done: " + str(tickers.index(ticker) + "/" + str(len(tickers))))
                flag = True
                page_num = 0
                while flag:
                    time.sleep(6)
                    r = requests.get(HistoricNews.NYT_URL % (query_ticker_term(ticker), page_num))

                    try:
                        obj = json.loads(r.text)
                        if obj["status"].lower() == "ok":
                            docs = obj["response"]["docs"]

                            if ticker not in news_articles.keys():
                                news_articles[ticker] = []
                            for doc in docs:
                                news_articles[ticker].append({"title": doc['lead_paragraph'].split('. ')[0],
                                                              "publishedAt": doc['pub_date'], "url": doc['web_url']})
                        else:
                            raise KeyError()

                        if len(obj['response']['docs']) == 0:
                            flag = False
                        else:
                            page_num += 1  # Go get the other articles.
                    except KeyError:
                        print('Sleeping for ten minutes. Too many requests on nyt: ' + str(r.text))
                        time.sleep(600)

        # Guardian News Data, don't wait for NYT API timeouts.
        def guardian():
            print("Guardian Thread Running...")
            for ticker in tickers:
                print("Guardian % done: " + str(tickers.index(ticker) + "/" + str(len(tickers))))
                flag = True
                page_num = 1
                while flag:
                    time.sleep(1)
                    r = requests.get(HistoricNews.GUARDIAN_URL % (query_ticker_term(ticker), page_num))

                    try:
                        obj = json.loads(r.text)['response']
                        if obj["status"].lower() == "ok":
                            docs = obj["results"]

                            if ticker not in news_articles.keys():
                                news_articles[ticker] = []
                            for doc in docs:
                                news_articles[ticker].append({"title": doc['webTitle'].split('. ')[0], "publishedAt": doc['webPublicationDate'], "url": doc['webUrl']})

                            if obj['currentPage'] < obj['pages']:
                                page_num += 1
                            else:
                                flag = False
                        else:
                            raise KeyError()

                    except KeyError:
                        print('Sleeping for ten minutes. Too many requests on guardian: ' + str(r.text))
                        time.sleep(600)

        print("Starting News Daemons!")
        nyt_thread = threading.Thread(target=new_york_times, args=(), daemon=True)
        guardian_thread = threading.Thread(target=guardian, args=(), daemon=True)

        nyt_thread.start()
        guardian_thread.start()

        # Wait for both threads to finish before writing.
        print("Waiting for News Daemons!")
        nyt_thread.join()
        guardian_thread.join()

        print("Writing News Data to Disk!")
        for key, value in news_articles.items():
            '''
                Make like newsAPI to make compatible with preprocessor, merge news items to one file.
            '''
            with open(os.path.join(News.DATA_PATH, key + '.json'), "r") as file:
                preexisting = json.loads(file.read())
                preexisting["articles"].extend(value)
                preexisting["totalResults"] = len(preexisting["articles"])

            with open(os.path.join(News.DATA_PATH, key + '.json'), 'w') as file:
                file.write(json.dumps(preexisting))


# HistoricNews.download(["AAPL", "GE", "SNAP", "AMZN"])
