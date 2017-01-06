# coding=utf-8
from __future__ import unicode_literals

import celery
import datetime
from celery.schedules import crontab
from celery.task import periodic_task

from django.utils import timezone

from velo.payment.models import Payment, Transaction
from velo.payment.utils import validate_payment


@periodic_task(run_every=crontab(minute="*/10", ))
def get_transaction_statuses():
    payments = Payment.objects.filter(status__in=(Payment.STATUSES.new, Payment.STATUSES.pending),
                                      created__lt=(timezone.now() - datetime.timedelta(minutes=10)))

    for payment in payments:
        validate_payment(payment)

    return True


@celery.task
def process_server_response(transaction_id):
    from velo.payment.bank import Swedbank, IBanka, FirstDataIntegration
    t = Transaction.objects.get(id=transaction_id)
    if t.link.title == "Swedbank":
        instance = Swedbank(t.id)
    elif t.link.title == "FirstData":
        instance = FirstDataIntegration(t.id)
    elif t.link.title == "IBanka":
        instance = IBanka(t.id)
    else:
        instance = None
    # class_ = import_class(t.link.bank.integration_class)

    if not instance.server_check_transaction():
        process_server_response.apply_async(args=[transaction_id], countdown=30)

    return True


@periodic_task(run_every=crontab(minute="*/10"))
def timeout_old_transactions():
    transactions = Transaction.objects.filter(status__in=[Transaction.STATUS.new, Transaction.STATUS.pending],
                                              modified__lt=(timezone.now() - datetime.timedelta(minutes=15)))
    for t in transactions:
        # log_message('TIMEOUT Transaction', object=t)
        t.status = Transaction.STATUS_TIMEOUT
        t.save()
