# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-04-01 14:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_invoice_invoice_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountcode',
            name='code',
            field=models.CharField(max_length=20),
        ),
    ]
