# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from functools import partial
from urllib.parse import urlparse, parse_qs

import os
import hashlib

from velo.gallery.models import Album, Photo
from velo.gallery.tasks import generate_thumbnails


def youtube_video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


def sync_album(album_id):
    album = Album.objects.get(id=album_id)
    for root, _, files in os.walk(album.folder):
        for f in sorted(files):
            if f[-3:].lower() != 'jpg' and f[-4:].lower() != 'jpeg':
                continue
            fullpath = os.path.join(root, f)
            md5 = md5sum(fullpath)
            photo, created = album.photo_set.get_or_create(md5=md5, defaults={'image': fullpath[11:]})

            if not album.primary_image:
                album.primary_image = photo
                album.save()

            if not created:
                photo.image = fullpath[6:]
                photo.save()
            else:
                generate_thumbnails.delay(photo.id, 'image', model_class='gallery.models.Photo')

