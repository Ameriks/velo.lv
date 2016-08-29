# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django_tables2.utils import A
import django_tables2 as tables
import itertools

from velo.registration.models import Participant, Application, CompanyParticipant
from velo.velo.tables import CustomCheckBoxColumn, CustomSelectionCheckBoxColumn


class ApplicationTable(tables.Table):
    id = tables.LinkColumn('application', args=[A('code')])
    action = tables.TemplateColumn(verbose_name="", orderable=False, template_name="registration/table/my_application_action.html")

    def render_competition(self, value):
        return value.get_full_name

    class Meta:
        model = Application
        attrs = {"class": "table-block"}
        fields = ("id", "competition", "created", "payment_status", "action")
        empty_text = _("You haven't created any application.")
        order_by = ("-created")
        per_page = 20
        template = "base/table.html"


class ParticipantTableBase(tables.Table):
    year = tables.Column(verbose_name=_('Year'), accessor='birthday.year', order_by='birthday')
    team = tables.Column(empty_values=(), verbose_name=_('Team'))

    def render_team(self, record, *args, **kwargs):
        if record.team:
            return mark_safe('<a href="#">%s</a>' % record.team)
        elif record.team_name:
            return '%s' % record.team_name
        else:
            return '-'

    def __init__(self, *args, **kwargs):
        super(ParticipantTableBase, self).__init__(*args, **kwargs)
        self.counter = itertools.count(1)

    class Meta:
        model = Participant
        attrs = {"class": "table-block"}
        fields = ("first_name", "last_name", "bike_brand2", "group")
        sequence = ('first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        empty_text = _("There are no participants")
        order_by = ("last_name")
        per_page = 200
        template = "base/table.html"


class ParticipantTable(ParticipantTableBase):
    primary_number = tables.Column(verbose_name=_('Number'), default='-', accessor='primary_number')

    class Meta(ParticipantTableBase.Meta):
        fields = ("first_name", "last_name", "bike_brand2", "group", 'primary_number')
        sequence = ("primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        order_by = ("primary_number")


class ParticipantTableWCountry(ParticipantTableBase):
    primary_number = tables.Column(verbose_name=_('Number'), default='-', accessor='primary_number')

    class Meta(ParticipantTableBase.Meta):
        fields = ("first_name", "last_name", "country", "bike_brand2", "group", 'primary_number')
        sequence = ("primary_number", 'first_name', 'last_name', 'year', "country", 'group', 'team', 'bike_brand2',)
        order_by = ("primary_number")


class ParticipantTableWithPoints(ParticipantTable):
    calculated_total = tables.Column(verbose_name=_('Points'), accessor='calculated_total')

    class Meta(ParticipantTable.Meta):
        sequence = (
        "calculated_total", "primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        order_by = ("-calculated_total", "primary_number")


class ParticipantTableWithPassage(ParticipantTable):
    passage_assigned = tables.Column(verbose_name=_('Passage'), accessor='passage_assigned')

    class Meta(ParticipantTable.Meta):
        sequence = (
        "passage_assigned", "primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        order_by = ("passage_assigned", "primary_number")


class ParticipantTableWithLastYearPlace(ParticipantTable):
    calculated_total = tables.Column(verbose_name=_("Last Year's Place"), accessor='calculated_total')
    primary_number = tables.Column(verbose_name=_('Number'), default='-', accessor='primary_number')
    registration_dt = tables.Column(verbose_name=_('Registration Date'), default='-', accessor='registration_dt', visible=False)

    def render_calculated_total(self, value):
        return int(value)

    class Meta(ParticipantTable.Meta):
        sequence = (
        "calculated_total", "primary_number", 'first_name', 'last_name', 'year', 'group', 'team', 'bike_brand2',)
        order_by = ("calculated_total", "primary_number", "registration_dt")


class CompanyParticipantTable(tables.Table):
    selection = CustomSelectionCheckBoxColumn(orderable=False)
    class Meta:
        model = CompanyParticipant
        attrs = {"class": "table-block"}
        fields = (
        "first_name", "last_name", "birthday", "distance", "phone_number", 'email', 'created', 'is_participating')
        sequence = ('selection', "first_name", 'last_name', 'birthday', "distance", 'phone_number', 'email', 'created',
                    'is_participating')
        empty_text = _("There are no participants")
        order_by = ("created")
        per_page = 500
        template = "base/table.html"


class CompanyApplicationTable(tables.Table):
    id = tables.LinkColumn('companyapplication', args=[A('code')])
    team_name = tables.LinkColumn('companyapplication', args=[A('code')])

    def render_competition(self, value):
        return value.get_full_name

    class Meta:
        model = Application
        attrs = {"class": "table-block"}
        fields = ("id", "team_name", "competition", "created",)
        empty_text = _("You haven't created any company application.")
        order_by = ("-created")
        per_page = 20
        template = "base/table.html"
