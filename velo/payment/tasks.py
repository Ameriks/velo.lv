import celery
import datetime
from celery.schedules import crontab
from celery.task import periodic_task

from django.utils import timezone

from velo.payment.models import Transaction
from velo.payment.utils import log_message


@celery.task
def check_firstdata_transaction(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    instance = transaction.link.get_class(transaction)

    if not instance.server_check_transaction():
        check_firstdata_transaction.apply_async(args=[transaction_id], countdown=30)

    return True


@periodic_task(run_every=crontab(minute="*/10"))
def timeout_old_transactions():
    transactions = Transaction.objects.filter(status__in=[Transaction.STATUS.new, Transaction.STATUS.pending],
                                              modified__lt=(timezone.now() - datetime.timedelta(minutes=15)))
    for t in transactions:
        log_message('TIMEOUT Transaction', object=t)
        t.status = Transaction.STATUS_TIMEOUT
        t.save()
