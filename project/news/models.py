from django.db import models, ProgrammingError
from velo.mixins.models import StatusMixin
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