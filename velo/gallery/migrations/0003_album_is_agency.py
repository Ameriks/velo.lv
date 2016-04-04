# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20150603_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='is_agency',
            field=models.BooleanField(default=False),
        ),
    ]
