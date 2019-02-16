import click
from mcgpyutils import OutputUtils
from mcgpyutils import ColorUtils as colors
from .storage import TweetStorage
from .__version__ import __version__

_ou = OutputUtils()
_storage = TweetStorage()


@click.group(invoke_without_command=True, context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(prog_name=f'{colors.RED}trump{colors.WHITE}pet-s{colors.BLUE}erver{colors.RETURN_TO_NORMAL}', version=__version__)
@click.pass_context
def cli(context):
    '''
    Server component of a Donald Trump tweet analyzer. This application manages
    the insertion of data into a MongoDB database from data received through the
    Twitter API.
    '''

    # Show help if no command was specified.
    if context.invoked_subcommand is None:
        click.echo(context.get_help())


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


# Setup available commands
cli.add_command(catalog)
cli.add_command(record)


if __name__ == "__main__":
    cli()
