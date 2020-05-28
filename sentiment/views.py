from django.shortcuts import render
from sentiment.models import DailyScore

def index(request):
    context={}
    scores=[]
    dates=[]
    positive=[]
    negative=[]
    neutral=[]
    data= DailyScore.objects.order_by('date')
   
    for item in data:
        scores.append(item.score)
        dates.append(str(item.date))
        positive.append(item.positiveCount)
        negative.append(item.negativeCount)
        neutral.append(item.neutralCount)
        
    context['scores']=scores
    context['dates']=dates 
    context['positive']=positive
    context['negative']=negative
    context['neutral']=neutral
    return render(request,'sentiment/index.html',context)
