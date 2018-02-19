import sys
import string
import re
import html
from operator import itemgetter
import random
import nltk
from mcgpyutils import ColorUtils as colors
from mcgpyutils import FileSystemUtils

class TweetAnalyzer:
    def __init__(self, storage):
        self.storage = storage
        self.fsu = FileSystemUtils()


    def get_word_frequency(self):
        best_words = {}
        largest_word_length = 0
        punctuation_to_keep = ['@', '#', '-']
        punctuation_to_remove = re.sub('[' + ''.join(punctuation_to_keep) + ']', '', string.punctuation)
        punctuation_to_remove = punctuation_to_remove + '“”…'
        translator = str.maketrans('', '', punctuation_to_remove)

        for tweet in self.storage.get_all_tweets():
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

        return sorted(best_words.items(), key=itemgetter(1), reverse=False), largest_word_length


    def search_tweets(self, phrase):
        found_tweets = []

        for tweet in self.storage.get_all_tweets():
            if re.search(phrase, tweet['full_text'], re.IGNORECASE):
                found_text = re.sub(phrase, f'{colors.RED}\g<0>{colors.RETURN_TO_NORMAL}', tweet['full_text'], 0, re.IGNORECASE)
                found_tweets.append({
                    'created_at': tweet['created_at'],
                    'full_text': found_text
                })

        return found_tweets


    def generate_trumpian_tweet(self):
        real_tweets = list(self.storage.get_all_tweets())
        tokenizer = nltk.data.load(f'{self.fsu.get_path_to_script(__file__)}/nltk_data/tokenizers/punkt/english.pickle')

        tweets = []
        selected_indexes = []
        while len(tweets) < 3:
            tweet_index = -1
            while (tweet_index < 0) or (tweet_index in selected_indexes) or ('retweeted_status' in real_tweets[tweet_index]):
                tweet_index = random.randrange(0, len(real_tweets) - 1)

            selected_indexes.append(tweet_index)
            sentences = tokenizer.tokenize(real_tweets[tweet_index]['full_text'])

            if(len(sentences) == 3 and sentences[0][-1] == '.' and sentences[1][-1] == '.' and sentences[2][-1] == '!'):
                tweets.append(sentences)

        return f'{tweets[0][0]} {tweets[1][1]} {tweets[2][2]}'
