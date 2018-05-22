from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from velo.core.views import CompetitionDetail, MapView, MapGPXDownloadView
from velo.staticpage.views import StaticPageView
from velo.registration.views import ParticipantList, TeamJsonList, ParticipantSearchView, DataForExternalTotal, \
    DataForExternalAll, BikeBrandJsonList
from velo.results.views import ResultList, SebStandingResultList, SebTeamResultList, SebTeamResultStandingList, \
    TeamResultsByTeamName, ResultDiplomaPDF, TeamResultsByTeamNameBetweenDistances, TeamResultsByPointsBetweenDistances
from velo.team.views import TeamAppliedView, TeamListView, TeamView, TeamMemberProfileView

urlpatterns = [
                       url(r'^(?P<pk>\d+)/$', CompetitionDetail.as_view(), name='competition'),
                       url(_(r'^(?P<pk>\d+)/total.json$'), DataForExternalTotal.as_view(), name='external_total_json'),
                       url(_(r'^(?P<pk>\d+)/all.json$'), DataForExternalAll.as_view(), name='external_all_json'),

                       url(_(r'^(?P<pk>\d+)/maps/$'), MapView.as_view(), name='maps'),
                       url(_(r'^maps/gpx/(?P<pk2>\d+)/$'), MapGPXDownloadView.as_view(), name='map_gpx'),

                       url(_(r'^(?P<pk>\d+)/team/$'), TeamListView.as_view(), name='team'),
                       url(_(r'^(?P<pk>\d+)/team/(?P<pk2>\d+)/$'), TeamView.as_view(), name='team'),
                       url(_(r'^(?P<pk>\d+)/team/(?P<pk2>\d+)/(?P<pk3>\d+)/$'), TeamMemberProfileView.as_view(), name='team_member'),

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
                       url(_(r'^(?P<pk>\d+)/results/team_name/between_distances/$'), TeamResultsByTeamNameBetweenDistances.as_view(),
                           name='result_team_by_name_btw_distances'),
                       url(_(r'^(?P<pk>\d+)/results/team_name/between_distances2/$'), TeamResultsByPointsBetweenDistances.as_view(),
                           name='result_team_by_name_btw_distances2'),



                       url(_(r'^(?P<pk>\d+)/teams.json$'), TeamJsonList.as_view(), name='teams_json'),
                       url(_(r'^bike_brands.json$'), BikeBrandJsonList.as_view(), name='bikebrand_json'),




                       url(_(r'^participant/search.json$'), ParticipantSearchView.as_view(), name='participant_search'),


                       url(_(r'^(?P<pk>\d+)/(?P<slug>.*)/$'), StaticPageView.as_view(), name='staticpage'),


]
