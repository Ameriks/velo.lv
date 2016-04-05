# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import os
import uuid

from velo.velo.mixins.models import StatusMixin


def get_banner_upload(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("adverts", "banner", "%s%s" % (filename, ext))


@python_2_unicode_compatible
class FlashBanner(StatusMixin, models.Model):
    BANNER_LOCATIONS = (
        ('left-side', 'left-side'),
    )
    title = models.CharField(max_length=50, blank=True)
    banner = models.FileField(upload_to=get_banner_upload)
    competition = models.ForeignKey('core.Competition')
    location = models.CharField(max_length=20, choices=BANNER_LOCATIONS)

    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    converted = models.TextField(blank=True, help_text='Convert flash to html5 in https://www.google.com/doubleclick/studio/swiffy/')

    url = models.URLField(blank=True)

    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ('ordering', )

    def __str__(self):
        return self.title
