# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import velo.supporter.models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetitionSupporter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('support_level', models.PositiveSmallIntegerField(choices=[(10, 'Supporter'), (30, 'Partner'), (40, 'Technical Partner'), (70, 'Sponsor'), (90, 'General Sponsor')])),
                ('label', models.CharField(max_length=100, blank=True)),
                ('ordering', models.IntegerField(default=0)),
                ('competition', models.ForeignKey(to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='Logo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'height', width_field=b'width', upload_to=velo.supporter.models._get_logo_upload_path, blank=True)),
                ('width', models.FloatField(null=True, blank=True)),
                ('height', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supporter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField(blank=True)),
                ('is_agency_supporter', models.BooleanField(default=False)),
                ('supporter_kind', models.CharField(max_length=100, blank=True)),
                ('ordering', models.IntegerField(default=0, db_index=True)),
                ('default_logo', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='supporter.Logo', null=True)),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.AddField(
            model_name='logo',
            name='supporter',
            field=models.ForeignKey(to='supporter.Supporter'),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='logo',
            field=models.ForeignKey(blank=True, to='supporter.Logo', null=True),
        ),
        migrations.AddField(
            model_name='competitionsupporter',
            name='supporter',
            field=models.ForeignKey(to='supporter.Supporter'),
        ),
    ]
