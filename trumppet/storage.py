import pymongo
from mcgpyutils import OutputUtils

class TweetStorage:
    def __init__(self, config, api):
        self.api = api

        self.mongodb_config = config.get_json_config_field('mongodb')
        self.twitter_config = config.get_json_config_field('twitter')

        mongodb = pymongo.MongoClient(self.mongodb_config['server'], self.mongodb_config['port'])
        db = mongodb[self.mongodb_config['db']]
        self.db_tweets = db[self.mongodb_config["collection"]]

        self.ou = OutputUtils()
        

    def get_all_tweets(self):
        return self.db_tweets.find().sort("_id", pymongo.ASCENDING)


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
        statuses = list(reversed(self.api.GetUserTimeline(screen_name=self.twitter_config['screen_name'])))
        new_tweets = False

        for status in statuses:
            tweet = self._prepare_tweet(status)

            try:
                self.db_tweets.insert_one(tweet)
                new_tweets = True
                self.ou.info(f'Good news, Donnie just shed some new wisdom on {status.created_at}!')
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
