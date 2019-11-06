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


class News:

    DATA_PATH = CONFIG["downloaders"]["news"]["path"]
    DATE_FORMAT = CONFIG["all"]["date_format"]

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


class NewsAPIDotOrg:

    """
        Courtesy of https://newsapi.org/
    """

    API_KEY = CONFIG["downloaders"]["news"]["news_key"]
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://newsapi.org/v2/everything?q=%s&from=%s&apiKey=' + API_KEY

    @staticmethod
    def download(tickers):
        News.init()
        loop = tqdm(total=len(list(tickers)))

        # Download News Data.
        for ticker in tickers:
            loop.set_description('Downloading stock news for {}'.format(ticker))

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