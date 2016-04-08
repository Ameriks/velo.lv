# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from velo.core.views import UserRedirectView
from velo.payment.views import TeamPayView
from velo.registration.views import MyApplicationList
from velo.team.views import MyTeamList, TeamCreateView, TeamUpdateView, TeamApplyList, TeamApply

urlpatterns = patterns('',
                       url(r'^~redirect/$', UserRedirectView.as_view(), name='redirect'),

                       url(_(r'^my_applications/$'), MyApplicationList.as_view(), name='applications'),
                       url(_(r'^my_team/$'), MyTeamList.as_view(), name='team_list'),
                       url(_(r'^my_team/add/$'), TeamCreateView.as_view(), name='team'),
                       url(_(r'^my_team/(?P<pk2>\d+)/$'), TeamUpdateView.as_view(), name='team'),

                       url(_(r'^my_team/(?P<pk2>\d+)/pay/$'), TeamPayView.as_view(), name='team_pay'),

                       url(_(r'^my_team/(?P<pk2>\d+)/apply/$'), TeamApplyList.as_view(), name='team_apply_list'),
                       url(_(r'^my_team/(?P<pk2>\d+)/apply/(?P<competition_pk>\d+)/$'), TeamApply.as_view(),
                           name='team_apply_list'),

)
