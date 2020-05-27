from django.db import models

# Create your models here.
class DailyScore(models.Model):
    date=models.DateField()
    dateTime=models.DateTimeField(auto_now=True)
    score = models.FloatField()
    
    positiveCount= models.IntegerField(default=0)
    negativeCount=models.IntegerField(default=0)
    neutralCount=models.IntegerField(default=0)
    
    def __str__(self):
        return 'Date: ' + str(self.date) + ' Score: ' +str(self.score)
    
class Tweet(models.Model):
    date = models.DateField(auto_now=True)
    username=models.CharField(max_length=20)
    text= models.TextField(max_length=400)
    polarity = models.FloatField()
    
    def __str__(self):
        return 'Username: ' + self.username

class HourlyScore(models.Model):
    date=models.DateField()
    dateTime=models.DateTimeField(auto_now=True)
    score = models.FloatField()
    
    positiveCount= models.IntegerField(default=0)
    negativeCount=models.IntegerField(default=0)
    neutralCount=models.IntegerField(default=0)
    
    def __str__(self):
        return 'DateTime: ' + str(self.dateTime) + ' Score: ' +str(self.score)
    
    
    
    