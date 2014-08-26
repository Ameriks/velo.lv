# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from advert.views import FlashBannerView, FlashBannerRedirectView


urlpatterns = patterns('',
                       url(r'^f/(?P<pk>\d+)/$', FlashBannerView.as_view(), name='flash'),
                       url(r'^f/(?P<pk>\d+)/r/$', FlashBannerRedirectView.as_view(), name='flash_redirect'),
)