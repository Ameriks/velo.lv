# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin

from velo.news.models import Notification, News


class NewsAdmin(admin.ModelAdmin):
    exclude = ('image', 'created_by', 'modified_by')

admin.site.register(Notification)
admin.site.register(News, NewsAdmin)

