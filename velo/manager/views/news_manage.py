from django.core.urlresolvers import reverse, reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from velo.manager.forms import NewsForm
from velo.manager.tables import ManageNewsTable
from velo.news.models import News
from velo.velo.mixins.views import SingleTableViewWithRequest, CreateViewWithCompetition, UpdateViewWithCompetition

__all__ = ['ManageNewsList', 'ManageNewsUpdate', 'ManageNewsCreate']


class ManageNewsList(PermissionRequiredMixin, LoginRequiredMixin, SingleTableViewWithRequest):
    permission_required = "news.add_news"
    model = News
    table_class = ManageNewsTable
    template_name = 'bootstrap/manager/table.html'

    @property
    def add_link(self):
        return reverse_lazy('manager:news')


class ManageNewsUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateViewWithCompetition):
    permission_required = "news.change_news"
    pk_url_kwarg = 'pk2'
    model = News
    template_name = 'bootstrap/manager/news.html'
    form_class = NewsForm

    def get_success_url(self):
        return reverse('manager:news_list')


class ManageNewsCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateViewWithCompetition):
    permission_required = "news.add_news"
    pk_url_kwarg = 'pk2'
    model = News
    template_name = 'bootstrap/manager/news.html'
    form_class = NewsForm

    def get_success_url(self):
        return reverse('manager:news_list')
