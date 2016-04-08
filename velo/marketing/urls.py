# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import patterns, url

from velo.marketing.views import SMSReportView, TestEmailTemplate


urlpatterns = patterns('',
                       url(r'^sms/back/$', SMSReportView.as_view(), name='sms_back'),
                       url(r'^mailgun/webhook/$', 'velo.marketing.views.mailgun_webhook', name='mailgun_webhook'),
                       url(r'^email/test/$', TestEmailTemplate.as_view(), name='email_test'),

)
