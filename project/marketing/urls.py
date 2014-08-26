# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from marketing.views import SMSReportView, TestEmailTemplate


urlpatterns = patterns('',
                       url(r'^sms/back/$', SMSReportView.as_view(), name='sms_back'),
                       url(r'^mailgun/webhook/$', 'marketing.views.mailgun_webhook', name='mailgun_webhook'),
                       url(r'^email/test/$', TestEmailTemplate.as_view(), name='email_test'),

)