# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from manager.views import ManageTeamApplyList
from news.views import NotificationView, NewsListView, NewsDetailView
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('',
                       url(_(r'^notification/(?P<slug>.+)/$'), NotificationView.as_view(), name='notification'),

                       url(r'^$', NewsListView.as_view(), name='news_list'),
                       url(r'^(?P<pk>\d+)/$', NewsListView.as_view(), name='news_list'),
                       url(r'^(?P<pk>\d+)/(?P<slug>.+)/$', NewsDetailView.as_view(), name='news'),
                       url(r'^(?P<slug>.+)/$', NewsDetailView.as_view(), name='news'),
)