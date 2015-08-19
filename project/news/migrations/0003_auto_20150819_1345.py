# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_news_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='intro_content',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='news',
            name='language',
            field=models.CharField(default=b'lv', max_length=20, verbose_name=b'Language', db_index=True, choices=[(b'lv', b'Latviski'), (b'en', b'English')]),
        ),
        migrations.AlterField(
            model_name='news',
            name='slug',
            field=models.SlugField(unique=True, verbose_name=b'Slug'),
        ),
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.CharField(max_length=255, verbose_name=b'Title'),
        ),
    ]
