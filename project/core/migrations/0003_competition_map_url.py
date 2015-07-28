# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_competition_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='map_url',
            field=models.URLField(blank=True),
        ),
    ]
