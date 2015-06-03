# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=100, verbose_name='URL', db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('enable_comments', models.BooleanField(default=False, verbose_name='enable comments')),
                ('ordering', models.IntegerField(default=0)),
                ('is_published', models.BooleanField(default=True)),
                ('language', models.CharField(default='', max_length=10, blank=True, choices=[('', '*'), (b'lv', b'Latvian'), (b'en', b'English')])),
                ('competition', models.ForeignKey(blank=True, to='core.Competition', null=True)),
            ],
            options={
                'ordering': ('competition', 'ordering'),
                'verbose_name': 'flat page',
                'verbose_name_plural': 'flat pages',
            },
        ),
    ]
