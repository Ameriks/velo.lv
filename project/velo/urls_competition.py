# coding=utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from core.views import CompetitionDetail, MapView, MapGPXDownloadView
from flatpages.views import FlatpageView
from registration.views import ParticipantList, TeamJsonList, ParticipantSearchView, DataForExternalTotal, \
    DataForExternalAll, BikeBrandJsonList
from django.utils.translation import ugettext_lazy as _
from results.views import ResultList, SebStandingResultList, SebTeamResultList, SebTeamResultStandingList, \
    TeamResultsByTeamName, ResultDiplomaPDF
from supporter.views import CompetitionSupporters, CompetitionIframeSupporters
from team.views import TeamAppliedView, TeamListView, TeamView

urlpatterns = patterns('',
                       url(r'^(?P<pk>\d+)/$', CompetitionDetail.as_view(), name='competition'),
                       url(_(r'^(?P<pk>\d+)/total.json$'), DataForExternalTotal.as_view(), name='external_total_json'),
                       url(_(r'^(?P<pk>\d+)/all.json$'), DataForExternalAll.as_view(), name='external_all_json'),

                       url(_(r'^(?P<pk>\d+)/maps/$'), MapView.as_view(), name='maps'),
                       url(_(r'^maps/gpx/(?P<pk2>\d+)/$'), MapGPXDownloadView.as_view(), name='map_gpx'),

                       url(_(r'^(?P<pk>\d+)/supporters/$'), CompetitionSupporters.as_view(), name='supporters'),

                       url(_(r'^(?P<pk>\d+)/team/$'), TeamListView.as_view(), name='team'),
                       url(_(r'^(?P<pk>\d+)/team/(?P<pk2>\d+)/$'), TeamView.as_view(), name='team'),

                       url(_(r'^(?P<pk>\d+)/supporters/iframe/$'), CompetitionIframeSupporters.as_view(),
                           name='supporters_embeded'),
                       url(_(r'^(?P<pk>\d+)/supporters/iframe/(?P<level>\d+)/$'), CompetitionIframeSupporters.as_view(),
                           name='supporters_embeded'),

                       url(_(r'^(?P<pk>\d+)/standings/$'), SebStandingResultList.as_view(), name='standings_list'),
                       url(_(r'^(?P<pk>\d+)/standings/teams/$'), SebTeamResultStandingList.as_view(),
                           name='team_standings_list'),
                       url(_(r'^(?P<pk>\d+)/participants/$'), ParticipantList.as_view(), name='participant_list'),
                       url(_(r'^(?P<pk>\d+)/applied_teams/$'), TeamAppliedView.as_view(), name='applied_teams_list'),
                       url(_(r'^(?P<pk>\d+)/results/$'), ResultList.as_view(), name='result_distance_list'),
                       url(_(r'^(?P<pk>\d+)/results/(?P<pk2>\d+)/$'), ResultDiplomaPDF.as_view(),
                           name='result_diploma'),

                       url(_(r'^(?P<pk>\d+)/results/teams/$'), SebTeamResultList.as_view(), name='result_team_list'),
                       url(_(r'^(?P<pk>\d+)/results/team_name/$'), TeamResultsByTeamName.as_view(),
                           name='result_team_by_name'),

                       url(_(r'^(?P<pk>\d+)/teams.json$'), TeamJsonList.as_view(), name='teams_json'),
                       url(_(r'^bike_brands.json$'), BikeBrandJsonList.as_view(), name='bikebrand_json'),




                       url(_(r'^participant/search.json$'), ParticipantSearchView.as_view(), name='participant_search'),


                       url(_(r'^(?P<pk>\d+)/(?P<slug>.*)/$'), FlatpageView.as_view(), name='flatpage'),


)