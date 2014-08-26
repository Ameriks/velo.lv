from braces.views import PermissionRequiredMixin, LoginRequiredMixin


class ManagerPermissionMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = "registration.add_number"
