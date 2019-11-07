from datetime import datetime, timedelta
from DataBot.config import CONFIG
from abc import abstractmethod
from pathlib import Path
from tqdm import tqdm

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
    URL = 'https://newsapi.org/v2/everything?q="%s"&from=%s&pageSize=100&language=en&apiKey=' + API_KEY

    """
        Method for real time stock test articles.
    """
    @staticmethod
    def download(tickers):
        News.init()
        dict_set = set(line.strip() for line in open('./data/dictionary/dictionary.txt'))
        # Use ticker data to load all fortune 500 this is a dictionary with key as symbol and value as name of company
        with open('./data/fortune500/fortune500s_n.json', 'r') as json_file:
            data_ticker = json.load(json_file)

        loop = tqdm(total=len(list(tickers)))

        # Download News Data.
        # TODO: Make downloader better. AAPL works perfectly, F does not return any articles on Ford.
        for ticker in tickers:
            loop.set_description('Downloading stock news for {}'.format(ticker))

            ticker = ticker.lower()
            if len(ticker) > 3 and (ticker not in dict_set):
                ticker = ticker.upper()
            else:
                ticker = ticker.upper()
                ticker = data_ticker[ticker]
                ticker = ticker.upper()
            # print(ticker)
            flag = True
            while flag:
                r = requests.get(NewsAPIDotOrg.URL % (ticker, datetime.now() - timedelta(days=7)))

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
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://newsapi.org/v2/everything?q=%s&from=%s&pageSize=100&language=en&apiKey=' + NY_API_KEY

    """
        Get news articles for training. (Slow)
    """

    @staticmethod
    def download(tickers):
        News.init()
        loop = tqdm(total=len(list(tickers)))
        news_articles = []

        nyt_url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=%s&api-key=' + NY_API_KEY

        # NYT News Data.
        # TODO: Make downloader better. AAPL works perfectly, F does not return any articles on Ford.
        for ticker in tickers:
            loop.set_description('Downloading NYT stock news for {}'.format(ticker))

            flag = True
            while flag:
                r = requests.get(nyt_url % ticker)

                try:
                    obj = json.loads(r.text)
                    if obj["status"].lower() == "ok":
                        docs = obj["response"]["docs"]

                        for doc in docs:
                            news_articles.append({"title": doc['lead_paragraph'].split('. ')[0],
                                                  "publishedAt": doc['pub_date'], "url": doc['web_url']})
                    else:
                        raise KeyError()
                    loop.update(1)
                    flag = False
                except KeyError:
                    loop.set_description('Sleeping for an hour. Too many requests on nyt')
                    time.sleep(3600)

        loop.close()
        loop = tqdm(total=len(list(tickers)))

        intrino_url = 'https://api-v2.intrinio.com/companies/%s/news?page_size=1000&api_key=' + \
                      CONFIG['downloaders']['news']['intrino_key']
        for ticker in tickers:
            loop.set_description('Downloading Intrino stock news for {}'.format(ticker))

            flag = True
            while flag:
                r = requests.get(intrino_url % ticker)
                if r.status_code == 429 and "1 Minute Call" in json.loads(r.text)['error']:
                    loop.set_description('Sleeping for an minute. Too many requests on intrino')
                    time.sleep(90)
                    continue

                try:

                    obj = json.loads(r.text)
                    docs = obj["news"]

                    for doc in docs:
                        news_articles.append({"title": doc['title'],
                                              "publishedAt": doc['publication_date'], "url": doc['url']})
                    else:
                        raise KeyError()
                    loop.update(1)
                    flag = False
                except KeyError:
                    loop.set_description('Sleeping for an hour. Too many requests on intrino')
                    time.sleep(3600)

        json_data = {"status": "ok", "totalResults": len(docs), "articles": news_articles}
        with open(os.path.join(News.DATA_PATH, ticker + '.json'), "w") as file:
            file.write(json.dumps(json_data))

#NewsAPIDotOrg.download(["AAPL", "GE", "SNAP", "AMZN", "F"])