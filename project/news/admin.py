from django.contrib import admin

# Register your models here.
from news.models import Notification

admin.site.register(Notification)