# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-19 16:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_participant_survey_answer1'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='t_shirt_size',
            field=models.CharField(choices=[('XS', 'UNISEX XS'), ('S', 'UNISEX S'), ('M', 'UNISEX M'), ('L', 'UNISEX L'), ('XL', 'UNISEX XL'), ('XXL', 'UNISEX XXL')], max_length=3, null=True, verbose_name='T-Shirt size'),
        ),
    ]
