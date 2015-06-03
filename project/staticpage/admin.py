from django.contrib import admin
from staticpage.models import StaticPage
from django.utils.translation import ugettext_lazy as _
from staticpage.forms import StaticPageForm

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
