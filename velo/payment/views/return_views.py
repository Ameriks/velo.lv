from braces.views import CsrfExemptMixin

from django.http import Http404
from django.views import View

from velo.payment.models import Transaction
from velo.velo.mixins.views import NeverCacheMixin

__all__ = ['TransactionReturnView', ]


class TransactionReturnView(CsrfExemptMixin, NeverCacheMixin, View):
    integration_object = None

    def get(self, request, *args, **kwargs):
        transaction = Transaction.objects.get(code=kwargs.get('code'))
        self.integration_object = transaction.link.get_class(transaction)

        if not request.GET:
            raise Http404

        return self.integration_object.verify_return(request)

    def post(self, request, *args, **kwargs):
        if kwargs.get('code'):
            transaction = Transaction.objects.get(code=kwargs.get('code'))
        elif request.POST.get("trans_id"):
            transaction = Transaction.objects.get(external_code=request.POST.get("trans_id"))
        else:
            raise Http404("ERROR")

        self.integration_object = transaction.link.get_class(transaction)

        if not request.GET and not request.POST:
            raise Http404

        return self.integration_object.verify_return(request)
