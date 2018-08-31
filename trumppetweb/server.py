import json
import math
import time
from flask import Flask
from flask import request
from flask import render_template
from trumppetserver import TweetStorage
from trumppetserver import TweetAnalyzer

_app = Flask(__name__)
_storage = TweetStorage()
_analyzer = TweetAnalyzer()

_PLAYBACK_PER_PAGE = 20
_FREQUENCY_PER_PAGE = 100

@_app.route("/", methods=["GET"])
def index():
    start_date =_storage.get_oldest_tweet()['created_at']
    ts = time.strftime('%B %d, %Y', time.strptime(start_date,'%a %b %d %H:%M:%S +0000 %Y'))
    return render_template('index.html', num_tweets=_storage.get_num_tweets(), start_date=ts)


@_app.route("/playback", methods=["GET", "POST"])
def playback():
    page = request.args.get('page') or '1'
    num_tweets = _storage.get_num_tweets()
    num_pages = math.ceil(num_tweets / _PLAYBACK_PER_PAGE)
    start, end = _get_paginated_range(page, num_pages, num_tweets, _PLAYBACK_PER_PAGE)

    tweets = _storage.get_range_of_tweets(start, end)
    return render_template('playback.html', tweets=tweets, page=int(page), num_pages=num_pages, start=start, end=end, num_tweets=num_tweets)


@_app.route("/frequency", methods=["GET"])
def frequency():
    page = request.args.get('page') or '1'
    num_unique_words = _analyzer.get_num_unique_words()
    num_pages = math.ceil(num_unique_words / _FREQUENCY_PER_PAGE)
    start, end = _get_paginated_range(page, num_pages, num_unique_words, _FREQUENCY_PER_PAGE)

    word_on_page = _analyzer.get_range_of_word_freqs(start, end)
    return render_template('frequency.html', words=word_on_page, page=int(page), num_pages=num_pages, start=start, end=end, num_unique_words=num_unique_words)


@_app.route("/search", methods=["GET", "POST"])
def search():
    phrase = None
    results = None

    if request.method == 'POST':
        data = request.form
        phrase = data['phrase'].strip()
        results = list(reversed(list(_analyzer.search_tweets(phrase))))

    return render_template('search.html', phrase=phrase, results=results)


@_app.route("/freestyle", methods=["GET"])
def freestyle():
    trumpian_tweet, original_tweets = _analyzer.generate_trumpian_tweet()
    return render_template('freestyle.html', trumpian_tweet=trumpian_tweet, original_tweets=original_tweets)


def _get_paginated_range(page, num_pages, num_items, per_page):
    if page and page.isnumeric():
        page = int(page)
        if page > num_pages:
            page = num_pages
        elif page < 1:
            page = 1
    else:
        page = 1

    start = (page - 1) * per_page
    end = start + per_page
    if end > num_items:
        end = num_items

    return start, end


if __name__ == "__main__":
    _app.run(host="localhost", port=5001, debug=True)
