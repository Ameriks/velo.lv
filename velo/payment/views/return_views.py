from django.http import Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from velo.payment.models import Transaction, Payment
from velo.core.utils import log_message

__all__ = ['TransactionReturnView', ]


class TransactionReturnView(View):

    @method_decorator(never_cache)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        log = log_message('TransactionReturnView %s' % request.method, params={'GET': request.GET, 'POST': request.POST})

        if request.POST.get("trans_id", None):
            transaction = Transaction.objects.get(external_code=request.POST.get("trans_id"))
        else:
            if request.POST.get('VK_REF', None):
                _id = request.POST.get('VK_REF', None)
            elif request.GET.get('VK_REF', None):
                _id = request.GET.get('VK_REF', None)
            elif request.POST.get('IB_PAYMENT_ID', None):
                _id = request.POST.get('IB_PAYMENT_ID', None)
            elif request.GET.get('IB_PAYMENT_ID', None):
                _id = request.GET.get('IB_PAYMENT_ID', None)
            else:
                log.set_message("ERROR")
                raise Http404("ERROR")
            try:
                transaction = Transaction.objects.get(id=_id)
            except Transaction.DoesNotExist:
                pay = Payment.objects.get(id=_id)
                transaction = pay.transaction_set.all()[0]

        log.set_object(transaction)

        integration_object = transaction.channel.get_class(transaction)
        return integration_object.verify_return(request)
