# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('payment', '0001_initial'),
        ('marketing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='discount_code',
            field=models.ForeignKey(blank=True, to='payment.DiscountCode', null=True),
        ),
        migrations.AddField(
            model_name='mailgunemail',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
