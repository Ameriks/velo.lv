# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import DetailView
from slugify import slugify

from velo.manager.forms import PriceForm, InvoiceListSearchForm
from velo.manager.tables import ManagePriceTable
from velo.manager.tables.tables import ManageInvoiceTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.payment.models import Price, Invoice
from velo.registration.models import Application
from velo.team.models import Team
from velo.velo.mixins.views import SingleTableViewWithRequest, CreateViewWithCompetition, \
    UpdateViewWithCompetition, SetCompetitionContextMixin

__all__ = [
    'ManagePriceList', 'ManagePriceCreate', 'ManagePriceUpdate', 'ManageInvoiceList', 'ManageInvoice'
]

class ManagePriceList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Price
    table_class = ManagePriceTable
    template_name = 'bootstrap/manager/table.html'

    @property
    def add_link(self):
        return reverse_lazy('manager:price', kwargs={'pk': self.competition.id})


    def get_queryset(self):
        queryset = super(ManagePriceList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        return queryset


class ManagePriceCreate(ManagerPermissionMixin, CreateViewWithCompetition):
    pk_url_kwarg = 'pk2'
    model = Price
    template_name = 'bootstrap/manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})


class ManagePriceUpdate(ManagerPermissionMixin, UpdateViewWithCompetition):
    pk_url_kwarg = 'pk2'
    model = Price
    template_name = 'bootstrap/manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})


class ManageInvoiceList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Invoice
    table_class = ManageInvoiceTable
    template_name = 'bootstrap/manager/table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'search_form': InvoiceListSearchForm(request=self.request, competition=self.competition)})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        query_attrs = self.request.GET

        if query_attrs.get('status'):
            queryset = queryset.filter(status=query_attrs.get('status'))


        if query_attrs.get('search'):
            slug = slugify(query_attrs.get('search'))
            queryset = queryset.filter(
                Q(series__icontains=slug) |
                Q(file__icontains=query_attrs.get('search'))
            )

        return queryset.select_related('competition')


class ManageInvoice(ManagerPermissionMixin, SetCompetitionContextMixin, DetailView):
    model = Invoice
    pk_url_kwarg = 'pk2'
    template_name = 'bootstrap/manager/invoice.html'

    invoice_from = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'basket': self.invoice_data()})
        return context

    def invoice_data(self):
        print(self.kwargs.get('pk2'))
        try:
            application = Application.objects.all().filter(competition_id=self.kwargs.get('pk'), invoice__pk=self.kwargs.get('pk2'))[0]
            invoice_data = application.participant_set.all()
            self.invoice_from = "Application"
        except:
            try:
                team = Team.objects.all().filter(competition_id=self.kwargs.get('pk'), invoice__pk=self.kwargs.get('pk2'))[0]
                invoice_data = team.participant_set.all()
                self.invoice_from = "Team"
            except:
                return None

        return invoice_data


    @method_decorator(xframe_options_exempt)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def process_post(self, request):
        action = request.POST.get('action', '')
        if action == 'mark_as_payed':
            self.object.status = Invoice.PAY_STATUS.payed
            object = None
            self.invoice_data()
            if self.invoice_from == "Team":
                object = Team.objects.all().filter(competition_id=self.kwargs.get('pk'), invoice__pk=self.kwargs.get('pk2'))[0]
            elif self.invoice_from == "Application":
                object = Application.objects.all().filter(competition_id=self.kwargs.get('pk'), invoice__pk=self.kwargs.get('pk2'))[0]
            if object:
                for participant in object.participant_set.all():
                    participant.is_participating = True
                    participant.save()
                object.save()
                self.object.save()

    @method_decorator(xframe_options_exempt)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.process_post(request)
        return super().get(request, *args, **kwargs)
