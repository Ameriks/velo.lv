# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from payment.views import CheckPriceView, PaymentReturnView


urlpatterns = patterns('',
                       url(_(r'^checkprice/(?P<pk>\d+)/$'), CheckPriceView.as_view(), name='check_price'),
                       url(_(r'^back/(?P<slug>.+)/$'), PaymentReturnView.as_view(), name='back'),
)