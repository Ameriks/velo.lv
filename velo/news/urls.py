# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from velo.news.views import NotificationView, NewsListView, NewsDetailView


urlpatterns = [
                       url(_(r'^notification/(?P<slug>.+)/$'), NotificationView.as_view(), name='notification'),

                       url(r'^$', NewsListView.as_view(), name='news_list'),
                       url(r'^(?P<pk>\d+)/$', NewsListView.as_view(), name='news_list'),
                       url(r'^(?P<pk>\d+)/(?P<slug>.+)/$', NewsDetailView.as_view(), name='news'),
                       url(r'^(?P<slug>.+)/$', NewsDetailView.as_view(), name='news'),
]
