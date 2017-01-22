from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.columns import LinkColumn, Column
from django_tables2.utils import A

from velo.core.models import Competition
from velo.payment.models import Price, Invoice
from velo.results.models import DistanceAdmin, UrlSync
from velo.team.models import MemberApplication, Team
from velo.velo.mixins.table import GetRequestTableKwargs
from velo.velo.tables import CustomCheckBoxColumn
from velo.registration.models import Participant, Number, Application, PreNumberAssign, ChangedName


class ManageTeamTable(GetRequestTableKwargs, tables.Table):
    # status = LinkColumn('manager:edit_team', args=[A('competition_id'), A('pk')])
    apply = tables.Column(verbose_name=" ", empty_values=())

    def render_apply(self, record, **kwargs):
        if record.distance.competition.params_dict.get('teams_should_apply', False):
            return mark_safe("<a href='%s'>%s</a>" % (
            reverse('manager:team_apply_list', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id}),
            'Pieteikt'))
        else:
            return ''

    def render_title(self, record, **kwargs):
        url = reverse('manager:edit_team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        empty_text = _("You haven't added any team")
        order_by = ("distance", "-is_featured", "title")
        fields = ("distance", 'title', 'status', 'contact_person', 'phone_number', 'is_featured',)
        per_page = 300
        template = "bootstrap/table.html"


class ManageTeamApplyTable(GetRequestTableKwargs, tables.Table):
    # status = LinkColumn('manager:edit_team', args=[A('competition_id'), A('pk')])

    def render_title(self, record, **kwargs):
        url = reverse('manager:edit_team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    class Meta:
        model = Team
        attrs = {"class": "table table-striped table-hover"}
        empty_text = _("You haven't added any team")
        order_by = ("distance", "-is_featured", "title")
        fields = ("distance", 'title', 'status', 'contact_person', 'phone_number', 'is_featured',)
        per_page = 300
        template = "bootstrap/table.html"


class ManageDistanceAdminTable(GetRequestTableKwargs, tables.Table):
    distance = LinkColumn('manager:distance_admin', args=[A('competition_id'), A('pk')])

    def render_zero(self, record):
        return record.zero

    class Meta:
        model = DistanceAdmin
        attrs = {"class": "table table-striped table-hover"}
        fields = ("distance", 'zero', 'distance_actual',)
        empty_text = _("You haven't added any distance")
        order_by = ("distance")
        per_page = 100
        template = "bootstrap/table.html"


class ManageParticipantToNumberTable(GetRequestTableKwargs, tables.Table):
    last_name = tables.Column(empty_values=(), verbose_name='Last Name', orderable=False)
    first_name = tables.Column(empty_values=(), verbose_name='First Name', orderable=False)
    participant_slug = tables.Column(empty_values=(), verbose_name='Number Slug', orderable=False)

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant',
                      kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.get('participant__id')})
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
        url = reverse('manager:number',
                      kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.primary_number_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.primary_number))

    def render_participant_number_slug(self, record, **kwargs):
        url = reverse('manager:number',
                      kwargs={'pk': self.request_kwargs.get('pk'), 'pk_number': record.primary_number_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.primary_number.participant_slug))

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = ('distance', 'is_participating', 'first_name', 'last_name', 'birthday',)
        sequence = (
        "selection", 'distance', "first_name", 'last_name', 'birthday', 'is_participating', 'participant_number',
        'participant_number_slug')
        empty_text = _("You haven't added any participant")
        order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"


class ManageParticipantTable(GetRequestTableKwargs, tables.Table):
    selection = CustomCheckBoxColumn(accessor="pk", orderable=False)
    # last_name = LinkColumn('manager:participant', args=[A('competition_id'), A('pk')])
    pdf = tables.Column(empty_values=(), verbose_name='PDF', orderable=False)

    def render_distance(self, record, **kwargs):
        # Too long distance names for admin.
        return str(record.distance).split(' ', 1)[0]

    def render_last_name(self, record, **kwargs):
        url = reverse('manager:participant', kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.last_name))

    def render_pdf(self, record, **kwargs):
        url = reverse('participant_number_pdf', kwargs={'slug': record.code_short})
        return mark_safe('<a href="%s">PDF</a>' % url)

    class Meta:
        model = Participant
        attrs = {"class": "table table-striped table-hover"}
        fields = (
        "registration_dt", 'distance', 'is_participating', 'first_name', 'last_name', 'birthday', 'group', 'team_name',
        'price')
        sequence = (
        "selection", 'distance', "first_name", 'last_name', 'birthday', 'is_participating', 'price', 'group',
        'team_name', 'registration_dt', 'pdf')
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
            url = reverse('manager:participant',
                          kwargs={'pk': self.request_kwargs.get('pk'), 'pk_participant': record.participant_id})
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
    name = tables.TemplateColumn(template_name='bootstrap/manager/competition_list_name.html')

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


class ManageMemberApplicationTable(GetRequestTableKwargs, tables.Table):
    title = Column(verbose_name='Team Title', accessor='member.team')
    participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant.id')],
                             accessor="participant.full_name", verbose_name='Participant')
    unpaid_participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant_unpaid.id')],
                                    accessor="participant_unpaid.full_name", verbose_name='Unpaid Participant')
    potential_participant = LinkColumn('manager:participant', args=[A('competition_id'), A('participant_potential.id')],
                                       accessor="participant_potential.full_name",
                                       verbose_name=' Potential Participant')

    def render_title(self, record, **kwargs):
        url = reverse('manager:edit_team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.member.team_id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.member.team))

    class Meta:
        model = MemberApplication
        attrs = {"class": "table table-striped table-hover"}
        fields = ("member", "kind",)
        sequence = ('title', 'member', 'kind', 'participant', 'unpaid_participant', 'potential_participant')
        empty_text = _("You haven't added any applied member")
        order_by = ("title", "kind")
        per_page = 100
        template = "bootstrap/table.html"


class ManageApplicationTable(GetRequestTableKwargs, tables.Table):
    invoice_nr = tables.Column(accessor="invoice.invoice_nr", order_by=("invoice.series", "invoice.number"), )

    def render_payment_status(self, record, **kwargs):
        url = reverse('manager:application', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.get_payment_status_display()))

    class Meta:
        model = Application
        attrs = {"class": "table table-striped table-hover"}
        fields = ("competition", "payment_status", "discount_code", "email",)
        empty_text = _("There are no applications")
        # order_by = ("-created")
        per_page = 100
        template = "bootstrap/table.html"


class UrlSyncTable(GetRequestTableKwargs, tables.Table):
    id = LinkColumn('manager:urlsync', args=[A('competition_id'), A('id')], accessor="id", verbose_name=_('ID'), )

    class Meta:
        model = UrlSync
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "competition", "url", "kind", "index", "current_line", "enabled", "expires", "total_run_count")
        empty_text = _("There are no Sync tasks")
        per_page = 100
        template = "bootstrap/table.html"


class ManagePriceTable(GetRequestTableKwargs, tables.Table):
    id = LinkColumn('manager:price', args=[A('competition_id'), A('id')], accessor="id", verbose_name=_('ID'), )

    class Meta:
        model = Price
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "distance", "from_year", "till_year", "price", "start_registering", "end_registering")
        empty_text = _("There are no pricing records.")
        per_page = 100
        template = "bootstrap/table.html"


class PreNumberAssignTable(GetRequestTableKwargs, tables.Table):
    id = LinkColumn('manager:prenumber', args=[A('competition_id'), A('id')], accessor="id", verbose_name=_('ID'), )

    class Meta:
        model = PreNumberAssign
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "distance", "number", "segment", "participant_slug", "group_together")
        empty_text = _("There are no records.")
        per_page = 100
        template = "bootstrap/table.html"


class ChangedNameTable(GetRequestTableKwargs, tables.Table):
    id = LinkColumn('manager:changedname', args=[A('id')], accessor="id", verbose_name=_('ID'), )

    class Meta:
        model = ChangedName
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "slug", "new_slug",)
        empty_text = _("There are no records.")
        per_page = 100
        template = "bootstrap/table.html"


class ManageInvoiceTable(GetRequestTableKwargs, tables.Table):

    status = LinkColumn('manager:invoice', args=[A('competition_id'), A('id')], accessor="payment.status", verbose_name=_('Invoice status'), )

    class Meta:
        model = Invoice
        attrs = {"class": "table table-striped table-hover"}
        fields = ("id", "status", "file", "series", "number")
        empty_text = _("There are no invoice records.")
        per_page = 100
        template = "bootstrap/table.html"
