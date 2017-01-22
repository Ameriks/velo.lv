# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-21 16:03
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Count, Max
from slugify import slugify

from velo.payment.models import Invoice, PaymentChannel, Payment
from django.db import connection


def set_sequences(apps, schema_editor):
    series = Invoice.objects.values('series').annotate(Count('series'), Max('number'))
    cursor = connection.cursor()
    for serie in series:
        sequence_name = "payment_sequence_%s" % slugify(serie.get('series'), only_ascii=True, ok="_")
        current = serie.get('number__max') + 1
        sql = 'CREATE SEQUENCE %s START %i;' % (sequence_name, current)
        print(sql)
        cursor.execute(sql)

    cursor.execute("ALTER TABLE core_log ALTER COLUMN params TYPE JSON USING params::JSON;")
    invoice1 = PaymentChannel.objects.get(id=1)
    invoice1.params = {
                        "name": "Latvijas Kalnu divriteņu federācija",
                        "juridical_address": "Brīvības gatve 222, Rīga, Latvija, LV-1039",
                        "number": "40008071001",
                        "vat": "",
                        "account_name": "SEB banka A/S",
                        "account_code": "UNLALV2X",
                        "account_number": "LV43UNLA0050013169379"
                        }
    invoice1.save()

    for payment in Payment.objects.filter(created__year__gte=2016):
        payment.transaction_set.create(
            channel=payment.channel.payment_channel,
            status=payment.status,
            amount=payment.total,
        )




class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_dailytransactiontotals'),
        ('registration', '0005_application_external_invoice_to_local_invoice'),
        ('team', '0003_team_external_invoice_to_local_invoice'),
    ]

    operations = [
        migrations.RunPython(set_sequences),
    ]