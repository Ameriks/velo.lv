from django.contrib import admin
from django.db import models
# Register your models here.
from news.models import Notification, News


class NewsAdmin(admin.ModelAdmin):
    exclude = ('image', 'created_by', 'modified_by')

admin.site.register(Notification)
admin.site.register(News, NewsAdmin)

