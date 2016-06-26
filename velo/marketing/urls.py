# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url

from velo.marketing.views import SMSReportView, TestEmailTemplate

urlpatterns = [
                       url(r'^sms/back/$', SMSReportView.as_view(), name='sms_back'),
                       url(r'^email/test/$', TestEmailTemplate.as_view(), name='email_test'),

]
