# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-11-29 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0003_auto_20180515_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='show_contact_info',
            field=models.BooleanField(default=True, verbose_name='Show contact information in public team profile'),
        ),
    ]
