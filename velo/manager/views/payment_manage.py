# coding=utf-8
from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from manager.forms import PriceForm
from manager.tables import ManagePriceTable
from manager.views.permission_view import ManagerPermissionMixin
from payment.models import Payment, Price
from registration.models import Application
from velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, CreateViewWithCompetition, \
    UpdateViewWithCompetition


__all__ = [
    'ManagePriceList', 'ManagePriceCreate', 'ManagePriceUpdate',
]

class ManagePriceList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Price
    table_class = ManagePriceTable
    template_name = 'manager/table.html'

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
    template_name = 'manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})


class ManagePriceUpdate(ManagerPermissionMixin, UpdateViewWithCompetition):
    pk_url_kwarg = 'pk2'
    model = Price
    template_name = 'manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})

