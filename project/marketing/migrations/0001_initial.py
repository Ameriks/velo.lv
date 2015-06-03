# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MailgunEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('code', models.CharField(default=uuid.uuid4, unique=True, max_length=50)),
                ('em_from', models.CharField(default='Tavs velo.lv <hi@mans.velo.lv>', max_length=85)),
                ('em_to', models.CharField(max_length=255)),
                ('em_cc', models.CharField(max_length=255)),
                ('em_replyto', models.CharField(default=b'pieteikumi@velo.lv', max_length=255)),
                ('subject', models.TextField()),
                ('html', models.TextField()),
                ('text', models.TextField()),
                ('is_sent', models.BooleanField(default=False)),
                ('mailgun_id', models.CharField(max_length=80, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=20)),
                ('text', models.CharField(max_length=160)),
                ('is_processed', models.BooleanField(default=False)),
                ('response', models.TextField(blank=True)),
                ('send_out_at', models.DateTimeField()),
                ('status', models.CharField(max_length=50, blank=True)),
            ],
        ),
    ]
