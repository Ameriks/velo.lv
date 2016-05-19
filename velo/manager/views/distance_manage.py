# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.core.urlresolvers import reverse
from django.views.generic import UpdateView

from velo.manager.forms import DistanceAdminForm
from velo.manager.tables import ManageDistanceAdminTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.results.models import DistanceAdmin
from velo.velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin

__all__ = [
    'ManageDistanceAdminList', 'ManageDistanceAdminUpdate',
]

class ManageDistanceAdminList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = DistanceAdmin
    table_class = ManageDistanceAdminTable
    template_name = 'bootstrap/manager/table.html'

    def get_queryset(self):
        queryset = super(ManageDistanceAdminList, self).get_queryset()
        queryset = queryset.filter(competition=self.competition)
        queryset = queryset.select_related('distance', )
        return queryset


class ManageDistanceAdminUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, UpdateView):
    pk_url_kwarg = 'pk2'
    model = DistanceAdmin
    template_name = 'bootstrap/manager/participant_form.html'
    form_class = DistanceAdminForm

    def get_success_url(self):
        return reverse('manager:distance_admin_list', kwargs={'pk': self.kwargs.get('pk')})

