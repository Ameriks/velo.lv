# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin

from velo.results.models import Leader
from velo.supporter.models import Supporter, CompetitionSupporter, Logo


class LogoInline(admin.TabularInline):
    model = Logo
    extra = 0


class CompetitionSupporterInline(admin.TabularInline):
    model = CompetitionSupporter
    extra = 0


class SupporterAdmin(admin.ModelAdmin):
    inlines = (LogoInline, CompetitionSupporterInline)


admin.site.register(Supporter, SupporterAdmin)
admin.site.register(Leader)
