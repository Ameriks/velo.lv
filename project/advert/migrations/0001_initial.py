# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import advert.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlashBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('title', models.CharField(max_length=50, blank=True)),
                ('banner', models.FileField(upload_to=advert.models.get_banner_upload)),
                ('location', models.CharField(max_length=20, choices=[(b'left-side', b'left-side')])),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('converted', models.TextField(help_text=b'Convert flash to html5 in https://www.google.com/doubleclick/studio/swiffy/', blank=True)),
                ('url', models.URLField(blank=True)),
                ('ordering', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
    ]
