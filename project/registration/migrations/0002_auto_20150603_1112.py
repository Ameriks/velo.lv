# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0001_initial'),
        ('payment', '0001_initial'),
        ('core', '0001_initial'),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='team',
            field=models.ForeignKey(blank=True, to='team.Team', null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='where_heard',
            field=models.ForeignKey(related_name='+', verbose_name='Where Heard', blank=True, to='core.Choices', null=True),
        ),
        migrations.AddField(
            model_name='number',
            name='competition',
            field=models.ForeignKey(to='core.Competition'),
        ),
        migrations.AddField(
            model_name='number',
            name='created_by',
            field=models.ForeignKey(related_name='created_number_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='number',
            name='distance',
            field=models.ForeignKey(to='core.Distance'),
        ),
        migrations.AddField(
            model_name='number',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_number_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='application',
            field=models.ForeignKey(related_name='participant_set', to='registration.CompanyApplication'),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='created_by',
            field=models.ForeignKey(related_name='created_companyparticipant_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='distance',
            field=models.ForeignKey(blank=True, to='core.Distance', null=True),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_companyparticipant_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='companyparticipant',
            name='team_member',
            field=models.ForeignKey(blank=True, to='team.Member', null=True),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='competition',
            field=models.ForeignKey(to='core.Competition'),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='created_by',
            field=models.ForeignKey(related_name='created_companyapplication_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='companyapplication',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_companyapplication_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='competition',
            field=models.ForeignKey(verbose_name='Competition', to='core.Competition'),
        ),
        migrations.AddField(
            model_name='application',
            name='created_by',
            field=models.ForeignKey(related_name='created_application_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='discount_code',
            field=models.ForeignKey(blank=True, to='payment.DiscountCode', null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_application_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='number',
            unique_together=set([('competition', 'number', 'group')]),
        ),
    ]
