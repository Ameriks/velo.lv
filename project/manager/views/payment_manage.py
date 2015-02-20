# coding=utf-8
from __future__ import unicode_literals
from manager.tables import ManagePaymentTable
from manager.views.permission_view import ManagerPermissionMixin
from registration.models import Application
from velo.mixins.views import SingleTableViewWithRequest


__all__ = [
    'ManagePaymentList',
]

class ManagePaymentList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Application
    table_class = ManagePaymentTable
    template_name = 'manager/table.html'

    def get_queryset(self):
        queryset = super(ManagePaymentList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        return queryset

