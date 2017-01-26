# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.sites.models
from django.conf import settings
from django.db import migrations, models


def update_site_forward(apps, schema_editor):
    """Set site domain and name."""
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": "velo.lv",
            "name": "velo.lv"
        }
    )


def update_site_backward(apps, schema_editor):
    """Revert site domain and name to default."""
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": "example.com",
            "name": "example.com"
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site_forward, update_site_backward),
        migrations.AlterModelManagers(
            name='site',
            managers=[
                ('objects', django.contrib.sites.models.SiteManager()),
            ],
        ),
        migrations.AlterField(
            model_name='site',
            name='domain',
            field=models.CharField(max_length=100, unique=True,
                                   validators=[django.contrib.sites.models._simple_domain_name_validator],
                                   verbose_name='domain name'),
        ),
    ]
