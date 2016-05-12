# coding=utf-8
from __future__ import unicode_literals

import datetime
from celery.schedules import crontab
from celery.task import periodic_task

from django.utils import timezone

from velo.payment.models import Payment
from velo.payment.utils import validate_payment


@periodic_task(run_every=crontab(minute="*/10", ))
def get_transaction_statuses():
    payments = Payment.objects.filter(status__in=(Payment.STATUSES.new, Payment.STATUSES.pending),
                                      created__lt=(timezone.now() - datetime.timedelta(minutes=10)))

    for payment in payments:
        validate_payment(payment)

    return True
