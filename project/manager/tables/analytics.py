from difflib import get_close_matches
from django.core.urlresolvers import reverse
from django_tables2 import tables, A, LinkColumn, Column
from django.utils.safestring import mark_safe
from core.models import Competition
from registration.models import Participant, Number
from results.models import Result, HelperResults
from velo.mixins.table import GetRequestTableKwargs
from django.utils.translation import ugettext_lazy as _


__all__ = [
    'ManageResultNonParticipantTable', 'ManageFindNumberViewTable', 'HelperResultsMatchViewTable',
]

class ManageResultNonParticipantTable(GetRequestTableKwargs, tables.Table):
    class Meta:
        model = Result
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", 'participant', 'number', )
        per_page = 100
        template = "bootstrap/table.html"
        empty_text = _("There are no records")


class ManageFindNumberViewTable(GetRequestTableKwargs, tables.Table):
    _slugs = None
    matching_slug = Column(empty_values=(), verbose_name='Matching Slug', orderable=False)

    def render_matching_slug(self, record, **kwargs):
        matches = get_close_matches(record.slug, self._slugs.get(record.distance_id), 1, 0.5)
        if matches:
            return matches[0]
        else:
            return None

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.last_name))


    def __init__(self, *args, **kwargs):
        super(ManageFindNumberViewTable, self).__init__(*args, **kwargs)
        competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
        self._slugs = {obj.id: [p.participant_slug for p in Number.objects.filter(distance=obj).exclude(participant_slug='')] for obj in competition.get_distances()}


    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", 'distance', 'first_name', 'last_name', 'birthday', 'slug', )
        per_page = 10
        template = "bootstrap/table.html"
        empty_text = _("There are no records")



class HelperResultsMatchViewTable(GetRequestTableKwargs, tables.Table):
    current_slug = Column(accessor='participant.slug')

    def render_current_slug(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.participant_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.participant.slug))

    class Meta:
        model = HelperResults
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", 'matches_slug', )
        sequence = ('id', 'current_slug', 'matches_slug', )
        per_page = 30
        template = "bootstrap/table.html"
        empty_text = _("There are no records")
        order_by = ("-id",)




