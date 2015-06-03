# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='price',
            options={'ordering': ('distance', 'start_registering'), 'permissions': (('can_see_totals', 'Can see income totals'),)},
        ),
    ]
