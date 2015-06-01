from django.db import models, ProgrammingError
from django.utils import timezone
from velo.mixins.models import StatusMixin, TimestampMixin
from base64 import b32encode
from hashlib import sha1
from random import random

def notification_slug():
    pk = None
    rude = ('lol',)
    bad_pk = True
    while bad_pk:
        pk = b32encode(sha1(str(random())).digest()).lower()[:6]
        bad_pk = False
        for rw in rude:
            if pk.find(rw) >= 0: bad_pk = True

        if not bad_pk:
            try:
                Notification.objects.get(slug=pk)
                bad_pk = True
            except Notification.DoesNotExist:
                bad_pk = False
            except ProgrammingError:
                print 'Migrations should be run'
                bad_pk = False
    return pk


class Notification(StatusMixin, models.Model):
    slug = models.CharField(max_length=6, default=notification_slug)
    title = models.CharField(max_length=255)
    body = models.TextField()

    def __unicode__(self):
        return self.title


class News(StatusMixin, TimestampMixin, models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ForeignKey('gallery.Photo', blank=True, null=True)
    competition = models.ForeignKey('core.Competition', blank=True, null=True)
    published_on = models.DateTimeField(default=timezone.now)

    intro_content = models.TextField()
    content = models.TextField(blank=True)

    tmp_string = models.CharField(max_length=255, blank=True)

    legacy_id = models.IntegerField(null=True, blank=True)


class Comment(StatusMixin, TimestampMixin, models.Model):
    news = models.ForeignKey(News)
    content = models.TextField()

    legacy_id = models.IntegerField(null=True, blank=True)