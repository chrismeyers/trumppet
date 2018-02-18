import twitter
import click
from mcgpyutils import FileSystemUtils
from mcgpyutils import ConfigUtils
from mcgpyutils import OutputUtils
from .storage import TweetStorage
from .analyzer import TweetAnalyzer
from .__version__ import __version__

_ou = OutputUtils()
_fsu = FileSystemUtils()
_config = ConfigUtils()

_fsu.set_config_location(f'{_fsu.get_path_to_script(__file__)}/config')
_config.parse_json_config(f'{_fsu.get_config_location()}/trumppet_config.json')
_twitter_config = _config.get_json_config_field('twitter')

_api = twitter.Api(consumer_key=_twitter_config['consumer_key'],
                   consumer_secret=_twitter_config['consumer_secret'],
                   access_token_key=_twitter_config['access_token'],
                   access_token_secret=_twitter_config['access_token_secret'],
                   tweet_mode='extended',
                   sleep_on_rate_limit=True)

_storage = TweetStorage(_config, _api)
_analyzer = TweetAnalyzer(_storage)


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

    _storage.catalog_all_tweets()


@click.command('record', short_help='fetch and store latest tweets')
def record():
    '''
    Fetches the last 20 tweets and stores any that are new
    '''

    _storage.record_new_tweets()


@click.command('playback', short_help='print all stored tweets')
def playback():
    '''
    Prints all stored tweets
    '''

    tweets = _storage.get_all_tweets()

    for tweet in tweets:
        print(f'[{tweet["created_at"]}] {tweet["full_text"]}\n')


@click.command('frequency', short_help='get unique word counts')
def frequency():
    '''
    Gets a list of unique words in all tweets and a count of their occurrences
    '''

    best_words, largest_word_length = _analyzer.get_word_frequency()

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
