from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import ListView
from supporter.models import Supporter, CompetitionSupporter
from velo.mixins.views import SetCompetitionContextMixin


class AgencySupporters(ListView):
    model = Supporter

    def get_queryset(self):
        queryset = super(AgencySupporters, self).get_queryset()
        queryset = queryset.filter(is_agency_supporter=True)
        return queryset


class CompetitionSupporters(SetCompetitionContextMixin, ListView):
    model = CompetitionSupporter
    template_name = 'supporter/competition_supporter_list.html'

    def get_queryset(self):
        queryset = super(CompetitionSupporters, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        queryset = queryset.order_by('-support_level', 'ordering', '-label').select_related('supporter')

        return queryset


class CompetitionIframeSupporters(SetCompetitionContextMixin, ListView):
    model = CompetitionSupporter
    template_name = 'supporter/supporter_slide_iframe.html'

    @method_decorator(xframe_options_exempt)
    def get(self, *args, **kwargs):
       return super(CompetitionIframeSupporters, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(CompetitionIframeSupporters, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        level = self.kwargs.get('level', None)
        if level:
            queryset = queryset.filter(support_level__lte=level)

        queryset = queryset.order_by('-support_level', 'ordering', '-label').select_related('supporter')

        return queryset
