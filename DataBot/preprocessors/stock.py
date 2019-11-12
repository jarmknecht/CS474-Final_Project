import json
import os
import pandas as pd
import numpy as np
import shutil
from pathlib import Path

from DataBot.config import CONFIG


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
    def process(rolling_average_low=7, rolling_average_high=21, rolling_average_bollinger_band=20,
                sma=50, ema=50, momentum=3):
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

            '''
                Indicator #1: Rolling averages.
            '''

            # Rolling Average Computations. (Short)
            open_ra_short = stock_df["open"].rolling(window=rolling_average_low, center=False)
            high_ra_short = stock_df["high"].rolling(window=rolling_average_low, center=False)
            low_ra_short = stock_df["low"].rolling(window=rolling_average_low, center=False)
            close_ra_short = stock_df["close"].rolling(window=rolling_average_low, center=False)

            stock_df["open_ma7"] = open_ra_short.mean()
            stock_df["high_ma7"] = high_ra_short.mean()
            stock_df["low_ma7"] = low_ra_short.mean()
            stock_df["close_ma7"] = close_ra_short.mean()

            # Rolling Average Computations. (Short)
            open_ra_long = stock_df["open"].rolling(window=rolling_average_high, center=False)
            high_ra_long = stock_df["high"].rolling(window=rolling_average_high, center=False)
            low_ra_long = stock_df["low"].rolling(window=rolling_average_high, center=False)
            close_ra_long = stock_df["close"].rolling(window=rolling_average_high, center=False)

            stock_df["open_ma21"] = open_ra_long.mean()
            stock_df["high_ma21"] = high_ra_long.mean()
            stock_df["low_ma21"] = low_ra_long.mean()
            stock_df["close_ma21"] = close_ra_long.mean()

            '''
                Indicator # 2: Bollinger Bands
                
                * There are three lines that compose Bollinger Bands: A simple moving average
                (middle band) and an upper and lower band.
                * The upper and lower bands are typically 2 standard deviations +/- from a
                20-day simple moving average, but can be modified.
            '''

            open_ra_bb = stock_df["open"].rolling(window=rolling_average_bollinger_band, center=False)
            high_ra_bb = stock_df["high"].rolling(window=rolling_average_bollinger_band, center=False)
            low_ra_bb = stock_df["low"].rolling(window=rolling_average_bollinger_band, center=False)
            close_ra_bb = stock_df["close"].rolling(window=rolling_average_bollinger_band, center=False)

            open_bb_std = open_ra_bb.std()
            high_bb_std = high_ra_bb.std()
            low_bb_std = low_ra_bb.std()
            close_bb_std = close_ra_bb.std()

            stock_df["open_upper_band"] = open_ra_bb.mean() + (open_bb_std * 2)
            stock_df["open_lower_band"] = open_ra_bb.mean() - (open_bb_std * 2)

            stock_df["high_upper_band"] = high_ra_bb.mean() + (high_bb_std  * 2)
            stock_df["high_lower_band"] = high_ra_bb.mean() - (high_bb_std  * 2)

            stock_df["low_upper_band"] = low_ra_bb.mean() + (low_bb_std * 2)
            stock_df["low_lower_band"] = low_ra_bb.mean() - (low_bb_std * 2)

            stock_df["close_upper_band"] = close_ra_bb.mean() + (close_bb_std * 2)
            stock_df["close_lower_band"] = close_ra_bb.mean() - (close_bb_std * 2)

            '''
                Indicator #3: MACD - Moving Average Convergence/Divergence
                
                It is designed to reveal changes in the strength, direction, momentum, and duration of a
                trend in a stock's price.
            '''
            temp = pd.DataFrame()
            temp['ema26'] = stock_df['open'].ewm(span=26).mean()
            temp['ema12'] = stock_df['open'].ewm(span=12).mean()
            stock_df['open_macd'] = (temp['ema12'] - temp['ema26'])

            temp = pd.DataFrame()
            temp['ema26'] = stock_df['high'].ewm(span=26).mean()
            temp['ema12'] = stock_df['high'].ewm(span=12).mean()
            stock_df['high_macd'] = (temp['ema12'] - temp['ema26'])

            temp = pd.DataFrame()
            temp['ema26'] = stock_df['low'].ewm(span=26).mean()
            temp['ema12'] = stock_df['low'].ewm(span=12).mean()
            stock_df['low_macd'] = (temp['ema12'] - temp['ema26'])

            temp = pd.DataFrame()
            temp['ema26'] = stock_df['close'].ewm(span=26).mean()
            temp['ema12'] = stock_df['close'].ewm(span=12).mean()
            stock_df['close_macd'] = (temp['ema12'] - temp['ema26'])

            '''
                Indicator #4: EMA
                
                Changes in market trends.
            '''

            stock_df['open_ema'] = stock_df['open'].ewm(span=ema).mean()
            stock_df['high_ema'] = stock_df['high'].ewm(span=ema).mean()
            stock_df['low_ema'] = stock_df['low'].ewm(span=ema).mean()
            stock_df['close_ema'] = stock_df['close'].ewm(span=ema).mean()

            '''
                Indicator #5: SMA
                
                * A death cross occurs when the 50-day simple moving average crosses below
                the 200-day moving average.
                * A golden cross occurs when a short-term moving average breaks above
                a long-term moving average. 
            '''

            stock_df['open_sma'] = stock_df['open'].rolling(sma).mean()
            stock_df['high_sma'] = stock_df['high'].rolling(sma).mean()
            stock_df['low_sma'] = stock_df['low'].rolling(sma).mean()
            stock_df['close_sma'] = stock_df['close'].rolling(sma).mean()

            '''
                Indicator #6: Momentum
                
                Momentum is the rate of acceleration of a security's price or volume – that is, the speed at
                which the price is changing. Simply put, it refers to the rate of change on price movements for
                a particular asset and is usually defined as a rate. In technical analysis, momentum is considered
                an oscillator and is used to help identify trend lines.
            '''

            stock_df['momentum'] = np.where(stock_df['close'] > 0, 1, -1)
            stock_df['momentum_3day'] = stock_df.momentum.rolling(momentum).mean()

            # Write out to disk!
            stock_df.to_csv(os.path.join(Stock.DATA_OUT_PATH, file.replace(".json", ".csv")))