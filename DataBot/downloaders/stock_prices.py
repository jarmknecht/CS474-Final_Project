import json
import os
from json import JSONDecodeError

import requests
import shutil
import time
from abc import abstractmethod
from pathlib import Path
import urllib.parse
from tqdm import tqdm

from DataBot.config import CONFIG


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


class AlphaVantage(StockPrice):
    API_KEY = CONFIG["downloaders"]["stocks"]["alphavantage_key"]
    HISTORICAL = 'TIME_SERIES_DAILY'
    URL = 'https://www.alphavantage.co/query?function=%s&symbol=%s&outputsize=full&apikey=' + API_KEY

    @staticmethod
    def download(tickers):
        StockPrice.init()

        # Download New Data.
        invalid = []
        for ticker in tickers:
            time.sleep(10)
            print("TICKER: " + ticker)
            # print('Downloading stock prices for {}'.format(ticker))
            flag = True
            while flag:
                r = requests.get(AlphaVantage.URL % (AlphaVantage.HISTORICAL, urllib.parse.quote(ticker)))
                try:
                    obj = json.loads(r.text)
                    val = obj["Time Series (Daily)"]
                    flag = False
                    with open(os.path.join(StockPrice.DATA_PATH, ticker + '.json'), "w") as file:
                        file.write(r.text)
                except KeyError:
                    # Sleep for a minute and try again.
                    if "alpha" in r.text.lower():
                        print('Sleeping for 90 seconds ' + str(ticker))
                        time.sleep(90)
                    else:
                        invalid.append(ticker)
                        flag = False
                except JSONDecodeError:
                    print("JSON DECODE ERROR FOR -> " + str(ticker))
                    with open("./error.html", "w") as f:
                        f.write(r.text)
                    time.sleep(90)

        print(invalid)
