import sys
import string
import re
import html
from operator import itemgetter
import twitter
import click
import pymongo
from mcgpyutils import FileSystemUtils
from mcgpyutils import ConfigUtils
from mcgpyutils import OutputUtils

if __name__ == "__main__":
    from __version__ import __version__
else:
    from .__version__ import __version__

_ou = OutputUtils()

_fsu = FileSystemUtils()
_fsu.set_config_location(f'{_fsu.get_path_to_script(__file__)}/config')

_config = ConfigUtils()
_config.parse_json_config(f'{_fsu.get_config_location()}/trumppet_config.json')
_twitter_config = _config.get_json_config_field('twitter')
_mongodb_config = _config.get_json_config_field('mongodb')

_mongodb = pymongo.MongoClient(_mongodb_config['server'], _mongodb_config['port'])
_db = _mongodb[_mongodb_config['db']]
_db_tweets = _db[_mongodb_config["collection"]]

_api = twitter.Api(consumer_key=_twitter_config['consumer_key'],
                   consumer_secret=_twitter_config['consumer_secret'],
                   access_token_key=_twitter_config['access_token'],
                   access_token_secret=_twitter_config['access_token_secret'],
                   tweet_mode='extended',
                   sleep_on_rate_limit=True)


@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
def cli(context):
    '''
    Donald Trump tweet analyzer
    '''
    pass


@click.command('catalog', short_help='fetch and store all possible tweets')
def catalog():
    '''
    Fetches all the tweets returned by the Twitter API (limited to last 3200)
    '''

    max_tweet_archive = 3200
    tweets_per_call = 200
    oldest_tweet_id = None
    tweets = []
    batch = 1

    while len(tweets) < max_tweet_archive:
        statuses = _api.GetUserTimeline(screen_name=_twitter_config['screen_name'], 
                                        count=tweets_per_call,
                                        max_id=oldest_tweet_id)

        _ou.info(f'Processing tweet batch {batch} ({len(statuses)} new, {len(tweets)} total)...')

        for i, status in enumerate(statuses):
            if i == 0 and oldest_tweet_id:
                # max_id returns tweets greater than or EQUAL to the given ID.
                # Skipping the first tweet of the current batch prevents 
                # duplicating the last tweet of the previous batch.
                continue
            tweets.append(prepare_tweet(status))

        oldest_tweet_id = statuses[-1].id_str
        batch += 1

    try:
        _db_tweets.insert_many(list(reversed(tweets)))
        _ou.info(f'Inserted {len(tweets)} tweets')
    except pymongo.errors.BulkWriteError as e:
        _ou.error('Batch insert failed. The `catalog` command has likely already been executed. Try using the `record` command instead.')


@click.command('record', short_help='fetch and store latest tweets')
def record():
    '''
    Fetches the last 20 tweets and stores any that are new
    '''

    statuses = list(reversed(_api.GetUserTimeline(screen_name=_twitter_config['screen_name'])))
    new_tweets = False

    for status in statuses:
        tweet = prepare_tweet(status)

        try:
            _db_tweets.insert_one(tweet)
            new_tweets = True
            _ou.info(f'Good news, Donnie just shed some new wisdom on {status.created_at}!')
        except pymongo.errors.DuplicateKeyError as e:
            pass

    if not new_tweets:
        _ou.warning('No new insight from The Tweeter in Chief...')


def prepare_tweet(status):
    # Use the tweet id as the mongodb collection _id. This assumes we never 
    # get a duplicate tweet id. 
    tweet = {
        '_id': status.id_str,
        'created_at': status.created_at,
        'full_text': status.full_text,
        'favorite_count': status.favorite_count,
        'retweet_count': status.retweet_count,
        'hashtags': [hashtag.text for hashtag in status.hashtags],
        'source': status.source,
        'urls': [{'expanded_url': url.expanded_url, 'url': url.url} for url in status.urls],
        'user_mentions': [{'id': user.id, 'screen_name': user.screen_name} for user in status.user_mentions]
    }

    # If this is a retweet, just store the ID. The original tweet can be
    # looked up later if needed.
    if status.retweeted_status:
        tweet['retweeted_status'] = {}
        tweet['retweeted_status']['id'] = status.retweeted_status.id_str

    return tweet


@click.command('playback', short_help='print all stored tweets')
def playback():
    '''
    Prints all stored tweets
    '''

    for tweet in _db_tweets.find().sort("_id", pymongo.ASCENDING):
        print(f'[{tweet["created_at"]}] {tweet["full_text"]}\n')


@click.command('frequency', short_help='get unique word counts')
def frequency():
    '''
    Gets a list of unique words in all tweets and a count of their occurrences
    '''

    best_words = {}
    largest_word_length = 0
    punctuation_to_keep = ['@', '#', '-']
    punctuation_to_remove = re.sub('[' + ''.join(punctuation_to_keep) + ']', '', string.punctuation)
    punctuation_to_remove = punctuation_to_remove + '“”…'
    translator = str.maketrans('', '', punctuation_to_remove)

    for tweet in _db_tweets.find().sort("_id", pymongo.ASCENDING):
        if 'retweeted_status' in tweet:
            continue # Skip retweets

        # Clean the tweet. Remove URLs, numbers, and specified punctuation.
        text = tweet['full_text'].lower().strip()
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'\d+', '', text)
        text = text.replace('...', ' ')
        text = text.replace('\n', ' ')
        text = html.unescape(text)
        text = text.translate(translator)

        words = text.strip().split(' ')

        for word in words:
            if len(word) > largest_word_length:
                largest_word_length = len(word)

            if word == '' or word in punctuation_to_keep:
                continue
            elif word in best_words:
                best_words[word] += 1
            else:
                best_words[word] = 1

    best_words = sorted(best_words.items(), key=itemgetter(1), reverse=False)

    _ou.info(f'@{_twitter_config["screen_name"]} really does have the best words!')
    _ou.info('Here are his most frequent:')
    
    for word_info in best_words:
        print(f'{word_info[0]: <{largest_word_length}} {word_info[1]}')


# Setup available commands
cli.add_command(catalog)
cli.add_command(record)
cli.add_command(playback)
cli.add_command(frequency)


if __name__ == "__main__":
    cli()
