# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staticpage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staticpage',
            name='content',
            field=ckeditor.fields.RichTextField(verbose_name='content', blank=True),
        ),
    ]
