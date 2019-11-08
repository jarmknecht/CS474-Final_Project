import json


def query_ticker_term(ticker):
    """
        Tries to get unique stock ticker to query news articles.
    """
    # Use ticker data to load all fortune 500 this is a dictionary with key as symbol and value as name of company
    with open('./data/fortune500/fortune500s_n.json', 'r') as json_file:
        data_ticker = json.load(json_file)

    with open('./data/dictionary/dictionary.txt', 'r') as dictionary:
        dict_set = set(line.strip() for line in dictionary)

    ticker = ticker.lower()
    if len(ticker) > 2 and (ticker not in dict_set):
        ticker = ticker.upper()
    else:
        ticker = ticker.upper()
        ticker = data_ticker[ticker]
        ticker = ticker.upper()

    return ticker
