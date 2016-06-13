# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-13 06:26
from __future__ import unicode_literals

from django.db import migrations, models, connection

def migrate_data_back(apps, schema_editor):
    pass


def migrate_data(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("Update advert_banner set location=40, status=0")


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0005_auto_20160613_0006'),
    ]

    operations = [
        migrations.RunPython(migrate_data, migrate_data_back),
    ]
