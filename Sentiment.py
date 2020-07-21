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
import collections
import ast
import nltk

#Setting environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tracker.settings')
django.setup()
from sentiment.models import DailyScore, Tweet, HourlyScore, Word
from django.db.models import Model

#Twitter API access tokens
consumer_key = config('consumer_key')
consumer_secret = config('consumer_secret')
access_token = config('access_token')
access_token_secret = config('access_token_secret')

#Setting up Tweepy with access tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

hashtag_phrase = "Covid"

#Setting up Twitter API with Tweepy
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
analyzer = SentimentIntensityAnalyzer()

#Our script that runs hourly to gather 2,000 tweets from Twitter's API
def sentiment_script():

        #Declaring the data frame
        final = pd.DataFrame()
        word_list = []

        #Searches through 2,000 of the most recent tweets that contain the hashtag phrase and are in English. Ignores retweets.
        for tweet in tweepy.Cursor(api.search, q=hashtag_phrase + ' -filter:retweets', lang="en", tweet_mode='extended').items(2000):

                #Declaring variables for the data frame that take the username and the tweet text for a given tweet
                text = tweet.full_text
                screen_name = tweet.user.screen_name

                #Cleans the tweets
                text = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split())

                #Gathers the sentiment from the cleaned text for a given tweet
                textVader = analyzer.polarity_scores(text)

                #Classifies a tweet as positive/negative/neutral
                if (-0.05 < textVader['compound'] < 0.05):
                        polarityScore = "Neutral"
                elif (textVader['compound'] >= 0.05):
                        polarityScore = "Positive"
                elif (textVader['compound'] <= -0.05):
                        polarityScore = "Negative"
                
                #Gather nouns in tweets 
                blob = TextBlob(text)
                nouns = (str(blob.noun_phrases))
                word_list.append(nouns)
                
                #Creating the dataframe and appending it
                d = {'Tweet':[text], 'Username':[screen_name], 'Polarity':[textVader['compound']], 'Sentiment':[polarityScore]}
                df = pd.DataFrame(data=d)
                final = final.append(df)
        
        #gather most popular words and save them to database
        calculate_top_10_words(word_list)

        #Declaring a variable that takes the final mean and rounds it
        hourly_mean = round(final.mean(),3)

        #Counts the total number of positive, negative, and neutral tweets for a given hour
        numberPositive = str(final.Sentiment.str.count("Positive").sum())
        numberNegative = str(final.Sentiment.str.count("Negative").sum())
        numberNeutral = str(final.Sentiment.str.count("Neutral").sum())
        
        #Gets an hourly score for the 2,000 tweets that is aggregated at the end of the day
        hourly_score = HourlyScore(score=hourly_mean, positiveCount=numberPositive, negativeCount=numberNegative, neutralCount=numberNeutral,date=datetime.date.today())
        hourly_score.save()

        now = datetime.datetime.now()
        
        #Aggregates the hourly scores at 11:00pm UTC
        if(now.hour == 23):
                calculate_daily_score()
                clean_up()


def calculate_top_10_words(word_list):
        #List of words to exclude from word counter 
        exclude_list = ['covid','don t','didn t','covid19',
                       'coronavirus','your','please','haven t',
                       'read','don','thank','thanks','won t', 'doesn t',
                       'wasn t']
        
        hours_sentences = []
        hours_words = []
        
        #convert our word list to a better format 
        for sent in word_list:
                parsed_list = ast.literal_eval(sent)
                hours_sentences.append(parsed_list)
        
        #flatten the list in to a list of strings         
        for sentence_list in hours_sentences:
                for word in sentence_list:
                        if(word not in exclude_list):
                                hours_words.append(word)

        #collect 10 most popular words
        counter = collections.Counter(hours_words)
        top_10_words = counter.most_common(10)
        
        for word_pair in top_10_words:
                try:
                        word = Word(word=word_pair[0], count=word_pair[1], date=datetime.date.today())
                        word.save()
                except Exception:
                        print("There was a string formatting error while trying to save the word list.")


def calculate_daily_score():
        allScores = HourlyScore.objects.filter(date=datetime.date.today())
        counter=0
        scoreSum=0
        posSum=0
        negSum=0
        neutSum=0
                
        #Sums up the scores and divides by the number of hours
        for score in allScores:
                counter+=1
                scoreSum+=score.score
                posSum+=score.positiveCount
                negSum+=score.negativeCount
                neutSum+=score.neutralCount

        samplemean= scoreSum/max(1,counter)
        samplemean=round(samplemean,3)

        totaltweets = posSum+negSum+neutSum

        #In case scheduler fails
        if totaltweets < 48000:
                posSum = (posSum/totaltweets) * 48000
                neutSum = (neutSum/totaltweets) * 48000
                negSum = (negSum/totaltweets) * 48000

        print("Number of hourly scores:{} SumScores:{} Sample Mean:{} \n positiveTweets:{} negativeTweets:{} neutral tweets: {}".
                format(counter,scoreSum,samplemean,posSum,negSum,neutSum))
                
        daily_score=DailyScore(score=samplemean, positiveCount=posSum, negativeCount=negSum, neutralCount=neutSum,date=datetime.date.today())
        daily_score.save()

#Cleans up database by deleting previous days word data 
def clean_up():
        words = Word.objects.order_by('-dateTime')[:10].values_list("id", flat=True)
        Word.objects.exclude(pk__in=list(words)).delete()
        print('Clean up completed.')
               
#Runs the script 
sentiment_script()