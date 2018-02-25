import twitter
import pymongo
from mcgpyutils import FileSystemUtils
from mcgpyutils import ConfigUtils
from mcgpyutils import OutputUtils

class TweetStorage:
    def __init__(self):
        self.ou = OutputUtils()
        fsu = FileSystemUtils()
        config = ConfigUtils()

        fsu.set_config_location(f'{fsu.get_path_to_script(__file__)}/config')
        config.parse_json_config(f'{fsu.get_config_location()}/trumppetserver_config.json')

        self.mongodb_config = config.get_json_config_field('mongodb')
        self.twitter_config = config.get_json_config_field('twitter')

        mongodb = pymongo.MongoClient(host=self.mongodb_config['server'],
                                      port=self.mongodb_config['port'],
                                      authSource=self.mongodb_config['db'],
                                      username=self.mongodb_config['user'],
                                      password=self.mongodb_config['pass'])
        db = mongodb[self.mongodb_config['db']]
        self.db_tweets = db[self.mongodb_config["collection"]]

        self.api = twitter.Api(consumer_key=self.twitter_config['consumer_key'],
                               consumer_secret=self.twitter_config['consumer_secret'],
                               access_token_key=self.twitter_config['access_token'],
                               access_token_secret=self.twitter_config['access_token_secret'],
                               tweet_mode='extended',
                               sleep_on_rate_limit=True)

        

    def get_all_tweets(self):
        return self.db_tweets.find().sort("_id", pymongo.ASCENDING)


    def get_oldest_tweet(self):
        return self.db_tweets.find_one(sort=[('_id', pymongo.ASCENDING)])


    def get_newest_tweet(self):
        return self.db_tweets.find_one(sort=[('_id', pymongo.DESCENDING)])


    def get_num_tweets(self):
        return self.db_tweets.count()


    def get_last_n_tweets(self, num):
        num_tweets = self.get_num_tweets()

        if not isinstance(num, int) and not num.isdigit():
            num = 20
        elif int(num) < 0:
            num = 1
        elif int(num) > num_tweets:
            num = num_tweets
        else:
            num = int(num)

        return self.db_tweets.find(sort=[('_id', pymongo.DESCENDING)], limit=num)


    def get_range_of_tweets(self, start, end):
        all_tweets = list(reversed(list(self.get_all_tweets())))
        return all_tweets[start:end]


    def catalog_all_tweets(self):
        max_tweet_archive = 3200
        tweets_per_call = 200
        oldest_tweet_id = None
        tweets = []
        batch = 1

        while len(tweets) < max_tweet_archive:
            statuses = self.api.GetUserTimeline(screen_name=self.twitter_config['screen_name'], 
                                                count=tweets_per_call,
                                                max_id=oldest_tweet_id)

            self.ou.info(f'Processing tweet batch {batch} ({len(statuses)} new, {len(tweets)} total)...')

            for i, status in enumerate(statuses):
                if i == 0 and oldest_tweet_id:
                    # max_id returns tweets greater than or EQUAL to the given ID.
                    # Skipping the first tweet of the current batch prevents 
                    # duplicating the last tweet of the previous batch.
                    continue
                tweets.append(self._prepare_tweet(status))

            oldest_tweet_id = statuses[-1].id_str
            batch += 1

        try:
            self.db_tweets.insert_many(list(reversed(tweets)))
            self.ou.info(f'Inserted {len(tweets)} tweets')
            return len(tweets)
        except pymongo.errors.BulkWriteError as e:
            self.ou.error('Batch insert failed. The `catalog` command has likely already been executed. Try using the `record` command instead.')
            return -1


    def record_new_tweets(self):
        tweets_per_call = 200
        new_tweets = False

        timeline = self.api.GetUserTimeline(screen_name=self.twitter_config['screen_name'],
                                            count=tweets_per_call)
        statuses = list(reversed(timeline))

        for status in statuses:
            tweet = self._prepare_tweet(status)

            try:
                self.db_tweets.insert_one(tweet)
                new_tweets = True
                self.ou.info(f'Good news, President Trump just shed some new wisdom on {status.created_at}!')
            except pymongo.errors.DuplicateKeyError as e:
                pass

        if not new_tweets:
            self.ou.warning('No new insight from The Tweeter in Chief...')

        return new_tweets


    def _prepare_tweet(self, status):
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
