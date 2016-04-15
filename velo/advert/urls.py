# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url

from velo.advert.views import FlashBannerView, FlashBannerRedirectView


urlpatterns = [
                       url(r'^f/(?P<pk>\d+)/$', FlashBannerView.as_view(), name='flash'),
                       url(r'^f/(?P<pk>\d+)/r/$', FlashBannerRedirectView.as_view(), name='flash_redirect'),
]
