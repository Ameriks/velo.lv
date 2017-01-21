from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from velo.velo.mixins.views import NeverCacheMixin


class ManagerBaseMixin(NeverCacheMixin):
    add_link = None
    filter_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.add_link:
            context.update({'add_link': self.add_link})

        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.filter_class:
            queryset = self.filter_class(self.request.GET, queryset=queryset)

        return queryset


class ManagerPermissionMixin(ManagerBaseMixin, PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = "registration.add_number"


