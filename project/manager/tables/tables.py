# coding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import resolve, reverse
from django.utils.safestring import mark_safe
import django_tables2 as tables

from django_tables2.columns import LinkColumn, Column
from django.utils.translation import ugettext_lazy as _, ugettext
from core.models import Competition
from results.models import DistanceAdmin, Result
from team.models import MemberApplication, Team
from velo.mixins.table import GetRequestTableKwargs
from velo.tables import CustomCheckBoxColumn
from registration.models import Participant, Number, Application
from django_tables2.utils import A
from django_tables2_reports.tables import TableReport


class ManageTeamTable(GetRequestTableKwargs, tables.Table):
    # status = LinkColumn('manager:applied_team', args=[A('competition_id'), A('pk')])
    apply = tables.Column(verbose_name=" ", empty_values=())

    def render_apply(self, record, **kwargs):
        if record.distance.competition.params.get('teams_should_apply', False):
            return mark_safe("<a href='%s'>%s</a>" % (reverse('manager:team_apply_list', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id}), 'Pieteikt'))
        else:
            return ''

    # def render_title(self, record, **kwargs):
    #     url = reverse('manager:team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
    #     return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        empty_text = _("You haven't added any team")
        order_by = ("distance", "-is_featured", "title")
        fields = ("distance", 'title', 'status', 'contact_person', 'phone_number', 'is_featured', )
        per_page = 300
        template = "bootstrap/table.html"


class ManageTeamApplyTable(GetRequestTableKwargs, tables.Table):
    # status = LinkColumn('manager:applied_team', args=[A('competition_id'), A('pk')])

    def render_title(self, record, **kwargs):
        url = reverse('manager:applied_team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        empty_text = _("You haven't added any team")
        order_by = ("distance", "-is_featured", "title")
        fields = ("distance", 'title', 'status', 'contact_person', 'phone_number', 'is_featured', )
        per_page = 300
        template = "bootstrap/table.html"

class ManageDistanceAdminTable(GetRequestTableKwargs, tables.Table):
    distance = LinkColumn('manager:distance_admin', args=[A('competition_id'), A('pk')])
    def render_zero(self, record):
        return record.zero


    class Meta:
        model = DistanceAdmin
        attrs = {"class": "table table-striped table-hover"}
        fields = ("distance", 'zero', 'distance_actual', )
        empty_text = _("You haven't added any distance")
        order_by = ("distance")
        per_page = 100
        template = "bootstrap/table.html"


class ManageParticipantToNumberTable(GetRequestTableKwargs, tables.Table):
    last_name = tables.Column(empty_values=(), verbose_name='Last Name', orderable=False)
    first_name = tables.Column(empty_values=(), verbose_name='First Name', orderable=False)
    participant_slug = tables.Column(empty_values=(), verbose_name='Number Slug', orderable=False)

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.get('participant__id')})
        return mark_safe('<a href="%s">%s</a>' % (url, record.get('participant__last_name')))

    def render_first_name(self, record, **kwargs):
        return record.get('participant__first_name')

    def render_participant_slug(self, record, **kwargs):
        url = reverse('manager:number', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.get('id')})
        return mark_safe('<a href="%s">%s</a>' % (url, record.get('participant_slug')))

    class Meta:
        model = Number
        attrs = {"class": "table table-striped table-hover"}
        fields = ('participant_slug', 'number', 'group')
        sequence = ('number', 'participant_slug', "group", "first_name", 'last_name',)
        empty_text = _("No numbers")
        per_page = 100
        template = "bootstrap/table.html"



class ManageParticipantDifferSlugTable(GetRequestTableKwargs, tables.Table):
    selection = CustomCheckBoxColumn(accessor="pk", orderable=False)
    # last_name = LinkColumn('manager:participant', args=[A('competition_id'), A('pk')])
    participant_number = tables.Column(empty_values=(), verbose_name='Number', orderable=False)
    participant_number_slug = tables.Column(empty_values=(), verbose_name='Number', orderable=False)

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.last_name))

    def render_participant_number(self, record, **kwargs):
        url = reverse('manager:number', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.primary_number_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.primary_number))

    def render_participant_number_slug(self, record, **kwargs):
        url = reverse('manager:number', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.primary_number_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.primary_number.participant_slug))


    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ( 'distance', 'is_participating', 'first_name', 'last_name', 'birthday',)
        sequence = ("selection", 'distance', "first_name", 'last_name', 'birthday', 'is_participating', 'participant_number', 'participant_number_slug')
        empty_text = _("You haven't added any participant")
        order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"




class ManageParticipantTable(GetRequestTableKwargs, tables.Table):
    selection = CustomCheckBoxColumn(accessor="pk", orderable=False)
    # last_name = LinkColumn('manager:participant', args=[A('competition_id'), A('pk')])
    pdf = tables.Column(empty_values=(), verbose_name='PDF', orderable=False)

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.last_name))

    def render_pdf(self, record, **kwargs):
        url = reverse('manager:participant_pdf', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.id})
        return mark_safe('<a href="%s">PDF</a>' % url)


    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ("registration_dt", 'distance', 'is_participating', 'first_name', 'last_name', 'birthday', 'group', 'team_name', 'price')
        sequence = ("selection", 'distance', "first_name", 'last_name', 'birthday', 'is_participating', 'price', 'group', 'team_name', 'registration_dt', 'pdf')
        empty_text = _("You haven't added any participant")
        order_by = ("-registration_dt")
        per_page = 100
        template = "bootstrap/table.html"


class ManageNumberTable(tables.Table):
    request = None
    number = LinkColumn('manager:number', args=[A('competition_id'), A('pk')])

    def render_number(self, record, **kwargs):
        url = reverse('manager:number', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.number))

    def render_participant_slug(self, record, **kwargs):
        if record.participant_id:
            url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.participant_id})
            return mark_safe('<a href="%s">%s</a>' % (url, record.participant_slug))
        elif record.participant_slug:
            return record.participant_slug
        else:
            return '-'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.request_kwargs = kwargs.pop('request_kwargs')
        super(ManageNumberTable, self).__init__(*args, **kwargs)

    class Meta:
        model = Number
        attrs = {"class": "table table-striped table-hover"}
        fields = ("distance", "status", 'number', 'number_text', 'participant_slug', 'group')
        empty_text = _("You haven't added any number")
        per_page = 100
        template = "bootstrap/table.html"



class ManageCompetitionTable(tables.Table):
    name = tables.TemplateColumn(template_name='manager/competition_list_name.html')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.request_kwargs = kwargs.pop('request_kwargs')
        super(ManageCompetitionTable, self).__init__(*args, **kwargs)


    class Meta:
        model = Competition
        attrs = {"class": "table table-striped table-hover"}
        fields = ("name", 'place_name', 'competition_date', 'kind', 'bill_series', 'payment_channel')
        empty_text = _("You haven't added any competition")
        # order_by = ("-created")
        per_page = 100

class ManageMemberApplicationTable(TableReport):
    participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant.id')], accessor="participant.full_name", verbose_name='Participant')
    unpaid_participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant_unpaid.id')], accessor="participant_unpaid.full_name", verbose_name='Unpaid Participant')
    potential_participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant_potential.id')], accessor="participant_potential.full_name", verbose_name=' Potential Participant')

    class Meta:
        model = MemberApplication
        attrs = {"class": "table table-striped table-hover"}
        fields = ("member.team", "member", "kind",)
        empty_text = _("You haven't added any applied member")
        order_by = ("member.team", "kind")
        per_page = 100
        template = "bootstrap/table.html"


class ManageResultTable(tables.Table):
    id = LinkColumn('manager:result', args=[A('competition_id'), A('id')], accessor="id", verbose_name=_('ID'), )
    distance = tables.Column(verbose_name=_('Distance'), accessor='participant.distance')
    first_name = tables.Column(verbose_name=_('First Name'), accessor='participant.first_name')
    last_name = tables.Column(verbose_name=_('Last Name'), accessor='participant.last_name')
    group = tables.Column(verbose_name=_('Group'), accessor='participant.group')
    time = tables.Column(verbose_name=_('Time'), accessor='time')

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.participant_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.participant.last_name))

    class Meta:
        model = Result
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", "number", "avg_speed", "points_group", "points_distance", "status")
        sequence = ('id', 'competition', 'distance', 'number', 'first_name', 'last_name', 'time', 'avg_speed', 'group', 'points_group', 'points_distance', 'status')
        empty_text = _("There are no results")
        # order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.request_kwargs = kwargs.pop('request_kwargs')
        super(ManageResultTable, self).__init__(*args, **kwargs)


class ManageApplicationTable(GetRequestTableKwargs, tables.Table):

    def render_payment_status(self, record, **kwargs):
        url = reverse('manager:application', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.get_payment_status_display()))

    class Meta:
        model = Application
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", "payment_status", "discount_code", "email", "external_invoice_nr",)
        empty_text = _("There are no applications")
        # order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"
