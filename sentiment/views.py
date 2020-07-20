from django.shortcuts import render
from sentiment.models import DailyScore, Word

def index(request):
    context={}
    scores=[]
    dates=[]
    positive=[]
    negative=[]
    neutral=[]
    top_10_words =[]
    data= DailyScore.objects.order_by('date')
    words = Word.objects.order_by('-dateTime')[:10]
   
    for item in data:
        scores.append(item.score)
        dates.append(str(item.date))
        positive.append(item.positiveCount)
        negative.append(item.negativeCount)
        neutral.append(item.neutralCount)

    for word in words:
        word_pair = [word.word, word.count]
        top_10_words.append(word_pair)

    top_10_words.sort(key=get_count,reverse=True) 

    context['scores']=scores
    context['dates']=dates 
    context['positive']=positive
    context['negative']=negative
    context['neutral']=neutral
    context['top_10_words'] =top_10_words

    return render(request,'sentiment/index.html',context)


def get_count(word_pair):
    return word_pair[1]