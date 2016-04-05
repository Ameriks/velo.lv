# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin

from velo.advert.models import FlashBanner


class FlashBannerAdmin(admin.ModelAdmin):
    list_filter = ('competition', 'status')
    list_display = ('title', 'status', 'competition', 'location', 'ordering', 'url')


admin.site.register(FlashBanner, FlashBannerAdmin)
