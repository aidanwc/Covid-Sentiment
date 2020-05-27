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
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')
django.setup()
from sentiment.models import DailyScore,Tweet, HourlyScore
from django.db.models import Model

consumer_key = config('consumer_key')
consumer_secret = config('consumer_secret')
access_token = config('access_token')
access_token_secret = config('access_token_secret')

hashtag_phrase = "Covid"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

analyzer = SentimentIntensityAnalyzer()

def sentiment_script():

        final = pd.DataFrame()

        for tweet in tweepy.Cursor(api.search, q=hashtag_phrase + ' -filter:retweets', lang="en", tweet_mode='extended').items(2000):

                text = tweet.full_text
                screen_name = tweet.user.screen_name

                text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

                textVader = analyzer.polarity_scores(text)

                if (-0.05 < textVader['compound'] < 0.05):
                        polarityScore = "Neutral"
                elif (textVader['compound'] >= 0.05):
                        polarityScore = "Positive"
                elif (textVader['compound'] <= -0.05):
                        polarityScore = "Negative"
                
                d = {'Tweet':[text], 'Username':[screen_name], 'Polarity':[textVader['compound']], 'Sentiment':[polarityScore]}
                df = pd.DataFrame(data=d)

                final = final.append(df)

        hourly_mean = round(final.mean(),3)
       
        print()
        print(final)
        print(hourly_mean)

        numberPositive = str(final.Sentiment.str.count("Positive").sum())
        numberNegative = str(final.Sentiment.str.count("Negative").sum())
        numberNeutral = str(final.Sentiment.str.count("Neutral").sum())

        

        print("Number of positive tweets: " + numberPositive)
        print("Number of negative tweets: " + numberNegative)
        print("Number of neutral tweets: " + numberNeutral)
        print()
        
        hourly_score = HourlyScore(score=hourly_mean, positiveCount=numberPositive, negativeCount=numberNegative, neutralCount=numberNeutral)
        hourly_score.save()

        now = datetime.datetime.now()
        
        print("Today's date: {}".format(now.date()))
        print('Current time: {}\n'.format(now.hour))
        print(datetime.date.today())
        
        if(now.hour == 23):
                allScores = HourlyScore.objects.filter(date=datetime.date.today())
                counter=0
                scoreSum=0
                posSum=0
                negSum=0
                neutSum=0
                
                
                for score in allScores:
                        counter+=1
                        scoreSum+=score.score
                        posSum+=score.positiveCount
                        negSum+=score.negativeCount
                        neutSum+=score.neutralCount
                samplemean= scoreSum/max(1,counter)
                samplemean=round(samplemean,3)
                print("Number of hourly scores:{} SumScores:{} Sample Mean:{} \n positiveTweets:{} negativeTweets:{} neutral tweets: {}".
                      format(counter,scoreSum,samplemean,posSum,negSum,neutSum))
                
                daily_score=DailyScore(score=samplemean, positiveCount=posSum, negativeCount=negSum, neutralCount=neutSum)
                daily_score.save()


#Running Script 
sentiment_script()