# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin

from velo.results.models import DistanceAdmin


class DistanceModelAdmin(admin.ModelAdmin):
    list_filter = ('competition', )
    list_display = ('__unicode__', 'competition', 'distance', 'zero', 'distance_actual')


admin.site.register(DistanceAdmin, DistanceModelAdmin)
