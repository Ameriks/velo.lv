from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.utils.text import slugify
from django.views.generic import UpdateView, TemplateView

from extra_views import NamedFormsetsMixin, UpdateWithInlinesView, InlineFormSet, CreateWithInlinesView

from velo.core.formsets import CustomBaseInlineFormSet
from velo.manager.filter import ChipScanFilter
from velo.manager.forms import ResultListSearchForm, ResultForm, ManageLapResultForm, UrlSyncForm
from velo.manager.tables import ManageResultTable, ManageChipScanTable
from velo.manager.tables.tables import UrlSyncTable
from velo.manager.views.participant_manage import ManagerPermissionMixin
from velo.results.models import Result, LapResult, UrlSync, ChipScan
from velo.velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin, RequestFormKwargsMixin
from velo.manager.tasks import generate_pdfreport, result_process

__all__ = ['ManageResultList', 'ManageResultUpdate', 'ManageResultCreate', 'ManageResultReports', 'ManageUrlSyncList', 'ManageUrlSyncUpdate', 'ManageChipScanList']


class ManageResultList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Result
    table_class = ManageResultTable
    template_name = 'bootstrap/manager/table.html'

    def get_context_data(self, **kwargs):
        context = super(ManageResultList, self).get_context_data(**kwargs)
        context.update({'search_form': ResultListSearchForm(request=self.request, competition=self.competition)})
        return context

    def get_queryset(self):
        queryset = super(ManageResultList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        query_attrs = self.request.GET

        if query_attrs.get('distance'):
            queryset = queryset.filter(participant__distance_id=query_attrs.get('distance'))

        if query_attrs.get('group'):
            queryset = queryset.filter(participant__group=query_attrs.get('group'))

        if query_attrs.get('status'):
            queryset = queryset.filter(status=query_attrs.get('status'))

        if query_attrs.get('number'):
            try:
                number = int(query_attrs.get('number'))
                queryset = queryset.filter(participant__primary_number__number=number)
            except ValueError:
                messages.error(self.request, 'In number field you can enter only number')

        if query_attrs.get('search'):
            slug = slugify(query_attrs.get('search'))
            queryset = queryset.filter(
                Q(participant__slug__icontains=slug) |
                Q(participant__ssn__icontains=query_attrs.get('search'))
            )

        return queryset.select_related('competition', 'participant', 'number', 'participant__distance')


class ManageChipScanList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = ChipScan
    table_class = ManageChipScanTable
    template_name = 'bootstrap/manager/results/chipscan_table.html'
    filter_class = ChipScanFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset._qs = queryset.qs.filter(competition_id__in=self.competition.get_ids())

        return queryset

    def post(self, request, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))

        action = request.POST.get('action')

        if action in ('process_unprocessed', ):
            result_process.delay(kwargs.get('pk'), action, request.user.id)
            messages.info(request, 'Unprocessed chips are being processed')
        else:
            raise Http404

        return HttpResponseRedirect(reverse('manager:chipscan_list', kwargs={'pk': kwargs.get('pk')}))


class ManagLapResultInline(InlineFormSet):
    can_order = False
    model = LapResult
    form_class = ManageLapResultForm
    extra = 0
    formset_class = CustomBaseInlineFormSet

    def get_extra_form_kwargs(self):
        kwargs = super(ManagLapResultInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        return kwargs

    def get_formset_kwargs(self):
        kwargs = super(ManagLapResultInline, self).get_formset_kwargs()
        kwargs.update({'empty_form_class': self.form_class})
        return kwargs




class ManageResultUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    pk_url_kwarg = 'pk2'
    model = Result
    template_name = 'bootstrap/manager/form.html'
    form_class = ResultForm
    inlines = [ManagLapResultInline, ]
    inlines_names = ['lap']

    def get_success_url(self):
        return reverse('manager:result_list', kwargs={'pk': self.kwargs.get('pk')})


class ManageResultCreate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, NamedFormsetsMixin, CreateWithInlinesView):
    pk_url_kwarg = 'pk2'
    model = Result
    template_name = 'bootstrap/manager/form.html'
    form_class = ResultForm
    inlines = [ManagLapResultInline, ]
    inlines_names = ['lap']

    def get_success_url(self):
        messages.success(self.request, 'Result created. Update it if required.')
        return reverse('manager:result', kwargs={'pk': self.kwargs.get('pk'), 'pk2': self.object.id})


class ManageResultReports(ManagerPermissionMixin, SetCompetitionContextMixin, TemplateView):
    template_name = 'bootstrap/manager/result_reports.html'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action in ('results_groups', 'results_groups_top20', 'results_gender', 'results_distance',
                      'results_distance_top20', 'results_standings', 'results_standings_top20', 'results_standings_groups', 'results_standings_gender',
                      'results_standings_groups_top20', 'results_team', 'results_team_standings', 'results_progressive', 'results_most_active',
                      'RM_results_distance', 'RM_results_groups', 'RM_results_distance_top20', 'RM_results_groups_top20', 'RM_results_gender', 'RM_results_team'):
            generate_pdfreport.delay(kwargs.get('pk'), action, request.user.id)
            messages.info(request, 'Report is being generated. It will be emailed to %s' % request.user.email)
        else:
            raise Http404

        return HttpResponseRedirect(reverse('manager:result_reports', kwargs={'pk': kwargs.get('pk')}))


class ManageUrlSyncList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = UrlSync
    table_class = UrlSyncTable
    template_name = 'bootstrap/manager/table.html'


class ManageUrlSyncUpdate(ManagerPermissionMixin, SetCompetitionContextMixin, RequestFormKwargsMixin, UpdateView):
    pk_url_kwarg = 'pk2'
    model = UrlSync
    template_name = 'bootstrap/manager/participant_form.html'
    form_class = UrlSyncForm

    def get_success_url(self):
        return reverse('manager:urlsync', kwargs={'pk': self.kwargs.get('pk')})

