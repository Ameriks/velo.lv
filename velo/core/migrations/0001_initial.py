# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models, migrations
import velo.core.models
import django_countries.fields
import mptt.fields
import django.contrib.auth.models
import django.db.models.deletion
import easy_thumbnails.fields
import django.utils.timezone
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
        ('sitetree', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name', blank=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email Address')),
                ('email_status', models.SmallIntegerField(default=10, choices=[(-10, b'Invalid'), (10, b'Not yet validated'), (20, b'Bounced'), (40, b'Validating'), (50, b'Valid')])),
                ('email_validation_code', models.CharField(default=uuid.uuid4, max_length=36)),
                ('email_validation_expiry', models.DateTimeField(null=True, blank=True)),
                ('country', django_countries.fields.CountryField(default=b'LV', max_length=2, blank=True, null=True, verbose_name='Country')),
                ('ssn', models.CharField(max_length=12, verbose_name='Social Security Number', blank=True)),
                ('birthday', models.DateField(help_text=b'YYYY-MM-DD', null=True, verbose_name='Birthday', blank=True)),
                ('phone_number', models.CharField(max_length=60, verbose_name='Phone Number', blank=True)),
                ('send_email', models.BooleanField(default=True, verbose_name='Send Email Newsletters')),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('full_name', models.CharField(max_length=60, verbose_name='Full Name', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Choices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.SmallIntegerField(choices=[(10, b'Bike Brand'), (20, b'Occupation'), (30, b'Where Heard'), (40, b'City')])),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('alias', models.SlugField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('place_name', models.CharField(max_length=50, blank=True)),
                ('competition_date', models.DateField(null=True, blank=True)),
                ('competition_date_till', models.DateField(null=True, blank=True)),
                ('kind', models.SmallIntegerField(default=0, choices=[(0, b'Velo'), (1, b'Cross Country')])),
                ('complex_payment_enddate', models.DateTimeField(null=True, blank=True)),
                ('complex_payment_hideon', models.DateTimeField(null=True, blank=True)),
                ('complex_discount', models.SmallIntegerField(default=0)),
                ('bill_series', models.CharField(default=b'B', max_length=20, blank=True)),
                ('payment_channel', models.CharField(default=b'LKDF', max_length=20)),
                ('processing_class', models.CharField(max_length=100, blank=True)),
                ('legacy_id', models.IntegerField(null=True, blank=True)),
                ('is_in_menu', models.BooleanField(default=False)),
                ('skin', models.CharField(max_length=50, blank=True)),
                ('logo', easy_thumbnails.fields.ThumbnailerImageField(upload_to=velo.core.models._get_logo_upload_path, blank=True)),
                ('apply_image', easy_thumbnails.fields.ThumbnailerImageField(upload_to=velo.core.models._get_logo_upload_path, blank=True)),
                ('params', JSONField(null=True, blank=True)),
                ('sms_text', models.CharField(max_length=255, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('created_by', models.ForeignKey(related_name='created_competition_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_competition_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', blank=True, to='core.Competition', null=True)),
                ('sitetree', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sitetree.TreeItem', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomSlug',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=60)),
                ('last_name', models.CharField(max_length=60)),
                ('birthday', models.DateField()),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('name', models.CharField(max_length=100)),
                ('distance_text', models.CharField(max_length=50, blank=True)),
                ('distance_m', models.IntegerField(help_text=b'Distance in meters', null=True, blank=True)),
                ('can_have_teams', models.BooleanField(default=True)),
                ('have_results', models.BooleanField(default=True)),
                ('profile_price', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('kind', models.CharField(max_length=1, blank=True)),
                ('competition', models.ForeignKey(to='core.Competition')),
                ('created_by', models.ForeignKey(related_name='created_distance_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='modified_distance_set', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FailedTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=125)),
                ('full_name', models.TextField()),
                ('args', models.TextField(null=True, blank=True)),
                ('kwargs', models.TextField(null=True, blank=True)),
                ('exception_class', models.TextField()),
                ('exception_msg', models.TextField()),
                ('traceback', models.TextField(null=True, blank=True)),
                ('celery_task_id', models.CharField(max_length=36)),
                ('failures', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'ordering': ('-updated_at',),
            },
        ),
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, b'Inactive'), (1, b'Active'), (-1, b'Deleted')])),
                ('title', models.CharField(max_length=100)),
                ('price', models.DecimalField(default=0.0, max_digits=20, decimal_places=2)),
                ('in_complex', models.BooleanField(default=True)),
                ('complex_discount', models.SmallIntegerField(default=0)),
                ('competition', models.ForeignKey(to='core.Competition')),
            ],
            options={
                'ordering': ('competition', 'price'),
            },
        ),
        migrations.CreateModel(
            name='InsuranceCompany',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('term', models.TextField(blank=True)),
                ('terms_doc', models.FileField(upload_to=velo.core.models._get_insurance_term_upload_path, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('action', models.CharField(max_length=50, blank=True)),
                ('message', models.CharField(max_length=255, blank=True)),
                ('params', JSONField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to=velo.core.models._get_map_upload_path)),
                ('ordering', models.IntegerField(default=0)),
                ('competition', models.ForeignKey(to='core.Competition')),
            ],
            options={
                'ordering': ('competition', 'ordering'),
            },
        ),
        migrations.AddField(
            model_name='insurance',
            name='insurance_company',
            field=models.ForeignKey(to='core.InsuranceCompany'),
        ),
        migrations.AddField(
            model_name='user',
            name='bike_brand',
            field=models.ForeignKey(related_name='+', verbose_name='Bike Brand', blank=True, to='core.Choices', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.ForeignKey(related_name='+', verbose_name='City', blank=True, to='core.Choices', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AlterOrderWithRespectTo(
            name='distance',
            order_with_respect_to='competition',
        ),
    ]
