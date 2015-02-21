from django.conf.urls import patterns, url
from manager.views import ManageParticipantList, ManageCompetitionList, ManageCompetitionDetail, ManageParticipantUpdate, \
    ManageAppliedTeamMembersList, ManageParticipantCreate, ManageNumberList, ManageNumberUpdate, ManageDistanceAdminList, \
    ManageDistanceAdminUpdate, ManageTeamList, ManageTeamAppliedUpdate, MultipleSameSlugView, MultipleNumbersView, \
    ResultAssignedToInactiveParticipant, ManageParticipantPDF, ManageResultCreate, DifferNumberSlugView, \
    MatchParticipantToNumberView, FindNumberView, ManageResultReports, ManageApplicationExternalPay, \
    ManageParticipantIneseCreate, ManageApplicationList, ManageApplication, ManageTeams, ManageTeamApplyList, \
    ManageUrlSyncList, ManageUrlSyncUpdate, PayedAmountNotEqualView, ManagePriceList, ManagePriceCreate, ManagePriceUpdate
from manager.views.results_manage import ManageResultList, ManageResultUpdate
from team.views import TeamApply

urlpatterns = patterns('',
                       url(r'^competition/$', ManageCompetitionList.as_view(), name='competition_list'),
                       url(r'^competition/(?P<pk>\d+)/$', ManageCompetitionDetail.as_view(), name='competition'),



                       url(r'^competition/(?P<pk>\d+)/team/$', ManageTeams.as_view(), name='team_list'),

                       url(r'^competition/(?P<pk>\d+)/team/(?P<pk2>\d+)/apply/$', ManageTeamApplyList.as_view(), name='team_apply_list'),
                       url(r'^competition/(?P<pk>\d+)/team/(?P<pk2>\d+)/apply/(?P<competition_pk>\d+)/$', TeamApply.as_view(), name='team_apply_list'),


                       url(r'^competition/(?P<pk>\d+)/team/applied/$', ManageTeamList.as_view(), name='applied_team_list'),
                       url(r'^competition/(?P<pk>\d+)/team/applied/(?P<pk2>\d+)/$', ManageTeamAppliedUpdate.as_view(), name='applied_team'),

                       url(r'^competition/(?P<pk>\d+)/team/participant/applied/$', ManageAppliedTeamMembersList.as_view(), name='team_applied_participant_list'),
                       url(r'^competition/(?P<pk>\d+)/participant/$', ManageParticipantList.as_view(), name='participant_list'),
                       url(r'^competition/(?P<pk>\d+)/number/$', ManageNumberList.as_view(), name='number_list'),
                       url(r'^competition/(?P<pk>\d+)/number/(?P<pk_number>\d+)/$', ManageNumberUpdate.as_view(), name='number'),

                       url(r'^competition/(?P<pk>\d+)/distance_admin/$', ManageDistanceAdminList.as_view(), name='distance_admin_list'),
                       url(r'^competition/(?P<pk>\d+)/distance_admin/(?P<pk2>\d+)/$', ManageDistanceAdminUpdate.as_view(), name='distance_admin'),


                       url(r'^competition/(?P<pk>\d+)/result/$', ManageResultList.as_view(), name='result_list'),
                       url(r'^competition/(?P<pk>\d+)/result/(?P<pk2>\d+)/$', ManageResultUpdate.as_view(), name='result'),
                       url(r'^competition/(?P<pk>\d+)/result/add/$', ManageResultCreate.as_view(), name='result'),

                       url(r'^competition/(?P<pk>\d+)/result/reports/$', ManageResultReports.as_view(), name='result_reports'),
                       url(r'^competition/(?P<pk>\d+)/application/$', ManageApplicationList.as_view(), name='application_list'),
                       url(r'^competition/(?P<pk>\d+)/application/(?P<pk2>\d+)/$', ManageApplication.as_view(), name='application'),

                       url(r'^competition/(?P<pk>\d+)/urlsync/$', ManageUrlSyncList.as_view(), name='urlsync'),
                       url(r'^competition/(?P<pk>\d+)/urlsync/(?P<pk2>\d+)/$', ManageUrlSyncUpdate.as_view(), name='urlsync'),

                        url(r'^competition/(?P<pk>\d+)/price/$', ManagePriceList.as_view(), name='price_list'),
                        url(r'^competition/(?P<pk>\d+)/price/add/$', ManagePriceCreate.as_view(), name='price'),
                        url(r'^competition/(?P<pk>\d+)/price/(?P<pk2>\d+)/$', ManagePriceUpdate.as_view(), name='price'),

                       # This is legacy. To be deleted in next version.
                       url(r'^competition/(?P<pk>\d+)/application/(?P<pk2>\d+)/pay/$', ManageApplicationExternalPay.as_view(), name='application_pay'),



                       url(r'^competition/(?P<pk>\d+)/participant/(?P<pk_participant>\d+)/$', ManageParticipantUpdate.as_view(), name='participant'),
                       url(r'^competition/(?P<pk>\d+)/participant/(?P<pk_participant>\d+)/pdf/$', ManageParticipantPDF.as_view(), name='participant_pdf'),
                       url(r'^competition/(?P<pk>\d+)/participant/add/$', ManageParticipantCreate.as_view(), name='participant_create'),
                       url(r'^competition/(?P<pk>\d+)/participant/addi/$', ManageParticipantIneseCreate.as_view(), name='participant_createi'),



                       url(r'^competition/(?P<pk>\d+)/analytics/same_slug/$', MultipleSameSlugView.as_view(), name='analytics_same_slug'),
                       url(r'^competition/(?P<pk>\d+)/analytics/different_slugs/$', DifferNumberSlugView.as_view(), name='analytics_different_slugs'),
                       url(r'^competition/(?P<pk>\d+)/analytics/match_participant_number/$', MatchParticipantToNumberView.as_view(), name='analytics_participant_to_number'),



                       url(r'^competition/(?P<pk>\d+)/analytics/multiple_numbers/$', MultipleNumbersView.as_view(), name='analytics_multiple_numbers'),
                       url(r'^competition/(?P<pk>\d+)/analytics/results/incorrectly/assigned/$', ResultAssignedToInactiveParticipant.as_view(), name='analytics_results_incorrect'),

                       url(r'^competition/(?P<pk>\d+)/analytics/unmatched/$', FindNumberView.as_view(), name='analytics_find_unmatched_participant'),
                       url(r'^competition/(?P<pk>\d+)/analytics/payment_mismatch/$', PayedAmountNotEqualView.as_view(), name='analytics_find_payment_mismatch'),



)
