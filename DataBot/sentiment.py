from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def sentiment_scores(sentence):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(sentence)

    print("Overall sentiment dictionary is : ", scores)
    print("sentence was rated as ", scores['neg'] * 100, "% Negative")
    print("sentence was rated as ", scores['neu'] * 100, "% Neutral")
    print("sentence was rated as ", scores['pos'] * 100, "% Positive")

    print("Sentence Overall Rated As", end=" ")
    if scores['compound'] >= 0.05:
        print("Positive")

    elif scores['compound'] <= - 0.05:
        print("Negative")

    else:
        print("Neutral")

if __name__ == "__main__":
    print("\n1st statement :")
    sentence = "Geeks For Geeks is the best portal for \
    the computer science engineering students."

    # function calling
    sentiment_scores(sentence)

    print("\n2nd Statement :")
    sentence = "study is going on as usual"
    sentiment_scores(sentence)

    print("\n3rd Statement :")
    sentence = "I am vey sad today."
    sentiment_scores(sentence)

    print('\n4th Statement: ')
    f = open('./data/preprocessed/news/AAPL/2019-10-31/Disney Earnings Preview: What\'.txt', 'r')
    sentence = f.read()
    sentiment_scores(sentence)
    f.close()