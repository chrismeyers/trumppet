import sys
import twitter
import click
import pymongo
from mcgpyutils import FileSystemUtils
from mcgpyutils import ConfigUtils

if __name__ == "__main__":
    from __version__ import __version__
else:
    from .__version__ import __version__


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
                   tweet_mode='extended')


@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.pass_context
def cli(context):
    pass


@click.command()
def record():
    statuses = _api.GetUserTimeline(screen_name='realDonaldTrump')
    new_tweets = False

    for status in statuses:
        # Use the tweet id as the mongodb collection _id. This assumes we never get
        # a duplicate tweet id. 
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

        try:
            _db_tweets.insert_one(tweet)
            new_tweets = True
            print(f'Good news, Donnie just shed some new wisdom on {status.created_at}!')
        except pymongo.errors.DuplicateKeyError as e:
            pass

    if not new_tweets:
        print('No new insight from The Tweeter in Chief...')


@click.command()
def playback():
    for tweet in _db_tweets.find().sort("_id", pymongo.ASCENDING):
        print(f'[{tweet["created_at"]}] {tweet["full_text"]}\n')


# Setup available commands
cli.add_command(record)
cli.add_command(playback)


if __name__ == "__main__":
    cli()
