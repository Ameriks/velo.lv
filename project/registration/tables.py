from django.utils.safestring import mark_safe
import django_tables2 as tables

from django.utils.translation import ugettext_lazy as _
import itertools

from registration.models import Participant, Application
from django_tables2.utils import A


class ApplicationTable(tables.Table):
    id = tables.LinkColumn('application', args=[A('code')])

    def render_competition(self, value):
        return value.get_full_name

    def render_payment_status(self, value, record):
        if record.external_invoice_code:
            return mark_safe("%s <a href='https://www.e-rekins.lv/d/i/%s/'>%s</a>" % (value, record.external_invoice_code, _('Download Invoice')))
        return value

    class Meta:
        model = Application
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "competition", "created", "payment_status", )
        empty_text = _("You haven't created any application.")
        order_by = ("-created")
        per_page = 20
        template = "bootstrap/table.html"



class ParticipantTable(tables.Table):
    # all_numbers = tables.Column(empty_values=(), verbose_name='#')
    primary_number = tables.Column(empty_values=(), verbose_name='Starta numurs')
    year = tables.Column(verbose_name=_('Year'), accessor='birthday.year', order_by='birthday')
    team = tables.Column(empty_values=(), verbose_name=_('Team'))


    def render_primary_number(self, record):
        if not record.primary_number:
            return '-'
        else:
            return record.primary_number

    def render_team(self, record, *args, **kwargs):
        if record.team:
            return mark_safe('<a href="#">%s</a>' % record.team)
        elif record.team_name:
            return '%s' % record.team_name
        else:
            return '-'

    def __init__(self, *args, **kwargs):
         super(ParticipantTable, self).__init__(*args, **kwargs)

         self.counter = itertools.count(1)

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("first_name", "last_name", "bike_brand2", "group", 'primary_number') # all_numbers
        sequence = ("primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        empty_text = _("There are no participants")
        order_by = ("primary_number")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"


class ParticipantTableWithResult(tables.Table):
    # all_numbers = tables.Column(empty_values=(), verbose_name='#')
    primary_number = tables.Column(empty_values=(), verbose_name='#')
    year = tables.Column(verbose_name=_('Year'), accessor='birthday.year', order_by='birthday')
    team = tables.Column(empty_values=(), verbose_name=_('Team'))
    last_year_result = tables.Column(empty_values=(), verbose_name=_("Last Year's Result"), accessor='last_year_result')

    def render_last_year_result(self, record):
        if not record.last_year_result:
            return '-'
        else:
            return record.last_year_result


    def render_primary_number(self, record):
        if not record.primary_number:
            return '-'
        else:
            return record.primary_number

    def render_team(self, record, *args, **kwargs):
        if record.team:
            return mark_safe('<a href="#">%s</a>' % record.team)
        elif record.team_name:
            return '%s' % record.team_name
        else:
            return '-'

    def __init__(self, *args, **kwargs):
         super(ParticipantTableWithResult, self).__init__(*args, **kwargs)

         self.counter = itertools.count(1)

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("first_name", "last_name", "bike_brand2", "group", 'primary_number') # all_numbers
        sequence = ("primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        empty_text = _("There are no participants")
        order_by = ("last_year_result")
        # ordering = ('created')
        per_page = 200
        template = "bootstrap/table.html"
