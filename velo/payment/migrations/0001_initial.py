# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivePaymentChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_date', models.DateTimeField()),
                ('till_date', models.DateTimeField()),
                ('competition', models.ForeignKey(to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCampaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('discount_entry_fee_percent', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('discount_entry_fee', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('discount_insurance_percent', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('discount_insurance', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('competition', models.ForeignKey(to='core.Competition')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('code', models.CharField(unique=True, max_length=20)),
                ('usage_times', models.IntegerField(default=1)),
                ('usage_times_left', models.IntegerField(default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(to='payment.DiscountCampaign')),
                ('created_by', models.ForeignKey(related_name='created_discountcode_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_discountcode_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('erekins_code', models.CharField(max_length=100, blank=True)),
                ('total', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('donation', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('status', models.SmallIntegerField(default=10, choices=[(-70, 'ID not found'), (-60, 'Error'), (-50, 'Failed'), (-40, 'Declined'), (-30, 'Timeout'), (-20, 'Cancelled'), (-10, 'Reversed'), (10, 'New'), (20, 'Pending'), (30, 'OK')])),
                ('channel', models.ForeignKey(to='payment.ActivePaymentChannel')),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('created_by', models.ForeignKey(related_name='created_payment_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_payment_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_channel', models.CharField(default='LKDF', max_length=20)),
                ('title', models.CharField(max_length=50)),
                ('image_slug', models.CharField(max_length=50, blank=True)),
                ('erekins_url_prefix', models.CharField(max_length=50, blank=True)),
                ('erekins_auth_key', models.CharField(max_length=100, blank=True)),
                ('erekins_link', models.CharField(max_length=50, blank=True)),
                ('is_bill', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('from_year', models.IntegerField(default=0)),
                ('till_year', models.IntegerField(default=2050)),
                ('price', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('start_registering', models.DateTimeField(null=True, blank=True)),
                ('end_registering', models.DateTimeField(null=True, blank=True)),
                ('competition', models.ForeignKey(to='core.Competition')),
                ('created_by', models.ForeignKey(related_name='created_price_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('distance', models.ForeignKey(to='core.Distance')),
                ('modified_by', models.ForeignKey(related_name='modified_price_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('distance', 'start_registering'),
                'permissions': ('can_see_totals', 'Can see income totals'),
            },
        ),
        migrations.AddField(
            model_name='activepaymentchannel',
            name='payment_channel',
            field=models.ForeignKey(to='payment.PaymentChannel'),
        ),
    ]
