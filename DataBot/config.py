from pathlib import Path
import os

DATA_DIR = "/media/USB/dir/data/"

CONFIG = {
  "all": {
    "date_format": "%Y-%m-%d",
    "symbols": DATA_DIR + "fortune500"
  },
  "downloaders": {
    "stocks": {
      "path": DATA_DIR + "raw/prices",
      "alphavantage_key": "AAAAAAAAAAAAAAAA",
    },
    "news": {
      "path": DATA_DIR + "raw/news",
      "kaggle": DATA_DIR + "all-the-news",
      "news_key": "4d073d92cc214aef9cb00367878b8243",
      "nyt_key": "W68vMvjGpHA7E2Cmr4VX8RxkAEc8dVGJ",
      "intrino_key": "OjBmNDgxMWQ1NDQ5ZDhjMDk0NDNmNGZkMmVlMmViM2M2",
      "guardian_key": "11449c3e-48f6-4600-9dd5-7dc5711c5975",
      "ft_key": "59cbaf20e3e06d3565778e7b8bd3c005e75840be81740360c3ae92f0"
    },
    "social": {
      "path": DATA_DIR + "raw/social",
      "twitter_key": ""
    }
  },
  "preprocessors": {
      "stocks": {
        "path": DATA_DIR + "preprocessed/prices",
      },
      "news": {
        "path": DATA_DIR + "preprocessed/news",
      },
      "social": {
        "path": DATA_DIR + "preprocessed/social",
      }
  }
}


def init_datapaths():

    """
        Call to setup data directory.
    """

    var = Path(DATA_DIR)
    if not var.is_dir():
        os.mkdir(DATA_DIR)

    var = Path(DATA_DIR + "raw")
    if not var.is_dir():
        os.mkdir(DATA_DIR + "raw")

    var = Path(DATA_DIR + "preprocessed")
    if not var.is_dir():
        os.mkdir(DATA_DIR + "preprocessed")
