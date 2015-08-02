from django.contrib import admin
from django.db import models
# Register your models here.
from redactor.widgets import AdminRedactorEditor
from news.models import Notification, News


class NewsAdmin(admin.ModelAdmin):
    formfield_overrides = {
            models.TextField: {'widget': AdminRedactorEditor},
    }

admin.site.register(Notification)
admin.site.register(News, NewsAdmin)


