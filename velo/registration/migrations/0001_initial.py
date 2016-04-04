# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('payment_status', models.SmallIntegerField(default=0, verbose_name='Payment Status', choices=[(-10, 'Cancelled'), (0, "Haven't Payed"), (5, 'Approved for Payment'), (10, 'Waiting for Payment'), (20, 'Payed')])),
                ('email', models.EmailField(help_text='You will receive payment confirmation and information about start numbers.', max_length=254, blank=True)),
                ('code', models.CharField(default=uuid.uuid4, unique=True, max_length=50)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('company_name', models.CharField(max_length=100, verbose_name='Company name / Full Name', blank=True)),
                ('company_vat', models.CharField(max_length=100, verbose_name='VAT Number', blank=True)),
                ('company_regnr', models.CharField(max_length=100, verbose_name='Company number / SSN', blank=True)),
                ('company_address', models.CharField(max_length=100, verbose_name='Address', blank=True)),
                ('company_juridical_address', models.CharField(max_length=100, verbose_name='Juridical Address', blank=True)),
                ('invoice_show_names', models.BooleanField(default=True, verbose_name='Show participant names in invoice')),
                ('external_invoice_code', models.CharField(max_length=100, verbose_name='Invoice code', blank=True)),
                ('external_invoice_nr', models.CharField(max_length=20, verbose_name='Invoice Number', blank=True)),
                ('donation', models.DecimalField(default=0.0, verbose_name='Donation', max_digits=20, decimal_places=2)),
                ('total_discount', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('total_entry_fee', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('total_insurance_fee', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('final_price', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChangedName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('new_slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='CompanyApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('code', models.CharField(default=uuid.uuid4, unique=True, max_length=50)),
                ('team_name', models.CharField(max_length=50)),
                ('email', models.EmailField(help_text='You will receive payment confirmation and information about start numbers.', max_length=254)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanyParticipant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('is_participating', models.BooleanField(default=False, verbose_name='Is Participating')),
                ('first_name', models.CharField(max_length=60, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=60, verbose_name='Last Name', blank=True)),
                ('birthday', models.DateField(help_text='YYYY-MM-DD', null=True, verbose_name='Birthday', blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='Gender', choices=[('M', 'Male'), ('F', 'Female')])),
                ('ssn', models.CharField(max_length=12, verbose_name='Social Security Number', blank=True)),
                ('phone_number', models.CharField(help_text='Uz \u0161o telefona numuru tiks s\u016bt\u012bts rezult\u0101ts', max_length=60, verbose_name='Phone Number', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country')),
                ('bike_brand2', models.CharField(max_length=20, verbose_name='Bike Brand', blank=True)),
                ('slug', models.SlugField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Number',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('number', models.IntegerField()),
                ('number_text', models.CharField(max_length=50, blank=True)),
                ('participant_slug', models.SlugField(blank=True)),
                ('group', models.CharField(max_length=50, verbose_name='Group', blank=True)),
            ],
            options={
                'ordering': ('distance', 'group', 'number'),
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('code_short', models.CharField(db_index=True, max_length=20, blank=True)),
                ('discount_amount', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('team_name', models.CharField(max_length=50, verbose_name='Team', blank=True)),
                ('team_name_slug', models.SlugField(blank=True)),
                ('is_participating', models.BooleanField(default=False, verbose_name='Is Participating')),
                ('is_paying', models.BooleanField(default=True, verbose_name='Is Paying')),
                ('is_competing', models.BooleanField(default=True, verbose_name='Is Competing')),
                ('first_name', models.CharField(max_length=60, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=60, verbose_name='Last Name', blank=True)),
                ('birthday', models.DateField(help_text='YYYY-MM-DD', null=True, verbose_name='Birthday', blank=True)),
                ('is_only_year', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='Gender', choices=[('M', 'Male'), ('F', 'Female')])),
                ('ssn', models.CharField(max_length=12, verbose_name='Social Security Number', blank=True)),
                ('phone_number', models.CharField(help_text='Uz \u0161o telefona numuru tiks s\u016bt\u012bts rezult\u0101ts', max_length=60, verbose_name='Phone Number', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Email', blank=True)),
                ('send_email', models.BooleanField(default=True, verbose_name='Send Email')),
                ('send_sms', models.BooleanField(default=True, verbose_name='Send SMS')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Country')),
                ('bike_brand2', models.CharField(max_length=20, verbose_name='Bike Brand', blank=True)),
                ('group', models.CharField(help_text='Assigned automatically', max_length=50, verbose_name='Group', blank=True)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('full_name', models.CharField(max_length=120, verbose_name='Full Name', blank=True)),
                ('is_temporary', models.BooleanField(default=False)),
                ('is_sent_number_email', models.BooleanField(default=False)),
                ('is_sent_number_sms', models.BooleanField(default=False)),
                ('registration_dt', models.DateTimeField(null=True, verbose_name='Registration Date', blank=True)),
                ('comment', models.TextField(blank=True)),
                ('total_entry_fee', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('total_insurance_fee', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('final_price', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('application', models.ForeignKey(blank=True, to='registration.Application', null=True)),
                ('bike_brand', models.ForeignKey(related_name='+', verbose_name='Bike Brand', blank=True, to='core.Choices', null=True)),
                ('city', models.ForeignKey(related_name='+', verbose_name='City', blank=True, to='core.Choices', null=True)),
                ('company_participant', models.ForeignKey(blank=True, to='registration.CompanyParticipant', null=True)),
                ('competition', models.ForeignKey(to='core.Competition')),
                ('created_by', models.ForeignKey(related_name='created_participant_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('distance', models.ForeignKey(blank=True, to='core.Distance', null=True)),
                ('insurance', models.ForeignKey(blank=True, to='core.Insurance', null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_participant_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('occupation', models.ForeignKey(related_name='+', verbose_name='Occupation', blank=True, to='core.Choices', null=True)),
                ('price', models.ForeignKey(blank=True, to='payment.Price', null=True)),
                ('primary_number', models.ForeignKey(blank=True, to='registration.Number', null=True)),
                ('registrant', models.ForeignKey(verbose_name='Registrant', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('distance', 'created'),
                'verbose_name': 'participant',
                'verbose_name_plural': 'participants',
            },
        ),
        migrations.CreateModel(
            name='PreNumberAssign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(help_text='If specific number should be given', null=True, blank=True)),
                ('segment', models.IntegerField(help_text='If specific passage should be given', null=True, blank=True)),
                ('participant_slug', models.SlugField(blank=True)),
                ('group_together', models.SlugField(help_text='Group together in one passage', null=True, blank=True)),
                ('description', models.TextField(blank=True)),
                ('competition', models.ForeignKey(to='core.Competition')),
                ('distance', models.ForeignKey(to='core.Distance')),
            ],
        ),
    ]
