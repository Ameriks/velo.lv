# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_competition_map_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='frontpage_ordering',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
