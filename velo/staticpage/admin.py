# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from velo.staticpage.models import StaticPage
from velo.staticpage.forms import StaticPageForm


class StaticPageAdmin(admin.ModelAdmin):
    form = StaticPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'is_published', 'competition')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'language', 'ordering')}),
    )
    list_display = ('url', 'title', 'competition', 'language', 'is_published', 'ordering')
    list_filter = ('enable_comments', 'competition')
    search_fields = ('url', 'title')

admin.site.register(StaticPage, StaticPageAdmin)
