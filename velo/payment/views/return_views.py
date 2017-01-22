from django.http import Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from velo.payment.models import Transaction
from velo.core.utils import log_message

__all__ = ['TransactionReturnView', ]


class TransactionReturnView(View):

    @method_decorator(never_cache)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        log = log_message('TransactionReturnView %s' % request.method, params={'GET': request.GET, 'POST': request.POST})

        if kwargs.get('code'):
            transaction = Transaction.objects.get(code=kwargs.get('code'))
        elif request.POST.get("trans_id"):
            transaction = Transaction.objects.get(external_code=request.POST.get("trans_id"))
        else:
            raise Http404("ERROR")

        log.content_object = transaction
        log.save()

        integration_object = transaction.link.get_class(transaction)

        return integration_object.verify_return(request)
