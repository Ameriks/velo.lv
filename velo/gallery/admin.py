# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import admin

from velo.gallery.models import Album, Photo

admin.site.register(Album)
admin.site.register(Photo)
