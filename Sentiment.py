import re
import tweepy
import pandas as pd
from textblob import TextBlob
from datetime import datetime
from threading import Timer
import os
import django
from decouple import config
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')
django.setup()
from sentiment.models import DailyScore,Tweet
from django.db.models import Model

consumer_key = config('consumer_key')
consumer_secret = config('consumer_secret')
access_token = config('access_token')
access_token_secret = config('access_token_secret')

hashtag_phrase = "Covid"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

analyzer = SentimentIntensityAnalyzer()

def sentiment_script():

        final = pd.DataFrame()

        for tweet in tweepy.Cursor(api.search, q=hashtag_phrase + ' -filter:retweets', lang="en", tweet_mode='extended').items(2000):

                text = tweet.full_text
                screen_name = tweet.user.screen_name

                text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

                textVader = analyzer.polarity_scores(text)
                blob = TextBlob(text)
                polarity=blob.sentiment.polarity


                if(polarity == 0):
                        polarityScore = "Neutral"
                elif(polarity > 0):
                        polarityScore = "Positive"
                elif(polarity < 0):
                        polarityScore = "Negative"

                if (-0.05 < textVader['compound'] < 0.05):
                        polarityScoreVader = "Neutral"
                elif (textVader['compound'] >= 0.05):
                        polarityScoreVader = "Positive"
                elif (textVader['compound'] <= -0.05):
                        polarityScoreVader = "Negative"
                
                d = {'Tweet':[text], 'Username':[screen_name], 'Polarity':[textVader['compound']],'Sentiments':[polarityScore]}
                #t = {'Textblob':[polarity],'Vader':[textVader['compound']],'SentimentsBlob':[polarityScore], 'SentimentsVader':[polarityScoreVader]}
                df = pd.DataFrame(data=d)

                final = final.append(df)

        mean = final.mean()

        print(final)
        print(mean)


        numberPositiveV = str(final.Sentiments.str.count("Positive").sum())
        numberNegativeV = str(final.Sentiments.str.count("Negative").sum())
        numberNeutralV = str(final.Sentiments.str.count("Neutral").sum())
        print("")
        print("Number of positive tweets: " + numberPositiveV)
        print("Number of negative tweets: " + numberNegativeV)
        print("Number of neutral tweets: " + numberNeutralV)
        
        todays_score = DailyScore(score=mean)
        todays_score.save()

#Running the script
sentiment_script()