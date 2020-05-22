from django.shortcuts import render
from sentiment.models import DailyScore

def index(request):
    context={}
    scores=[]
    dates=[]
    data= DailyScore.objects.order_by('date')
   
    for item in data:
        scores.append(item.score)
        dates.append(str(item.date))
        print(str(item.date))
        
    context['scores']=scores
    context['dates']=dates 
    return render(request,'sentiment/index.html',context)
