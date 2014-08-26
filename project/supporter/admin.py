from django.contrib import admin
from results.models import Leader
from supporter.models import Supporter, CompetitionSupporter, Logo


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
