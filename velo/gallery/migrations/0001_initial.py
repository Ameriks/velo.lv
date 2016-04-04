# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import easy_thumbnails.fields
from django.conf import settings
import gallery.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('title', models.CharField(max_length=255)),
                ('gallery_date', models.DateField()),
                ('photographer', models.CharField(max_length=255, blank=True)),
                ('folder', models.FilePathField(path=b'media/gallery/', allow_files=False, recursive=True, allow_folders=True)),
                ('description', models.TextField(blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_internal', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-gallery_date', '-id'),
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('description', models.TextField(blank=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(max_length=255, upload_to=gallery.models._get_image_upload_path, blank=True)),
                ('md5', models.CharField(max_length=32, blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_numbered', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
                ('is_vertical', models.NullBooleanField(default=None)),
                ('width', models.IntegerField(null=True, blank=True)),
                ('height', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('image',),
                'permissions': (('can_assign_numbers', 'Can assign numbers'),),
            },
        ),
        migrations.CreateModel(
            name='PhotoNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('x1', models.FloatField(null=True, blank=True)),
                ('y1', models.FloatField(null=True, blank=True)),
                ('x2', models.FloatField(null=True, blank=True)),
                ('y2', models.FloatField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_photonumber_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_photonumber_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('kind', models.PositiveSmallIntegerField(default=1, choices=[(1, b'YouTube'), (2, b'Vimeo')])),
                ('video_id', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('published_at', models.DateTimeField(null=True, blank=True)),
                ('channel_title', models.CharField(max_length=255, blank=True)),
                ('view_count', models.IntegerField(default=0)),
                ('is_featured', models.BooleanField(default=False)),
                ('is_agency_video', models.BooleanField(default=False)),
                ('ordering', models.IntegerField(default=0)),
                ('image_maxres', models.URLField(blank=True)),
                ('image', models.URLField(blank=True)),
                ('competition', models.ForeignKey(blank=True, to='core.Competition', null=True)),
                ('created_by', models.ForeignKey(related_name='created_video_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_video_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('is_featured', 'ordering', 'title'),
                'permissions': (('can_see_unpublished_video', 'Can see unpublished video'),),
            },
        ),
    ]
