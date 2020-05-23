import re
import tweepy
import pandas as pd
from textblob import TextBlob
from datetime import datetime
from threading import Timer
import os
import django
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')
django.setup()
from sentiment.models import DailyScore,Tweet
from django.db.models import Model


x = datetime.today()
y = x.replace(day=x.day+1, hour=14, minute=0, second=0, microsecond=0)
delta_t = y-x
secs = delta_t.seconds+1

consumer_key = config('consumer_key')
consumer_secret = config('consumer_secret')
access_token = config('access_token')
access_token_secret = config('access_token_secret')

hashtag_phrase = "Covid"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def sentiment_script():

        final = pd.DataFrame()

        for tweet in tweepy.Cursor(api.search, q=hashtag_phrase + ' -filter:retweets', lang="en", tweet_mode='extended').items(2000):

                text = tweet.full_text
                screen_name = tweet.user.screen_name

                text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

                blob = TextBlob(text)
                polarity=blob.sentiment.polarity
                
                d = {'Tweet':[text], 'Username':[screen_name], 'Polarity':[polarity]}
                df = pd.DataFrame(data=d)
                
              
                
                final = final.append(df)

        
        
        mean = final.mean()
        
        print(final)
        print(mean)
        
        todays_score=DailyScore(score=mean)
        todays_score.save()

        

#Running the script
sentiment_script()