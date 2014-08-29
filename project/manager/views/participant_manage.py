# coding=utf-8
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView, UpdateView, CreateView, DetailView
from manager.forms import ParticipantListSearchForm, ParticipantForm, ParticipantCreateForm, ParticipantIneseCreateForm, \
    ApplicationListSearchForm, InvoiceCreateForm
from manager.tables import ManageParticipantTable, ManageApplicationTable
from manager.views.permission_view import ManagerPermissionMixin
from payment.models import Payment
from registration.models import Participant, Application
from velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin, \
    CreateViewWithCompetition, UpdateViewWithCompetition
from velo.utils import load_class


__all__ = [
    'ManageParticipantList', 'ManageParticipantUpdate', 'ManageParticipantCreate', 'ManageParticipantIneseCreate', 'ManageParticipantPDF',
    'ManageApplicationList', 'ManageApplication',
]


class ManageApplication(ManagerPermissionMixin, SetCompetitionContextMixin, DetailView):
    model = Application
    pk_url_kwarg = 'pk2'
    template_name = 'manager/application.html'

    invoice_form = None

    def get_context_data(self, **kwargs):
        context = super(ManageApplication, self).get_context_data(**kwargs)
        context.update({'invoice_form': self.invoice_form})
        context.update({'payments': self.object.payment_set.all()})
        return context

    def create_invoice_form(self):

        kwargs = {'instance': self.get_object()}
        if self.request.method == 'POST':
            kwargs.update({'data': self.request.POST})

        self.invoice_form = InvoiceCreateForm(**kwargs)

    @method_decorator(xframe_options_exempt)
    def get(self, request, *args, **kwargs):
        self.create_invoice_form()
        return super(ManageApplication, self).get(request, *args, **kwargs)

    def process_post(self, request):
        action = request.POST.get('action', '')
        if action == 'mark_as_payed':
            self.object.payment_status = Application.PAY_STATUS_PAYED
            for participant in self.object.participant_set.all():
                participant.is_participating = True
                participant.save()
            self.object.save()
        elif action == 'create_invoice':
            self.create_invoice_form()
            if self.invoice_form.is_valid():
                self.invoice_form.save()

    @method_decorator(xframe_options_exempt)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.process_post(request)
        return super(ManageApplication, self).get(request, *args, **kwargs)



class ManageApplicationList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Application
    table_class = ManageApplicationTable
    template_name = 'manager/table.html'


    search_form = None
    def get_search_form(self):
        if not self.search_form:
            self.search_form = ApplicationListSearchForm(request=self.request, competition=self.competition)
        return self.search_form

    def get_context_data(self, **kwargs):
        context = super(ManageApplicationList, self).get_context_data(**kwargs)
        context.update({'search_form': self.get_search_form()})
        return context

    def get_queryset(self):
        queryset = super(ManageApplicationList, self).get_queryset()
        queryset = queryset.filter(competition_id=self.competition.id)

        query_attrs = self.get_search_form().fields

        if query_attrs.get('status').initial:
            queryset = queryset.filter(payment_status=query_attrs.get('status').initial)

        if query_attrs.get('search').initial:
            slug = slugify(query_attrs.get('search').initial)
            queryset = queryset.filter(
                Q(external_invoice_nr__icontains=slug) |
                Q(email__icontains=query_attrs.get('search').initial.upper()) |
                Q(participant__slug__icontains=slug) |
                Q(participant__team_name__icontains=query_attrs.get('search').initial.upper())
            )

        queryset = queryset.select_related('competition').distinct()
        return queryset



class ManageParticipantList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Participant
    table_class = ManageParticipantTable
    template_name = 'manager/table.html'

    search_form = None
    def get_search_form(self):
        if not self.search_form:
            self.search_form = ParticipantListSearchForm(request=self.request, competition=self.competition)
        return self.search_form

    def get_context_data(self, **kwargs):
        context = super(ManageParticipantList, self).get_context_data(**kwargs)
        context.update({'search_form': self.get_search_form()})
        return context

    def table_order_by(self):
        if self.request.GET.get('sort', None):
            self.request.session['manager__participant_list__order_by'] = self.request.GET.get('sort', None)
        return self.request.session.get('manager__participant_list__order_by', None)

    def get_queryset(self):
        queryset = super(ManageParticipantList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        query_attrs = self.get_search_form().fields

        if query_attrs.get('distance').initial:
            queryset = queryset.filter(distance_id=query_attrs.get('distance').initial)

        if query_attrs.get('group').initial:
            queryset = queryset.filter(group=query_attrs.get('group').initial)

        if query_attrs.get('status').initial:
            queryset = queryset.filter(is_participating=query_attrs.get('status').initial)

        if query_attrs.get('search').initial:
            slug = slugify(query_attrs.get('search').initial)
            queryset = queryset.filter(
                Q(slug__icontains=slug) |
                Q(ssn__icontains=query_attrs.get('search').initial) |
                Q(primary_number__number__icontains=query_attrs.get('search').initial) |
                Q(team_name__icontains=query_attrs.get('search').initial.upper())
            )

        queryset = queryset.select_related('distance', 'competition', 'price')
        return queryset


class ManageParticipantUpdate(ManagerPermissionMixin, UpdateViewWithCompetition):
    pk_url_kwarg = 'pk_participant'
    model = Participant
    template_name = 'manager/participant_form.html'
    form_class = ParticipantForm

    def get_success_url(self):
        if self.request.POST.get('submit_and_next', None):
            return reverse('manager:participant_create', kwargs={'pk': self.kwargs.get('pk')})
        else:
            return reverse('manager:participant_list', kwargs={'pk': self.kwargs.get('pk')})

class ManageParticipantCreate(ManagerPermissionMixin, CreateViewWithCompetition):
    pk_url_kwarg = 'pk_participant'
    model = Participant
    template_name = 'manager/participant_form.html'
    form_class = ParticipantCreateForm

    def get_success_url(self):
        if self.request.POST.get('submit_and_next', None):
            return reverse('manager:participant_create', kwargs={'pk': self.kwargs.get('pk')})
        elif self.request.POST.get('submit_and_continue', None):
            return reverse('manager:participant', kwargs={'pk': self.kwargs.get('pk'), 'pk_participant': self.object.id})
        else:
            return reverse('manager:participant_list', kwargs={'pk': self.kwargs.get('pk')})


class ManageParticipantIneseCreate(ManageParticipantCreate):
    form_class = ParticipantIneseCreateForm

    def get_context_data(self, **kwargs):
        context = super(ManageParticipantIneseCreate, self).get_context_data(**kwargs)
        js_vars = {
            'participant_search': "{0}?search=%QUERY".format(reverse('competition:participant_search')),
        }
        context.update({'js_vars': js_vars})
        return context

    def get_success_url(self):
        if self.request.POST.get('submit_and_next', None):
            return reverse('manager:participant_createi', kwargs={'pk': self.kwargs.get('pk')})
        elif self.request.POST.get('submit_and_continue', None):
            return reverse('manager:participant', kwargs={'pk': self.kwargs.get('pk'), 'pk_participant': self.object.id})
        else:
            return reverse('manager:participant_list', kwargs={'pk': self.kwargs.get('pk')})



class ManageParticipantPDF(ManagerPermissionMixin, DetailView):
    pk_url_kwarg = 'pk_participant'
    model = Participant

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        if self.object.competition.processing_class:
            _class = load_class(self.object.competition.processing_class)
        else:
            raise Http404
        processing_class = _class(self.object.competition_id)
        file_obj = processing_class.number_pdf(participant_id=self.object.id)
        response = HttpResponse(mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % self.object.slug
        response.write(file_obj.getvalue())
        file_obj.close()
        return response
