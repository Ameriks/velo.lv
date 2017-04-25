from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from markdownx.admin import MarkdownxModelAdmin

from velo.staticpage.models import StaticPage
from velo.staticpage.forms import StaticPageForm


class StaticPageAdmin(MarkdownxModelAdmin):
    form = StaticPageForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'content_md', 'is_published', 'competition')}),
        (_('Advanced options'), {'classes': ('collapse',), 'fields': ('enable_comments', 'language', 'ordering')}),
    )
    list_display = ('url', 'title', 'competition', 'language', 'is_published', 'ordering')
    list_filter = ('enable_comments', 'competition')
    search_fields = ('url', 'title')

    add_form_template = "admin/change_news.html"
    change_form_template = "admin/change_news.html"


admin.site.register(StaticPage, StaticPageAdmin)
