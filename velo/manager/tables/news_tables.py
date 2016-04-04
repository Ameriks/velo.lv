from news.models import News
from velo.mixins.table import GetRequestTableKwargs
from django_tables2 import tables, A, LinkColumn, Column
from django.utils.translation import ugettext_lazy as _


__all__ = ['ManageNewsTable', ]

class ManageNewsTable(GetRequestTableKwargs, tables.Table):
    title = LinkColumn('manager:news', args=[A('pk')])
    class Meta:
        model = News
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "title", "language", 'competition', 'published_on', )
        per_page = 100
        template = "bootstrap/table.html"
        empty_text = _("There are no records")
        order_by = ['-published_on', ]