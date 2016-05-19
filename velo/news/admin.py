# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin
from django import forms

from velo.manager.widgets import PhotoPickWidget
from velo.news.models import Notification, News


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ("language", 'title', 'slug', 'competition', 'published_on', 'image', 'intro_content', 'content')
        widgets = {
            'image': PhotoPickWidget,
        }


class NewsAdmin(admin.ModelAdmin):
    exclude = ('created_by', 'modified_by')
    form = NewsForm
    add_form_template = "admin/change_news.html"
    change_form_template = "admin/change_news.html"


admin.site.register(Notification)
admin.site.register(News, NewsAdmin)

