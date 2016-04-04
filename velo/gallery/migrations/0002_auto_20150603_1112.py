# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gallery', '0001_initial'),
        ('registration', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photonumber',
            name='number',
            field=models.ForeignKey(to='registration.Number'),
        ),
        migrations.AddField(
            model_name='photonumber',
            name='photo',
            field=models.ForeignKey(to='gallery.Photo'),
        ),
        migrations.AddField(
            model_name='photo',
            name='album',
            field=models.ForeignKey(to='gallery.Album'),
        ),
        migrations.AddField(
            model_name='photo',
            name='created_by',
            field=models.ForeignKey(related_name='created_photo_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_photo_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='numbers',
            field=models.ManyToManyField(to='registration.Number', through='gallery.PhotoNumber'),
        ),
        migrations.AddField(
            model_name='album',
            name='competition',
            field=models.ForeignKey(blank=True, to='core.Competition', null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='created_by',
            field=models.ForeignKey(related_name='created_album_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='modified_by',
            field=models.ForeignKey(related_name='modified_album_set', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='primary_image',
            field=models.OneToOneField(related_name='primary_album', null=True, blank=True, to='gallery.Photo'),
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together=set([('kind', 'video_id')]),
        ),
    ]
