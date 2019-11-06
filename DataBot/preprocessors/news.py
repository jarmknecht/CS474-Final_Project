from DataBot.config import CONFIG
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm

import textwrap
import requests
import shutil
import json
import os
import re


class News:

    """
        Downloads links to newspaper articles for stock.
    """

    DATA_IN_PATH = CONFIG["downloaders"]["news"]["path"]
    DATA_OUT_PATH = CONFIG["preprocessors"]["news"]["path"]
    DATE_FORMAT = CONFIG["all"]["date_format"]

    @staticmethod
    def init():
        var = Path(News.DATA_OUT_PATH)
        if not var.is_dir():
            os.mkdir(News.DATA_OUT_PATH)
        else:
            shutil.rmtree(News.DATA_OUT_PATH)
            os.mkdir(News.DATA_OUT_PATH)

    # TODO: Needs work!!!!
    @staticmethod
    def process():
        News.init()
        news_catalog = os.listdir(News.DATA_IN_PATH)
        for file in news_catalog:
            with open(os.path.join(News.DATA_IN_PATH, file), "r") as f:
                json_data = json.loads(f.read())

            os.mkdir(os.path.join(News.DATA_OUT_PATH, file.replace(".json", "")))
            loop = tqdm(total=int(json_data['totalResults']))
            for article in json_data['articles']:
                url = article['url']
                r = requests.get(url)
                loop.update(1)

                if r.status_code == 200:

                    title = article['title']
                    author = article['author']
                    paragraphs = [paragraph.replace("<p>", "").replace("</p>", "") for paragraph in
                                  re.findall("<p>.*</p>", r.text)]

                    paragraphs = [paragraph for paragraph in paragraphs if len(paragraph) > 25]
                    with open(os.path.join(News.DATA_OUT_PATH, file.replace(".json", ""), title.replace("/", "") + ".txt"), "w") as f:

                        if title is not None:
                            f.write(title)
                            f.write("\n")

                        if author is not None:
                            f.write(author)
                            f.write("\n")

                        for paragraph in paragraphs:
                            f.write("\n".join(textwrap.wrap(paragraph, 75)))

            loop.close()

News.process()

