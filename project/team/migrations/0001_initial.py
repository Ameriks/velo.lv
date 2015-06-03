# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import team.models
import django_countries.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('first_name', models.CharField(max_length=60, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=60, verbose_name='Last Name')),
                ('birthday', models.DateField(verbose_name='Birthday')),
                ('slug', models.SlugField()),
                ('ssn', models.CharField(max_length=12, verbose_name='SSN', blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='Gender', choices=[('M', 'Male'), ('F', 'Female')])),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('license_nr', models.CharField(max_length=50, verbose_name='License NR', blank=True)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MemberApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.SmallIntegerField(db_index=True, verbose_name='Kind', choices=[(10, 'Participant'), (20, 'Reserve')])),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('competition', models.ForeignKey(to='core.Competition')),
                ('member', models.ForeignKey(to='team.Member')),
                ('participant', models.ForeignKey(blank=True, to='registration.Participant', null=True)),
                ('participant_potential', models.ForeignKey(related_name='memberapplication_potential_set', blank=True, to='registration.Participant', null=True)),
                ('participant_unpaid', models.ForeignKey(related_name='memberapplication_unpaid_set', blank=True, to='registration.Participant', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('slug', models.SlugField()),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('img', models.ImageField(upload_to=team.models.get_team_upload, verbose_name='Image', blank=True)),
                ('shirt_image', models.ImageField(upload_to=team.models.get_team_upload, verbose_name='Shirt Image', blank=True)),
                ('country', django_countries.fields.CountryField(max_length=2, verbose_name='Country')),
                ('contact_person', models.CharField(max_length=100, verbose_name='Contact Person', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('phone_number', models.CharField(max_length=50, verbose_name='Phone Number', blank=True)),
                ('management_info', models.TextField(verbose_name='Management Info', blank=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('final_price', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('company_name', models.CharField(max_length=100, verbose_name='Company name / Full Name', blank=True)),
                ('company_vat', models.CharField(max_length=100, verbose_name='VAT Number', blank=True)),
                ('company_regnr', models.CharField(max_length=100, verbose_name='Company number / SSN', blank=True)),
                ('company_address', models.CharField(max_length=100, verbose_name='Address', blank=True)),
                ('company_juridical_address', models.CharField(max_length=100, verbose_name='Juridical Address', blank=True)),
                ('external_invoice_code', models.CharField(max_length=100, verbose_name='Invoice code', blank=True)),
                ('external_invoice_nr', models.CharField(max_length=20, verbose_name='Invoice Number', blank=True)),
                ('created_by', models.ForeignKey(related_name='created_team_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('distance', models.ForeignKey(to='core.Distance')),
                ('modified_by', models.ForeignKey(related_name='modified_team_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('distance', '-is_featured', 'title'),
            },
        ),
        migrations.AddField(
            model_name='member',
            name='team',
            field=models.ForeignKey(to='team.Team'),
        ),
    ]
