#!/bin/env python

import urllib2
import json
import datetime
from abc import ABCMeta
from urllib import urlencode
from abc import abstractmethod
from urlparse import urlunparse
from bs4 import BeautifulSoup
from time import sleep
import logging as log
import md5
import re
import psycopg2
#from connect import do_connect
#from connect import close_connection
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

__author__ = 'Alexandre Paixao'

class TwitterSearch:

    __metaclass__ = ABCMeta

    def __init__(self, rate_delay, error_delay=5):
        """
        :param rate_delay: How long to pause between calls to Twitter
        :param error_delay: How long to pause when an error occurs
        """
        self.rate_delay = rate_delay
        self.error_delay = error_delay

    def search(self, query):
        self.perform_search(query)

    def perform_search(self, query):
        """
        Scrape items from twitter
        :param query:   Query to search Twitter with. Takes form of queries constructed with using Twitters
                        advanced search: https://twitter.com/search-advanced
        """
        url = self.construct_url(query)
        continue_search = True
        min_tweet = None
        response = self.execute_search(url)
        while response is not None and continue_search and response['items_html'] is not None:
            tweets = self.parse_tweets(response['items_html'])

            # If we have no tweets, then we can break the loop early
            if len(tweets) == 0:
                break

            # If we haven't set our min tweet yet, set it now
            if min_tweet is None:
                min_tweet = tweets[0]

            continue_search = self.save_tweets(tweets)

            # Our max tweet is the last tweet in the list
            max_tweet = tweets[-1]
            if min_tweet['tweet_id'] is not max_tweet['tweet_id']:
                max_position = "TWEET-%s-%s" % (max_tweet['tweet_id'], min_tweet['tweet_id'])
                url = self.construct_url(query, max_position=max_position)
                sleep(self.rate_delay)
                response = self.execute_search(url)

    def execute_search(self, url):
        """
        Executes a search to Twitter for the given URL
        :param url: URL to search twitter with
        :return: A JSON object with data from Twitter
        """
        try:
            # Specify a user agent to prevent Twitter from returning a profile card
            headers = {
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'
            }
            req = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(req)
            data = json.loads(response.read())
            return data

        # If we get a ValueError exception due to a request timing out, we sleep for our error delay, then make
        # another attempt
        except ValueError as e:
            print e.message
            print "Sleeping for %i" % self.error_delay
            sleep(self.error_delay)
            return self.execute_search(url)

    @staticmethod
    def parse_tweets(items_html):
        """
        Parses Tweets from the given HTML
        :param items_html: The HTML block with tweets
        :return: A JSON list of tweets
        """
        soup = BeautifulSoup(items_html, 'html.parser')     
        tweets = []
        for li in soup.find_all("li", class_='js-stream-item'):

            # If our li doesn't have a tweet-id, we skip it as it's not going to be a tweet.
            if 'data-item-id' not in li.attrs:
                continue

            tweet = {
                'tweet_id': li['data-item-id'],
                'text': None,
                'user_id': None,
                'created_at': None
            }           
            
            # Tweet Text
            text_p = li.find("p", class_="tweet-text")
            if text_p is not None:
                tweet['text'] = text_p.get_text().encode('utf-8').strip()
                #p.agent_info = u' '.join((agent_contact, agent_telno)).encode('utf-8').strip()

            # Tweet User ID, User Screen Name, User Name
            user_details_div = li.find("div", class_="tweet")
            if user_details_div is not None:
                tweet['user_id'] = user_details_div['data-user-id']
                #tweet['user_screen_name'] = user_details_div['data-user-id']
                #tweet['user_name'] = user_details_div['data-name']

            # Tweet date
            date_span = li.find("span", class_="_timestamp")
            if date_span is not None:
                tweet['created_at'] = float(date_span['data-time-ms'])

            tweets.append(tweet)
        return tweets

    @staticmethod
    def construct_url(query, max_position=None):
        """
        For a given query, will construct a URL to search Twitter with
        :param query: The query term used to search twitter
        :param max_position: The max_position value to select the next pagination of tweets
        :return: A string URL
        """

        params = {
            # Type Param
            'f': 'tweets',
            # Query Param
            'q': query
        }

        # If our max_position param is not None, we add it to the parameters
        if max_position is not None:
            params['max_position'] = max_position

        url_tupple = ('https', 'twitter.com', '/i/search/timeline', '', urlencode(params), '')
        return urlunparse(url_tupple)

    @abstractmethod
    def save_tweets(self, tweets):
        """
        An abstract method that's called with a list of tweets.
        When implementing this class, you can do whatever you want with these tweets.
        """


class TwitterSearchImpl(TwitterSearch):

    def __init__(self, rate_delay, error_delay, max_tweets):
        """
        :param rate_delay: How long to pause between calls to Twitter
        :param error_delay: How long to pause when an error occurs
        :param max_tweets: Maximum number of tweets to collect for this example
        """
        super(TwitterSearchImpl, self).__init__(rate_delay, error_delay)
        #self.max_tweets = max_tweets
        self.max_tweets = 50
        self.counter = 0 

    def save_tweets(self, tweets):
        """
        Just prints out tweets
        :return:
        """

        #conn = do_connect()
        #Conexao com banco de dados para salvar os twittes adquiridos
        conn = psycopg2.connect("dbname='extracao_twitter' user='postgres' host='127.0.0.1' password='vi124578'")
        
        cur  = conn.cursor()        
        
        for tweet in tweets:
            # Lets add a counter so we only collect a max number of tweets
            self.counter += 1

            if tweet['created_at'] is not None:
                t = datetime.datetime.fromtimestamp((tweet['created_at']/1000))
                #fmt = "%Y-%m-%d %H:%M:%S"
                fmt = "%Y-%m-%d"
                #print "%i [%s] - %s" % (self.counter, t.strftime(fmt), tweet['text'])
                #print "%i - \tUserId: %s \tCreated At: [%s] \tTweet: %s" % (self.counter, tweet['user_id'], t.strftime(fmt), tweet['text'])
                print "%i - UserId: %s Created At: [%s] Tweet: %s" % (self.counter, tweet['user_id'], t.strftime(fmt), tweet['text'])
                #print "%i - %s - [%s] %s" % (self.counter, tweet['user_id'], t.strftime(fmt), tweet['text'])
                txt_md5 = md5.new(tweet['text']).hexdigest()
                hash_tweet = re.sub(r'(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})', r'\1-\2-\3-\4-\5', txt_md5)
                #upsert_comment_python(id_plat integer, id_ds integer, id_at integer, dt date, id_rs integer, cmm text, hshcmm uuid )
                #print "Select upsert_comment_python(%s, %s, %s::text, %s::date, %s, %s::text, %s::uuid)" % (id_platform, 1, tweet['user_id'], t.strftime(fmt), tweet['tweet_id'], tweet['text'], hash_tweet,)
                user_id = str(tweet['user_id'])
                tweet_id = str(tweet['tweet_id'])
                #Executando a Query para armazenar os dados no banco
                cur.execute("Insert Into TABELA(%s, %s::date, %s, %s::text, %s::uuid)", (user_id, t.strftime(fmt), tweet_id, tweet['text'], hash_tweet,))


            # When we've reached our max limit, return False so collection stops
            if self.counter >= self.max_tweets:
                return False

        cur.close()
        conn.commit()
        #close_connection(conn)
        conn.close()
        
        return True


class TwitterSlicer(TwitterSearch):
    """
    Inspired by: https://github.com/simonlindgren/TwitterScraper/blob/master/TwitterSucker.py
    The concept is to have an implementation that actually splits the query into multiple days.
    The only additional parameters a user has to input, is a minimum date, and a maximum date.
    This method also supports parallel scraping.
    """
    def __init__(self, rate_delay, error_delay, since, until):
        super(TwitterSlicer, self).__init__(rate_delay, error_delay)
        self.since = since
        self.until = until
        self.counter = 0

    def search(self, query):
        n_days = (self.until - self.since).days
        for i in range(0, n_days):
            since_query = self.since + datetime.timedelta(days=i)
            until_query = self.since + datetime.timedelta(days=(i + 1))
            day_query = "%s since:%s until:%s" % (query, since_query.strftime("%Y-%m-%d"),
                                                  until_query.strftime("%Y-%m-%d"))
            self.perform_search(day_query)

    def save_tweets(self, tweets):
        """
        Just prints out tweets 
        :return: True always
        """
        #conn = do_connect()
        conn = psycopg2.connect("dbname='extracao_twitter' user='postgres' host='127.0.0.1' password='vi124578'")
        cur  = conn.cursor()        
        
        for tweet in tweets:
            # Lets add a counter so we only collect a max number of tweets
            self.counter += 1
            if tweet['created_at'] is not None:
                t = datetime.datetime.fromtimestamp((tweet['created_at']/1000))
                fmt = "%Y-%m-%d"
                #fmt = "%Y-%m-%d %H:%M:%S"
                log.info("%i [%s] - %s" % (self.counter, t.strftime(fmt), tweet['text']))
                #log.info( "%i - \tUserId: %s \tCreated At: [%s] \tTweet: %s" % (self.counter, tweet['user_id'], t.strftime(fmt), tweet['text']))
                #print "%i - \tUserId: %s \tCreated At: [%s] \tTweet: %s" % (self.counter, tweet['user_id'], t.strftime(fmt), tweet['text'])
                txt_md5 = md5.new(tweet['text']).hexdigest()
                hash_tweet = re.sub(r'(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})', r'\1-\2-\3-\4-\5', txt_md5)
                user_id = str(tweet['user_id'])
                tweet_id = str(tweet['tweet_id'])
                #Executando a Query para armazenar os dados no banco
                #cur.execute("Insert Into dados(%s, %s::date, %s, %s::text, %s::uuid)", (user_id, t.strftime(fmt), tweet_id, tweet['text'], hash_tweet,))
                cur.execute("Insert Into dados(user_id, strftime,tweet_id,tweet,hash_tweet) values(%s, %s, %s, %s, %s)",
                            (user_id, t.strftime(fmt), tweet_id, tweet['text'], hash_tweet))
                
                

                
        cur.close()
        conn.commit()
        #close_connection(conn)
        conn.close()

        return True


if __name__ == '__main__':
    log.basicConfig(level=log.INFO)

    #Define a palavra-chave a ser buscada
    search_query = "privatizacao"
    #search_query = "PPI"
    rate_delay_seconds = 0
    error_delay_seconds = 5
    
    """
    # Example of using TwitterSearch
    twit = TwitterSearchImpl(rate_delay_seconds, error_delay_seconds, None)
    twit.search(search_query)
    """ 
    
    # Example of using TwitterSlice
    # Define o período para busca dos twittes
    select_tweets_since = datetime.datetime.strptime("2017-09-05", '%Y-%m-%d')
    select_tweets_until = datetime.datetime.strptime("2017-09-15", '%Y-%m-%d')

    twitSlice = TwitterSlicer(rate_delay_seconds, error_delay_seconds, select_tweets_since, select_tweets_until)
    twitSlice.search(search_query)


    #print("TwitterSearch collected %i" % twit.counter)
    print("TwitterSlicer collected %i" % twitSlice.counter)