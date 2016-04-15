# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-14 15:46
from __future__ import unicode_literals

from django.db import migrations, models
from django.db import connection

import velo.core.models


def migrate_data(apps, schema_editor):
    cursor = connection.cursor()
    velo.core.models.Competition.objects.filter(id=51).update(logo_svg="competition/51_seb-maratons.svg")
    velo.core.models.Competition.objects.filter(id=54).update(logo_svg="competition/54_uec--white.svg")
    velo.core.models.Competition.objects.filter(id=60).update(logo_svg="competition/60_rigas-bernu-velomaratons.svg")
    velo.core.models.Competition.objects.filter(id=61).update(logo_svg="competition/61_rigas-velomaratons.svg")
    velo.core.models.Competition.objects.filter(id=62).update(logo_svg="competition/61_rigas-velomaratons.svg")
    cursor.execute("Update core_competition set processing_class='velo.' || processing_class where processing_class <> ''")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20160408_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='logo_svg',
            field=models.FileField(blank=True, upload_to=velo.core.models._get_logo_upload_path),
        ),
        migrations.RunPython(migrate_data),
    ]
