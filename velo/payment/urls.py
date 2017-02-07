from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from velo.payment.views import CheckPriceView, InvoiceDownloadView, TransactionRedirectView

urlpatterns = [
                       url(_(r'^checkprice/(?P<pk>\d+)/$'), CheckPriceView.as_view(), name='check_price'),

                       url(_(r'^invoice/(?P<slug>.+)/$'), InvoiceDownloadView.as_view(), name='invoice_pdf'),

                       url(_(r'^transaction/(?P<slug>.+)/$'), TransactionRedirectView.as_view(), name='transaction'),
]
