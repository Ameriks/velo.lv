# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chipscan',
            name='url_sync',
            field=models.ForeignKey(blank=True, to='results.UrlSync', null=True),
        ),
    ]
