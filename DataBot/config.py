from pathlib import Path
import os

DATA_DIR = "./data/"

CONFIG = {
  "all": {
    "date_format": "%Y-%m-%d",
  },
  "downloaders": {
    "stocks": {
      "path": DATA_DIR + "raw/prices",
      "alphavantage_key": "AAAAAAAAAAAAAAAA",
    },
    "news": {
      "path": DATA_DIR + "raw/news",
      "news_key": "4d073d92cc214aef9cb00367878b8243",
      "nyt_key": "W68vMvjGpHA7E2Cmr4VX8RxkAEc8dVGJ",
      "intrino_key": "OjBmNDgxMWQ1NDQ5ZDhjMDk0NDNmNGZkMmVlMmViM2M2"
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
