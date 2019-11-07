from DataBot.config import CONFIG

from pathlib import Path
from tqdm import tqdm

import datetime
import newspaper
import shutil
import json
import os


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

    @staticmethod
    def process():
        News.init()
        news_catalog = os.listdir(News.DATA_IN_PATH)
        for file in news_catalog:
            with open(os.path.join(News.DATA_IN_PATH, file), "r") as f:
                json_data = json.loads(f.read())

            os.mkdir(os.path.join(News.DATA_OUT_PATH, file.replace(".json", "")))
            loop = tqdm(total=int(json_data['totalResults']))
            for article_summary in json_data['articles']:
                url = article_summary['url']
                title = article_summary['title']
                if len(title) > 30:
                    title = title[:30]
                loop.set_description(title[:30])

                try:
                    article = newspaper.Article(url)
                    article.download()
                    article.parse()
                except newspaper.article.ArticleException:
                    loop.set_description('News article could not be downloaded.')
                    loop.update(1)
                    continue

                text = article.text     # May be interesting article.keywords, article.summary

                date = article_summary['publishedAt'].split("T")[0]
                date = datetime.datetime.strptime(date, '%Y-%m-%d')   # 2019-10-30T19:15:10Z
                date = date.date()

                path = Path(os.path.join(News.DATA_OUT_PATH, file.replace(".json", ""), str(date)))
                if not path.is_dir():
                    os.mkdir(path)

                with open(os.path.join(path, title.replace("/", "") + ".txt"), "w") as f:
                    f.write(title + '\n')
                    f.write(text)

                loop.update(1)

            loop.close()

News.process()

