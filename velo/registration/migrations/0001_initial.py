# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-26 18:43
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('payment_status', models.SmallIntegerField(choices=[(0, 'Nav apmaksāts'), (10, 'Gaida maksājumu'), (20, 'Apmaksāts'), (-10, 'Atcelts')], default=0, verbose_name='Maksājuma statuss')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('can_send_newsletters', models.BooleanField(default=True, verbose_name='Es vēlos saņemt velo.lv jaunumus.')),
                ('code', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('legacy_id', models.IntegerField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=100, verbose_name='Uzņēmuma nosaukums / Vārds Uzvārds')),
                ('company_vat', models.CharField(blank=True, max_length=100, verbose_name='VAT Numurs')),
                ('company_regnr', models.CharField(blank=True, max_length=100, verbose_name='Uzņēmuma numurs / Personas kods')),
                ('company_address', models.CharField(blank=True, max_length=100, verbose_name='Adrese')),
                ('company_juridical_address', models.CharField(blank=True, max_length=100, verbose_name='Juridiskā adrese')),
                ('invoice_show_names', models.BooleanField(default=True, verbose_name='Rādīt dalībnieku vārdus rēķinā')),
                ('external_invoice_code', models.CharField(blank=True, max_length=100, verbose_name='Rēķina kods')),
                ('external_invoice_nr', models.CharField(blank=True, max_length=20, verbose_name='Rēķina numurs')),
                ('donation', models.DecimalField(decimal_places=2, default=0.0, max_digits=20, verbose_name='Ziedojums')),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_entry_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_insurance_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('final_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('params', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('language', models.CharField(choices=[('lv', 'Latvian'), ('en', 'English'), ('ru', 'Russian')], default='lv', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChangedName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('new_slug', models.SlugField()),
            ],
        ),
        migrations.CreateModel(
            name='CompanyApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('status', models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0)),
                ('code', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('team_name', models.CharField(max_length=50)),
                ('email', models.EmailField(help_text='Jūs saņemsiet maksājuma apstiprinājumu un informāciju par starta numuriem.', max_length=254)),
                ('description', models.TextField(blank=True, verbose_name='Apraksts')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanyParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('is_participating', models.BooleanField(default=False, verbose_name='Vai piedalās?')),
                ('first_name', models.CharField(blank=True, max_length=60, verbose_name='Vārds')),
                ('last_name', models.CharField(blank=True, max_length=60, verbose_name='Uzvārds')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Dzimšanas diena')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Vīrietis'), ('F', 'Sieviete')], max_length=1, verbose_name='Dzimums')),
                ('ssn', models.CharField(blank=True, max_length=12, verbose_name='Personas kods')),
                ('phone_number', models.CharField(blank=True, help_text='Uz šo telefona numuru tiks sūtīts rezultāts', max_length=60, verbose_name='Telefona numurs')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-pasts')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Valsts')),
                ('bike_brand2', models.CharField(blank=True, max_length=20, verbose_name='Velo Zīmols')),
                ('slug', models.SlugField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Number',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('status', models.SmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (-1, 'Deleted')], default=0)),
                ('number', models.IntegerField()),
                ('number_text', models.CharField(blank=True, max_length=50)),
                ('participant_slug', models.SlugField(blank=True)),
                ('group', models.CharField(blank=True, max_length=50, verbose_name='Grupa')),
            ],
            options={
                'ordering': ('distance', 'group', 'number'),
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Izveidots')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Labots')),
                ('code_short', models.CharField(blank=True, db_index=True, max_length=20)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('team_name', models.CharField(blank=True, max_length=50, verbose_name='Komanda')),
                ('team_name_slug', models.SlugField(blank=True)),
                ('is_participating', models.BooleanField(default=False, verbose_name='Vai piedalās?')),
                ('is_paying', models.BooleanField(default=True, verbose_name='Vai maksā?')),
                ('is_competing', models.BooleanField(default=True, verbose_name='Vai piedalās')),
                ('first_name', models.CharField(blank=True, max_length=60, verbose_name='Vārds')),
                ('last_name', models.CharField(blank=True, max_length=60, verbose_name='Uzvārds')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Dzimšanas diena')),
                ('is_only_year', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Vīrietis'), ('F', 'Sieviete')], max_length=1, verbose_name='Dzimums')),
                ('ssn', models.CharField(blank=True, max_length=12, verbose_name='Personas kods')),
                ('ssn_hashed', models.CharField(blank=True, max_length=44, verbose_name='Social Security Number Hashed')),
                ('phone_number', models.CharField(blank=True, help_text='Uz šo telefona numuru tiks sūtīts rezultāts', max_length=60, verbose_name='Telefona numurs')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='E-pasts')),
                ('send_email', models.BooleanField(default=True, verbose_name='Sūtīt e-pastu')),
                ('send_sms', models.BooleanField(default=True, verbose_name='Sūtīt SMS')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name='Valsts')),
                ('bike_brand2', models.CharField(blank=True, max_length=20, verbose_name='Velo Zīmols')),
                ('group', models.CharField(blank=True, help_text='Piešķirt automātiski', max_length=50, verbose_name='Grupa')),
                ('legacy_id', models.IntegerField(blank=True, null=True)),
                ('full_name', models.CharField(blank=True, max_length=120, verbose_name='Pilns vārds')),
                ('is_temporary', models.BooleanField(default=False)),
                ('is_sent_number_email', models.BooleanField(default=False)),
                ('is_sent_number_sms', models.BooleanField(default=False)),
                ('registration_dt', models.DateTimeField(blank=True, null=True, verbose_name='Reģistrēšanas datums')),
                ('comment', models.TextField(blank=True)),
                ('total_entry_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('total_insurance_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('final_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.Application')),
                ('bike_brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.Choices', verbose_name='Velo Zīmols')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.Choices', verbose_name='Pilsēta')),
                ('company_participant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.CompanyParticipant')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_participant_set', to=settings.AUTH_USER_MODEL)),
                ('distance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Distance')),
                ('insurance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Insurance')),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='modified_participant_set', to=settings.AUTH_USER_MODEL)),
                ('occupation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.Choices', verbose_name='Nodarbošanās')),
                ('price', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.Price')),
                ('primary_number', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.Number')),
                ('registrant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Reģistrētājs')),
            ],
            options={
                'verbose_name': 'dalībnieks',
                'verbose_name_plural': 'dalībnieki',
                'ordering': ('distance', 'created'),
            },
        ),
        migrations.CreateModel(
            name='PreNumberAssign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(blank=True, help_text='Ja jāpiešķir specifisks numurs.', null=True)),
                ('segment', models.IntegerField(blank=True, help_text='Ja jāpiešķir specifisks koridors.', null=True)),
                ('participant_slug', models.SlugField(blank=True)),
                ('group_together', models.SlugField(blank=True, help_text='Norādiet vienādu skaitli, lai cilvēkus sagrupētu vienā koridorī', null=True)),
                ('description', models.TextField(blank=True)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Competition')),
                ('distance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Distance')),
            ],
        ),
        migrations.CreateModel(
            name='UCICategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=60)),
                ('first_name', models.CharField(blank=True, max_length=60, verbose_name='Vārds')),
                ('last_name', models.CharField(blank=True, max_length=60, verbose_name='Uzvārds')),
                ('issued', models.DateField(blank=True, null=True)),
                ('code', models.CharField(max_length=20)),
                ('birthday', models.DateField(blank=True, help_text='YYYY-MM-DD', null=True, verbose_name='Dzimšanas diena')),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
        ),
    ]
