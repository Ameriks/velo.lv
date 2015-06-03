# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import news.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gallery', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('content', models.TextField()),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='created_comment_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_comment_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
                ('published_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('intro_content', models.TextField()),
                ('content', models.TextField(blank=True)),
                ('tmp_string', models.CharField(max_length=255, blank=True)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('competition', models.ForeignKey(blank=True, to='core.Competition', null=True)),
                ('created_by', models.ForeignKey(related_name='created_news_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('image', models.ForeignKey(blank=True, to='gallery.Photo', null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_news_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('slug', models.CharField(default=news.models.notification_slug, max_length=6)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='news',
            field=models.ForeignKey(to='news.News'),
        ),
    ]
