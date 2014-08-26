from django.core.urlresolvers import reverse
from django.views.generic import UpdateView
from manager.forms import DistanceAdminForm
from manager.tables import ManageDistanceAdminTable
from manager.views.permission_view import ManagerPermissionMixin
from results.models import DistanceAdmin
from velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin

__all__ = [
    'ManageDistanceAdminList', 'ManageDistanceAdminUpdate',
]

class ManageDistanceAdminList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = DistanceAdmin
    table_class = ManageDistanceAdminTable
    template_name = 'manager/table.html'

    def get_queryset(self):
        queryset = super(ManageDistanceAdminList, self).get_queryset()
        queryset = queryset.filter(competition=self.competition)
        queryset = queryset.select_related('distance', )
        return queryset


class ManageDistanceAdminUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, UpdateView):
    pk_url_kwarg = 'pk2'
    model = DistanceAdmin
    template_name = 'manager/participant_form.html'
    form_class = DistanceAdminForm

    def get_success_url(self):
        return reverse('manager:distance_admin_list', kwargs={'pk': self.kwargs.get('pk')})

