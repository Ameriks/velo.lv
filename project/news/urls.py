# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from news.views import NotificationView
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('',
                       url(_(r'^notification/(?P<slug>.+)/$'), NotificationView.as_view(), name='notification'),
)