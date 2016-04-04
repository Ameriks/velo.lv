from gallery.models import Album
from velo.mixins.table import GetRequestTableKwargs
from django_tables2 import tables, A, LinkColumn, Column
from django.utils.translation import ugettext_lazy as _


__all__ = ['AlbumTable', ]

class AlbumTable(GetRequestTableKwargs, tables.Table):
    competition = Column("Competition", accessor="competition.get_full_name", order_by="competition")
    title = LinkColumn('gallery:album_pick', args=[A('pk')])
    class Meta:
        model = Album
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "title", "gallery_date", 'photographer', 'competition', 'is_internal', 'is_agency')
        per_page = 100
        template = "bootstrap/table.html"
        empty_text = _("There are no records")
        order_by = ['-gallery_date', ]
