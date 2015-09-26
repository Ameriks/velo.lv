# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_chipscan_url_sync'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlsync',
            name='index',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='urlsync',
            name='kind',
            field=models.CharField(default=b'FINISH', max_length=30),
        ),
    ]
