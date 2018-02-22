import json
from flask import Flask
from flask import request
from flask import Response
from storage import TweetStorage
from analyzer import TweetAnalyzer


_storage = TweetStorage()
_analyzer = TweetAnalyzer(_storage)

_app = Flask(__name__)

'''
API Endpoints

| HTTP Method    | URI             | Action                                |
| -------------- | --------------- | ------------------------------------- |
| GET            | /tweets/<num>   | Return the last <num> tweets, max 50  |
| GET            | /frequency      | Gets word frequency statistics        |
| POST           | /search         | Gets tweets matching the given phrase |
| GET            | /freestyle      | Gets a fake Trumpian-style tweet      |

'''

@_app.route("/tweets/<num>", methods=["GET"])
def get_tweets(num):
    '''
    Return the last <num> tweets, max 50
    '''

    num = 50 if int(num) > 50 else int(num)
    num = num * -1

    all_tweets = list(_storage.get_all_tweets())
    last_n = all_tweets[int(num):]

    return Response(json.dumps(last_n), mimetype='application/json')


@_app.route("/frequency", methods=["GET"])
def get_word_frequency():
    '''
    Gets word frequency statistics
    '''

    best_words, largest_word_length = _analyzer.get_word_frequency()
    data = {
        "largest_word_length": largest_word_length,
        "best_words": best_words
    }

    return Response(json.dumps(data), mimetype='application/json')


@_app.route("/search", methods=["POST"])
def search():
    '''
    Gets tweets matching the given phrase
    '''

    data = request.form
    matches = _analyzer.search_tweets(data['phrase'])

    return Response(json.dumps(matches), mimetype='application/json')


@_app.route("/freestyle", methods=["GET"])
def freestyle():
    '''
    Gets a fake Trumpian-style tweet
    '''

    fake_tweet, original_tweets = _analyzer.generate_trumpian_tweet()
    data = {
        "fake_tweet": fake_tweet,
        "original_tweets": original_tweets
    }

    return Response(json.dumps(data), mimetype='application/json')


if __name__ == "__main__":
    _app.run(host="localhost", port=5000, debug=True)
