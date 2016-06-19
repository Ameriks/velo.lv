from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.columns import LinkColumn
from django_tables2.utils import A

from velo.results.models import Result, ChipScan


__all__ = ['ManageResultTable', 'ManageChipScanTable']


class ManageResultTable(tables.Table):
    id = LinkColumn('manager:result', args=[A('competition_id'), A('id')], accessor="id", verbose_name=_('ID'), )
    distance = tables.Column(verbose_name=_('Distance'), accessor='participant.distance')
    first_name = tables.Column(verbose_name=_('First Name'), accessor='participant.first_name')
    last_name = tables.Column(verbose_name=_('Last Name'), accessor='participant.last_name')
    group = tables.Column(verbose_name=_('Group'), accessor='participant.group')
    time = tables.Column(verbose_name=_('Time'), accessor='time')

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant',
                      kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.participant_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.participant.last_name))

    class Meta:
        model = Result
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", "number", "avg_speed", "points_group", "points_distance", "status")
        sequence = ('id', 'competition', 'distance', 'number', 'first_name', 'last_name', 'time', 'avg_speed', 'group',
                    'points_group', 'points_distance', 'status')
        empty_text = _("There are no results")
        # order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.request_kwargs = kwargs.pop('request_kwargs')
        super().__init__(*args, **kwargs)


class ManageChipScanTable(tables.Table):
    time = tables.TimeColumn(verbose_name=_('Time'), accessor='time', format='H:i:s.u')

    def render_nr(self, record, **kwargs):
        url = reverse('manager:result_list', kwargs={'pk': self.request_kwargs.get('pk')})
        return mark_safe('<a href="%s?number=%s">%s</a>' % (url, record.nr.number, record.nr))

    class Meta:
        model = ChipScan
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "nr_text", "time_text", "nr", "time", "is_processed", "is_blocked", "url_sync")
        empty_text = _("There are no chip scans")
        per_page = 100
        template = "bootstrap/table.html"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.request_kwargs = kwargs.pop('request_kwargs')
        super().__init__(*args, **kwargs)

