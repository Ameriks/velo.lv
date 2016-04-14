# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from base64 import b32encode
from hashlib import sha1
from random import random
from ckeditor.fields import RichTextField
from slugify import slugify

from velo.velo.mixins.models import StatusMixin, TimestampMixin


def notification_slug():
    pk = None
    bad_pk = True
    while bad_pk:
        pk = b32encode(sha1(str(random())).digest()).lower()[:6]
        bad_pk = False
        if not bad_pk:
            try:
                Notification.objects.get(slug=pk)
                bad_pk = True
            except Notification.DoesNotExist:
                bad_pk = False
    return pk


@python_2_unicode_compatible
class Notification(StatusMixin, models.Model):
    slug = models.CharField(max_length=6, default=notification_slug)
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.title


class NewsManagerPublished(models.Manager):
    def published(self, competition_ids=None):
        queryset = super(NewsManagerPublished, self).get_queryset().filter(published_on__lte=timezone.now()).order_by('-published_on')
        if competition_ids:
            queryset = queryset.filter(competition_id__in=competition_ids)
        return queryset


@python_2_unicode_compatible
class News(StatusMixin, TimestampMixin, models.Model):

    LANGUAGE_CHOICES = (("lv", "Latviski"), ("en", "English"))

    language = models.CharField("Language", max_length=20, db_index=True, default='lv', choices=LANGUAGE_CHOICES)

    title = models.CharField("Title", max_length=255)
    slug = models.SlugField("Slug", unique=True)
    image = models.ForeignKey('gallery.Photo', blank=True, null=True)
    competition = models.ForeignKey('core.Competition', blank=True, null=True, limit_choices_to={'level__lte': 1})
    published_on = models.DateTimeField(default=timezone.now)

    intro_content = RichTextField()
    content = RichTextField(blank=True)

    tmp_string = models.CharField(max_length=255, blank=True)

    legacy_id = models.IntegerField(null=True, blank=True)

    objects = NewsManagerPublished()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.competition:
            return reverse('news:news', args=[self.competition_id, self.slug])
        return reverse('news:news', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super(News, self).save(*args, **kwargs)


class Comment(StatusMixin, TimestampMixin, models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    legacy_id = models.IntegerField(null=True, blank=True)
