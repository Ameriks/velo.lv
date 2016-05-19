# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import UpdateView

from velo.manager.forms import NumberForm, NumberListSearchForm
from velo.manager.tables import ManageNumberTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.registration.models import Number
from velo.velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin

__all__ = [
    'ManageNumberList', 'ManageNumberUpdate',
]


class ManageNumberList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Number
    table_class = ManageNumberTable
    template_name = 'bootstrap/manager/table.html'

    search_form = None

    def get_search_form(self):
        if not self.search_form:
            self.search_form = NumberListSearchForm(request=self.request, competition=self.competition)
        return self.search_form

    def get_context_data(self, **kwargs):
        context = super(ManageNumberList, self).get_context_data(**kwargs)
        context.update({'search_form': self.get_search_form()})
        return context

    def get_queryset(self):
        queryset = super(ManageNumberList, self).get_queryset()
        queryset = queryset.extra(
            select={
                'participant_id': 'SELECT rp.id FROM registration_participant rp WHERE registration_number.participant_slug = rp.slug and rp.is_participating is True and rp.distance_id = registration_number.distance_id and rp.competition_id in %s LIMIT 1',
            },
            select_params=(self.competition.get_ids(),),
        ).select_related('distance')

        query_attrs = self.get_search_form().fields

        if query_attrs.get('distance').initial:
            queryset = queryset.filter(distance_id=query_attrs.get('distance').initial)
        else:
            queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        if query_attrs.get('group').initial:
            queryset = queryset.filter(group=query_attrs.get('group').initial)

        if query_attrs.get('status').initial:
            queryset = queryset.filter(status=query_attrs.get('status').initial)

        if query_attrs.get('number').initial:
            try:
                number = int(query_attrs.get('number').initial)
                queryset = queryset.filter(number=number)
            except ValueError:
                messages.error(self.request, 'In number field you can enter only number')

        return queryset


class ManageNumberUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, UpdateView):
    pk_url_kwarg = 'pk_number'
    model = Number
    template_name = 'bootstrap/manager/participant_form.html'
    form_class = NumberForm

    def get_success_url(self):
        return reverse('manager:number_list', kwargs={'pk': self.kwargs.get('pk')})
