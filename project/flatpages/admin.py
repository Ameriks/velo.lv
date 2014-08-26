from django.contrib import admin
from flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from flatpages.forms import FlatpageForm

class FlatPageAdmin(admin.ModelAdmin):
    form = FlatpageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'is_published', 'competition')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'language', 'ordering')}),
    )
    list_display = ('url', 'title', 'competition', 'language', 'is_published', 'ordering')
    list_filter = ('enable_comments', 'competition')
    search_fields = ('url', 'title')

admin.site.register(FlatPage, FlatPageAdmin)
