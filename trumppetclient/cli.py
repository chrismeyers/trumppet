import sys
import json
import click
import requests
from mcgpyutils import OutputUtils
from mcgpyutils import FileSystemUtils
from mcgpyutils import ConfigUtils
from mcgpyutils import ColorUtils as colors
from .__version__ import __version__


_TRUMPSERVER_NOT_RESP = 'The trumppetserver is not responding, please try again later.'

_ou = OutputUtils()
_fsu = FileSystemUtils()
_config = ConfigUtils()

_fsu.set_config_location(f'{_fsu.get_path_to_script(__file__)}/config')
_config.parse_json_config(f'{_fsu.get_config_location()}/trumppetclient_config.json')

# If another instance of the trumppetserver API is running, local or otherwise,
# it can be used instead of the default. 
if 'custom' in _config.get_json_config_field('trumppetserver')['base_url'] and \
  _config.get_json_config_field('trumppetserver')['base_url']['custom'] != '':
    _base_url = _config.get_json_config_field('trumppetserver')['base_url']['custom']
else:
    _base_url = _config.get_json_config_field('trumppetserver')['base_url']['default']


@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name=f'{colors.RED}trump{colors.WHITE}pet-c{colors.BLUE}lient{colors.RETURN_TO_NORMAL}', version=__version__)
@click.pass_context
def cli(context):
    '''
    Client component of a Donald Trump tweet analyzer. This application displays
    data retrieved from the server component through HTTP requests.
    '''
    
    # Show help if no command was specified.
    if context.invoked_subcommand is None:
        click.echo(context.get_help())


@click.command('playback', short_help='prints previous tweets')
@click.option('--num', default=20, help="the number of tweets to print")
def playback(num):
    '''
    Prints last --num tweets, default 20, max 50
    '''

    try:
        r = requests.get(f'{_base_url}/tweets/{num}')
    except requests.exceptions.ConnectionError as e:
        _ou.error(_TRUMPSERVER_NOT_RESP)
        sys.exit(1)

    tweets = r.json()

    for tweet in tweets:
        print(f'[{tweet["created_at"]}] {tweet["full_text"]}\n')


@click.command('frequency', short_help='get unique word counts')
def frequency():
    '''
    Gets a list of unique words in all tweets and a count of their occurrences
    '''

    try:
        r = requests.get(f'{_base_url}/frequency')
    except requests.exceptions.ConnectionError as e:
        _ou.error(_TRUMPSERVER_NOT_RESP)
        sys.exit(1)

    freq_data = r.json()

    largest_word_length = freq_data['largest_word_length']
    best_words = freq_data['best_words']

    _ou.info(f'Mr. Trump really does have the best words!')
    _ou.info('Here are his most frequent:')
    
    for word_info in best_words:
        print(f'{word_info[0]: <{largest_word_length}} {word_info[1]}')


@click.command('search', short_help='searches tweets for usage of a word or phrase')
@click.option('--phrase', required=True, nargs=1, help="the search query")
def search(phrase):
    '''
    Searches tweets for usage of a word or phrase
    '''

    payload = {
        "phrase": phrase
    }
    try:
        r = requests.post(f'{_base_url}/search', data=payload)
    except requests.exceptions.ConnectionError as e:
        _ou.error(_TRUMPSERVER_NOT_RESP)
        sys.exit(1)

    tweets = r.json()

    _ou.info(f'{len(tweets)} results for the term "{phrase}":')
    for tweet in tweets:
        print(f'[{tweet["created_at"]}] {tweet["full_text"]}\n')


@click.command('freestyle', short_help='generates a tweet that Trump posted...probably')
def freestyle():
    '''
    Generates a Trumpian-style tweet (Sentance. Sentance. Exclamation!) based on
    past tweets
    '''

    try:
        r = requests.get(f'{_base_url}/freestyle')
    except requests.exceptions.ConnectionError as e:
        _ou.error(_TRUMPSERVER_NOT_RESP)
        sys.exit(1)

    fake_news = r.json()

    _ou.info('At some point, Donald Trump probably said (this actually is fake news)...')
    print(fake_news['fake_tweet'])


# Setup available commands
cli.add_command(playback)
cli.add_command(frequency)
cli.add_command(search)
cli.add_command(freestyle)


if __name__ == "__main__":
    cli()
