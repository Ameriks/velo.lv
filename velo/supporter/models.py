# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.fields import ThumbnailerImageField

import os
import uuid


def _get_logo_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("supporter", "%02d_%s%s" % (instance.supporter_id, filename, ext))


class Supporter(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    is_agency_supporter = models.BooleanField(default=False)
    supporter_kind = models.CharField(max_length=100, blank=True)
    ordering = models.IntegerField(default=0, db_index=True)
    default_logo = models.ForeignKey('supporter.Logo', blank=True, null=True, on_delete=models.SET_NULL, related_name='+', )
    default_svg = models.ForeignKey('supporter.Logo', blank=True, null=True, on_delete=models.SET_NULL, related_name='+', )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('ordering', )


class Logo(models.Model):
    supporter = models.ForeignKey(Supporter)
    svg_logo = models.FileField(upload_to=_get_logo_upload_path, blank=True, )
    image = ThumbnailerImageField(upload_to=_get_logo_upload_path, blank=True, width_field='width', height_field='height')
    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)

    def __str__(self):
        if self.image:
            return self.image.url
        elif self.svg_logo:
            return self.svg_logo.url
        else:
            return "-"


class CompetitionSupporter(models.Model):
    SUPPORT_LEVELS = (
        (10, _('Supporter')),

        (30, _('Partner')),
        (40, _('Technical Partner')),

        (70, _('Sponsor')),
        (90, _('General Sponsor'))
    )
    competition = models.ForeignKey('core.Competition')
    supporter = models.ForeignKey(Supporter)
    logo = models.ForeignKey(Logo, blank=True, null=True)
    support_level = models.PositiveSmallIntegerField(choices=SUPPORT_LEVELS)

    label = models.CharField(max_length=100, blank=True)

    ordering = models.IntegerField(default=0)
