from django.conf.urls import url
from velo.marketing.views import SMSReportView, TestEmailTemplate, CreateSendyView

urlpatterns = [
    url(r'^sms/back/$', SMSReportView.as_view(), name='sms_back'),
    url(r'^email/test/$', TestEmailTemplate.as_view(), name='email_test'),
    url(r'^sendy/create/$', CreateSendyView.as_view(), name='sendy_create'),
]
