import pytz
import datetime
from django.db import migrations

from velo.payment.bank import close_business_day


def calculate_old_transaction_daily_totals(apps, schema_editor):
    riga_tz = pytz.timezone("Europe/Riga")

    datums = riga_tz.localize(datetime.datetime(year=2016, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))
    while datums < riga_tz.localize(datetime.datetime.now()):
        close_business_day(datums)
        datums = datums + datetime.timedelta(days=1)


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20170121_1603'),
    ]

    operations = [
        migrations.RunPython(calculate_old_transaction_daily_totals),
    ]
