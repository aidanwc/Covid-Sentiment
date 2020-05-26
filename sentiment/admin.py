from django.contrib import admin

from sentiment.models import *

admin.site.register(DailyScore)
admin.site.register(Tweet)
admin.site.register(HourlyScore)
