from DataBot.config import CONFIG
from pathlib import Path

import pandas as pd

import shutil
import json
import os


class Stock:

    """
        Computes Traditional Stock Market Indicators.
    """

    DATA_IN_PATH = CONFIG["downloaders"]["stocks"]["path"]
    DATA_OUT_PATH = CONFIG["preprocessors"]["stocks"]["path"]
    DATE_FORMAT = CONFIG["all"]["date_format"]

    @staticmethod
    def init():
        var = Path(Stock.DATA_OUT_PATH)
        if not var.is_dir():
            os.mkdir(Stock.DATA_OUT_PATH)
        else:
            shutil.rmtree(Stock.DATA_OUT_PATH)
            os.mkdir(Stock.DATA_OUT_PATH)

    @staticmethod
    def process(window=15):
        """
           Computes traditional financial indicators.

           Calculates
                - moving average
                - bollinger bands

           Shorter windows should be used when considering short term investments, while longer
           windows should be considered for longer term investments.
        """
        Stock.init()
        stock_files = os.listdir(Stock.DATA_IN_PATH)
        for file in stock_files:
            with open(os.path.join(Stock.DATA_IN_PATH, file), "r") as f:
                json_data = json.loads(f.read())

            # JSON to Pandas Dataframe
            stock_data = json_data["Time Series (Daily)"]
            stock_df = pd.DataFrame.from_dict(stock_data, orient='index')

            stock_df.columns = [''.join([i for i in col_name.replace(".", "") if not i.isdigit()]).strip() for
                                col_name in stock_df.columns]

            # Rolling Average Computations.
            open_roll = stock_df["open"].rolling(window=window, center=False)
            high_roll = stock_df["high"].rolling(window=window, center=False)
            low_roll = stock_df["low"].rolling(window=window, center=False)
            close_roll = stock_df["close"].rolling(window=window, center=False)

            stock_df["open_roll_avg"] = open_roll.mean()
            stock_df["high_roll_avg"] = high_roll.mean()
            stock_df["low_roll_avg"] = low_roll.mean()
            stock_df["close_roll_avg"] = close_roll.mean()

            # Bollinger Bands Calculations.
            open_std = open_roll.std()
            high_std = high_roll.std()
            low_std = low_roll.std()
            close_std = close_roll.std()

            stock_df["open_upper_bollinger_band"] = stock_df["open_roll_avg"] + (open_std * 2)
            stock_df["open_lower_bollinger_band"] = stock_df["open_roll_avg"] - (open_std * 2)

            stock_df["high_upper_bollinger_band"] = stock_df["high_roll_avg"] + (high_std * 2)
            stock_df["high_lower_bollinger_band"] = stock_df["high_roll_avg"] - (high_std * 2)

            stock_df["low_upper_bollinger_band"] = stock_df["low_roll_avg"] + (low_std * 2)
            stock_df["low_lower_bollinger_band"] = stock_df["low_roll_avg"] - (low_std * 2)

            stock_df["close_upper_bollinger_band"] = stock_df["close_roll_avg"] + (close_std * 2)
            stock_df["close_lower_bollinger_band"] = stock_df["close_roll_avg"] - (close_std * 2)

            stock_df.to_csv(os.path.join(Stock.DATA_OUT_PATH, file.replace(".json", ".csv")))

