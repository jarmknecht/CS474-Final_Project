from DataBot.config import CONFIG
from abc import abstractmethod
from pathlib import Path
from tqdm import tqdm

import requests
import shutil
import json
import time
import os


class StockPrice:

    DATA_PATH = CONFIG["downloaders"]["stocks"]["path"]
    DATE_FORMAT = CONFIG["all"]["date_format"]

    @abstractmethod
    def download(self, tickers):
        raise NotImplementedError("The method not implemented")

    @staticmethod
    def init():
        var = Path(StockPrice.DATA_PATH)
        if not var.is_dir():
            os.mkdir(StockPrice.DATA_PATH)
        else:
            shutil.rmtree(StockPrice.DATA_PATH)
            os.mkdir(StockPrice.DATA_PATH)


class AlphaVantage:
    API_KEY = CONFIG["downloaders"]["stocks"]["alphavantage_key"]
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://www.alphavantage.co/query?function=%s&symbol=%s&outputsize=full&apikey=' + API_KEY

    @staticmethod
    def download(tickers):
        StockPrice.init()
        loop = tqdm(total=len(list(tickers)))

        # Download New Data.
        for ticker in tickers:
            loop.set_description('Downloading stock prices for {}'.format(ticker))
            flag = True
            while flag:
                r = requests.get(AlphaVantage.URL % (AlphaVantage.HISTORICAL, ticker))
                try:
                    obj = json.loads(r.text)
                    val = obj["Time Series (Daily)"]
                    loop.update(1)
                    flag = False
                except KeyError:
                    # Sleep for a minute and try again.
                    loop.set_description('Sleeping for 90 seconds')
                    time.sleep(90)

            with open(os.path.join(StockPrice.DATA_PATH, ticker + '.json'), "w") as file:
                file.write(r.text)

        loop.close()
