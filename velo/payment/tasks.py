import celery
import datetime
from celery.schedules import crontab
from celery.task import periodic_task

from django.utils import timezone

from velo.payment.bank import close_business_day
from velo.payment.models import Transaction, Payment
from velo.core.utils import log_message
from velo.payment.utils import approve_payment


@celery.task
def check_firstdata_transaction(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    instance = transaction.channel.get_class(transaction)

    if not instance.server_check_transaction():
        check_firstdata_transaction.apply_async(args=[transaction_id], countdown=30)

    return True


@periodic_task(run_every=crontab(minute="*/10"))
def timeout_old_transactions():
    transactions = Transaction.objects.filter(status__in=[Transaction.STATUSES.new, Transaction.STATUSES.pending],
                                              modified__lt=(timezone.now() - datetime.timedelta(minutes=15)))
    for t in transactions:
        log_message('TIMEOUT Transaction', object=t)
        t.status = Transaction.STATUSES.timeout
        t.save()


@periodic_task(run_every=crontab(minute="35", hour="0"))
def close_business_day_task():
    close_business_day()


@periodic_task(run_every=crontab(minute="*/22"))
def check_transactions():
    ok_payments = list(Payment.objects.filter(status=Payment.STATUSES.pending, transaction__status=Transaction.STATUSES.ok))
    for ok_payment in ok_payments:
        approve_payment(ok_payment)
