import celery
import datetime
import os

from celery.schedules import crontab
from celery.task import periodic_task

from django.conf import settings
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


@celery.task
def update_family_codes(file_name: str):
    import xlrd
    from velo.payment.models import DiscountCode

    campaign_ids = [6, 8]
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    # adding new codes
    with xlrd.open_workbook(file_path) as wb:
        sheet = wb.sheet_by_name('Pieaugušo kartes')
        code_list = []
        for row in range(1, sheet.nrows):
            active_code = sheet.row_values(row)[0]
            d_codes = DiscountCode.objects.filter(code=active_code)

            if not d_codes:
                for camp_id in campaign_ids:
                    DiscountCode.objects.create(
                        campaign_id=camp_id,
                        code=active_code,
                        usage_times=0,
                    )
            code_list.append(active_code)

    # disabling codes if they ar not in the file
    for discount_code in DiscountCode.objects.filter(campaign_id__in=campaign_ids):
        if discount_code.code not in code_list:
            discount_code.is_active = False
            discount_code.save()

    os.remove(file_path)

