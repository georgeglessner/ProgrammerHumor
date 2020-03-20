#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import tweepy
from time import sleep
from credentials import *
import praw
import requests
import urllib
import os
import re
import sys
from HTMLParser import HTMLParser

# connect to reddit
reddit = praw.Reddit(
    client_id=ID,
    client_secret=SECRET,
    password=PASSWORD,
    user_agent=AGENT,
    username=USERNAME)

# connect to twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# create images folder if one does not exits
if not os.path.exists('./images'):
    os.mkdir('./images')

caption = ''
source = ''
extension = ''

h = HTMLParser()

MAX_FILESIZE = 3072000

def get_images():
    global caption, source
    count = 0
    ids = []
    statuses = []

    # grab 50 most recent tweets to avoid duplicates
    tweets = api.user_timeline(screen_name='pr0grammerhum0r', count=50)
    for status in tweets:
        status = status.text.split('https', 1)
        status = status[0].strip()
        status = h.unescape(status)

        # lengthy statuses cut off, cannot compare accurately, get duplicates
        # do not add these statuses to list
        if len(status) < 100:
	    if len(status) == len(status.encode('utf-8')):
                statuses.append(status)
        else:
            pass

    # find Reddit post to post to Twitter
    for submission in reddit.subreddit('programmerhumor').hot():
        if 'https://i.imgur.com/' in submission.url or 'https://i.redd.it' in submission.url:
            if len(submission.title) < 100 and len(submission.title) == len(submission.title.encode('utf-8'))::
                if submission.title not in statuses:
                    img_url = submission.url
                    _, extension = os.path.splitext(img_url)
                    source = 'https://www.reddit.com/r/programmerhumor/comments/' + str(
                        submission)
                    if extension in ['.jpg', '.jpeg', '.gif', '.png']:
                        urllib.urlretrieve(img_url,
                                           'images/image{}'.format(extension))
                        file_size = os.stat('images/image{}'.format(extension))
                        if file_size.st_size > MAX_FILESIZE:
                            pass
                        else:
                            caption = submission.title + " " + source
                            break
                else:
                    print 'Tweet already exists in timeline'
    send_tweet(extension)


# favorite tweets matching keyword
def favorite_tweets():
    results = api.search(q='"programmer humor"', lang="en")
    for result in results:
        if result.author._json['screen_name'] != 'PR0GRAMMERHUM0R':
            try:
                if not result.favorited:
                    api.create_favorite(result.id)
            except tweepy.TweepError:
                pass

# feature request - reply to tweet with Reddit source
def comment_source():
    global source
    tweet_id = 0
    for tweet in api.user_timeline('pr0grammerhum0r', count=1):
        tweet_id = tweet.id
    reply = '@PR0GRAMMERHUM0R ' + source
    api.update_status(reply, in_reply_to_status_id=tweet_id)


# send tweet with image, sleep for 2 hours
def send_tweet(extension):
    api.update_with_media("images/image" + extension, caption)
    #favorite_tweets()
    #comment_source()
   #get_images()
    sys.exit()


if __name__ == '__main__':
    get_images()
