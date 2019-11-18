import datetime
import json
import newspaper
import os
import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm

from DataBot.config import CONFIG
from DataBot.util import query_ticker_term


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
        # Keep adding to our stock news, every week gets more info.
        # else:
        #     shutil.rmtree(News.DATA_OUT_PATH)
        #     os.mkdir(News.DATA_OUT_PATH)

    @staticmethod
    def process():
        News.init()

        with open(os.path.join(CONFIG['all']['symbols'], 'fortune500s_n.json'), 'r') as f:
            fortune500s_n = json.loads(f.read())

        news_catalog = os.listdir(News.DATA_IN_PATH)
        for file in news_catalog:
            with open(os.path.join(News.DATA_IN_PATH, file), "r") as f:
                json_data = json.loads(f.read())

            var = Path(os.path.join(News.DATA_OUT_PATH, file.replace(".json", "")))
            if not var.is_dir():
                os.mkdir(os.path.join(News.DATA_OUT_PATH, file.replace(".json", "")))

            # Add check for articles from kaggle.
            News.all_the_data(file.replace(".json", ""))

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

                # Attempt to get more relevant news content.
                content = []
                ticker = file.replace(".json", "")
                if " " + ticker + " " in title or "(" + ticker + ")" in title or fortune500s_n[ticker] in title:
                    content.append(title)

                corpus = text
                sentences = corpus.split(".")
                for sentence in sentences:
                    if " " + ticker + " " in title or "(" + ticker + ")" in title or fortune500s_n[ticker] in title:
                        content.append(sentence)

                if len(content) != 0:
                    path = Path(os.path.join(News.DATA_OUT_PATH, file.replace(".json", ""), str(date)))

                    if not path.is_dir():
                        os.mkdir(path)

                    file_path = Path(os.path.join(path, title.replace("/", "") + ".txt"))
                    if not file_path.exists():
                        with open(os.path.join(path, title.replace("/", "") + ".txt"), "w") as f:
                            f.write(".".join(content))

                loop.update(1)

            loop.close()

    @staticmethod
    def all_the_data(ticker):

        with open(os.path.join(CONFIG['all']['symbols'], 'fortune500s_n.json'), 'r') as f:
            fortune500s_n = json.loads(f.read())

        all_the_data_path = CONFIG['downloaders']['news']['kaggle']
        datasets = os.listdir(all_the_data_path)
        for dataset in datasets:
            table = pd.read_csv(os.path.join(all_the_data_path, dataset))
            table = table[table['content'].str.contains(query_ticker_term(ticker), case=False)]
            for index, row in table.iterrows():
                try:
                    date = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
                except ValueError:
                    date = datetime.datetime.strptime(
                        datetime.datetime.strptime(row['date'], '%Y/%m/%d').strftime('%Y-%m-%d'), '%Y-%m-%d')
                except TypeError:
                    continue

                date = date.date()

                title = row['title']

                # Attempt to get more relevant news content.
                content = []
                if " " + ticker + " " in title or "(" + ticker + ")" in title or fortune500s_n[ticker] in title:
                    content.append(title)

                corpus = row['content']
                sentences = corpus.split(".")
                for sentence in sentences:
                    if " " + ticker + " " in title or "(" + ticker + ")" in title or fortune500s_n[ticker] in title:
                        content.append(sentence)

                if len(content) != 0:
                    path = Path(os.path.join(News.DATA_OUT_PATH, ticker, str(date)))
                    if not path.is_dir():
                        os.mkdir(path)

                    # Add to our old news data.
                    file_path = Path(os.path.join(path, title.replace("/", "") + ".txt"))
                    if not file_path.exists():
                        with open(os.path.join(path, title.replace("/", "") + ".txt"), "w") as f:
                            f.write(".".join(content))

#print("Stating...")
#News.process()

