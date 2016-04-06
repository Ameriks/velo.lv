# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse

from velo.manager.forms import PriceForm
from velo.manager.tables import ManagePriceTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.payment.models import Price
from velo.velo.mixins.views import SingleTableViewWithRequest, CreateViewWithCompetition, \
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

