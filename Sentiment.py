import re
import tweepy
import pandas as pd
from textblob import TextBlob
from datetime import datetime
from threading import Timer
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')
django.setup()
from sentiment.models import DailyScore,Tweet
from django.db.models import Model


x = datetime.today()
y = x.replace(day=x.day+1, hour=14, minute=0, second=0, microsecond=0)
delta_t = y-x
secs = delta_t.seconds+1

consumer_key = 'IXUhw2wnVqkcdbBTH0EAXNFib'
consumer_secret = '9qKsjBuOEfCzYFAh2FZn547IfQF8uz6vsqgckyaZcPYpCh6JWS'
access_token = '1209000765773295616-zJNYvN4MrQqsvMjMXOHXDDrMazAH6T'
access_token_secret = '0NqekKBM37Ol5cxuNdRF8apfAShUjf7q08PJ4PlrRyfp2'

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
                
                try:
                    row=Tweet(username=screen_name,text=text,polarity=polarity)
                    row.save()
                except Exception:
                    print('Error Saving Tweet')
                
                final = final.append(df)

        
        
        mean = final.mean()
        
        print(final)
        print(mean)
        
        todays_score=DailyScore(score=mean)
        todays_score.save()

        

#Running the script
sentiment_script()