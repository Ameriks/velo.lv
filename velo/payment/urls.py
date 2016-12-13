# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from velo.payment.views import CheckPriceView, PaymentReturnView, InvoiceDownloadView

urlpatterns = [
                       url(_(r'^checkprice/(?P<pk>\d+)/$'), CheckPriceView.as_view(), name='check_price'),
                       url(_(r'^back/(?P<slug>.+)/$'), PaymentReturnView.as_view(), name='back'),

                       url(_(r'^invoice/(?P<slug>.+)/$'), InvoiceDownloadView.as_view(), name='invoice_pdf'),
]
