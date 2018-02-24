import json
from flask import Flask
from flask import request
from flask import render_template
from trumppetserver import TweetStorage
from trumppetserver import TweetAnalyzer


_app = Flask(__name__)
_storage = TweetStorage()
_analyzer = TweetAnalyzer()


@_app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@_app.route("/playback", methods=["GET", "POST"])
def playback():
    num = 20

    if request.method == 'POST':
        data = request.form
        num = data['num']

    tweets = list(reversed(_storage.get_last_n_tweets(num)))
    return render_template('playback.html', tweets=tweets, num_tweets=_storage.get_num_tweets())


@_app.route("/frequency", methods=["GET"])
def frequency():
    best_words, largest_word_length = _analyzer.get_word_frequency()
    return render_template('frequency.html', best_words=reversed(best_words))


@_app.route("/search", methods=["GET", "POST"])
def search():
    phrase = None
    results = None

    if request.method == 'POST':
        data = request.form
        phrase = data['phrase']
        results = list(reversed(list(_analyzer.search_tweets(data['phrase']))))

    return render_template('search.html', phrase=phrase, results=results)


@_app.route("/freestyle", methods=["GET"])
def freestyle():
    trumpian_tweet, original_tweets = _analyzer.generate_trumpian_tweet()
    return render_template('freestyle.html', trumpian_tweet=trumpian_tweet, original_tweets=original_tweets)


if __name__ == "__main__":
    _app.run(host="localhost", port=5001, debug=True)
