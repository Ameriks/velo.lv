# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 23:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0003_auto_20160408_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailgunemail',
            name='content_type',
        ),
        migrations.DeleteModel(
            name='MailgunEmail',
        ),
    ]