from datetime import datetime, timedelta
from DataBot.config import CONFIG
from abc import abstractmethod
from pathlib import Path
from tqdm import tqdm
from DataBot.util import query_ticker_term

import pandas as pd

import threading
import requests
import shutil
import json
import time
import os


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
                flag = True
                page_num = 0
                while flag:
                    time.sleep(1)
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

                        if len(data['response']['docs']) == 0:
                            flag = False
                        else:
                            page_bum += 1  # Go get the other articles.
                    except KeyError:
                        print('Sleeping for an hour. Too many requests on nyt')
                        time.sleep(3600)

        # Guardian News Data, don't wait for NYT API timeouts.
        def guardian():
            print("Guardian Thread Running...")
            for ticker in tickers:
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
                        print('Sleeping for an hour. Too many requests on guardian')
                        time.sleep(3600)

        print("Starting News Daemons!")
        nyt_thread = threading.Thread(target=new_york_times(), daemon=True)
        guardian_thread = threading.Thread(target=guardian(), daemon=True)

        nyt_thread.start()
        guardian_thread.start()

        # Wait for both threads to finish before writing.
        print("Waiting for News Daemons!")
        nyt_thread.join()
        guardian_thread.join()

        # TODO: ADD other news API's here.

        print("Writing News Data to Disk!")
        for key, value in news_articles.items():
            # Make JSON look like newsapi json format to not break things!
            json_data = {"status": "ok", "totalResults": len(value), "articles": value}
            with open(os.path.join(News.DATA_PATH, key + '.json'), "w") as file:
                file.write(json.dumps(json_data))


# HistoricNews.download(["AAPL", "GE", "SNAP", "AMZN"])
