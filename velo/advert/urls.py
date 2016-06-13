# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url

from .views import BannerView, BannerRedirectView


urlpatterns = [
                       url(r'^f/(?P<pk>\d+)/$', BannerView.as_view(), name='banner'),
                       url(r'^f/(?P<pk>\d+)/r/$', BannerRedirectView.as_view(), name='banner_redirect'),
]
