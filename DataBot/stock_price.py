from abc import abstractmethod
from pathlib import Path

import requests
import shutil
import json
import time
import os


class StockPrice:

    DATA_PATH = "./data/prices"
    DATE_FORMAT = "%Y-%m-%d"

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
    API_KEY = "AAAAAAAAAAAAAAAA"
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://www.alphavantage.co/query?function=%s&symbol=%s&outputsize=full&apikey=' + API_KEY

    @staticmethod
    def download(tickers):
        StockPrice.init()

        # Download New Data.
        for ticker in tickers:
            cache = os.listdir(StockPrice.DATA_PATH)
            if ticker + ".json" not in cache:

                flag = True
                while flag:
                    r = requests.get(AlphaVantage.URL % (AlphaVantage.HISTORICAL, ticker))
                    try:
                        obj = json.loads(r.text)
                        val = obj["Time Series (Daily)"]
                        flag = False
                    except KeyError:
                        # Sleep for a minute and try again.
                        print("Sleeping for 90")
                        time.sleep(90)

                with open(os.path.join(StockPrice.DATA_PATH, ticker + '.json'), "w") as file:
                    file.write(r.text)


AlphaVantage.download(["AAPL", "GOOG", "AMZN", "F", "HMC", "GE"])
