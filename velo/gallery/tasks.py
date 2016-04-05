# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf import settings

from celery.task import task
from celery.schedules import crontab
from celery.task import periodic_task
from easy_thumbnails.files import generate_all_aliases
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets, OAuth2Credentials
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from subprocess import call
import httplib2
import vimeo
import datetime

from velo.core.tasks import LogErrorsTask
from velo.velo.utils import load_class


@task(base=LogErrorsTask)
def generate_thumbnails(pk, field, model_class=None):
    model = load_class(model_class)
    instance = model._default_manager.get(pk=pk)
    fieldfile = getattr(instance, field)

    # optimize file
    call(["/usr/bin/jpegoptim", fieldfile.path])

    generate_all_aliases(fieldfile, include_global=True)

    try:
        if model.__name__ == 'Photo':
            instance.is_processed = True
            instance.save()

            album = instance.album
            if not album.photo_set.filter(is_processed=False).count():
                album.is_processed = True
                album.save()

    except:
        pass


@task(base=LogErrorsTask)
def get_video_info(_id):
    from velo.gallery.models import Video
    video = Video.objects.get(id=_id)

    new_video =  not video.title

    if video.kind == 1: # youtube
        YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"
        # CLIENT_SECRETS_FILE = "gallery/client_secrets.json"
        # flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
        #   message="Missing cert",
        #   scope=YOUTUBE_READONLY_SCOPE)
        #

        storage = Storage("gallery/youtube-oauth2.json")
        credentials = storage.get()

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
          http=credentials.authorize(httplib2.Http()))

        video_response = youtube.videos().list(
            id=video.video_id,
            part='snippet, statistics'
          ).execute()

        item = video_response.get('items')[0]

        video.title = item.get('snippet').get('title')
        video.channel_title = item.get('snippet').get('channelTitle')
        video.published_at = item.get('snippet').get('publishedAt')
        video.view_count = int(item.get('statistics').get('viewCount'))

        thumbs = item.get('snippet').get('thumbnails')
        standard_thumb = thumbs.get('standard', None)
        if not standard_thumb:
            standard_thumb = thumbs.get('high', None)
        if not standard_thumb:
            standard_thumb = thumbs.get('default', None)

        maxres_thumb = thumbs.get('maxres', None)
        if not maxres_thumb:
            maxres_thumb = thumbs.get('high', None)
        if not maxres_thumb:
            maxres_thumb = thumbs.get('default', None)

        video.image = standard_thumb.get('url')
        video.image_maxres = maxres_thumb.get('url')

        if new_video:
            if video.channel_title == 'wwwvelolv':
                video.is_agency_video = True
                video.status = 1
    elif video.kind == 2: # vimeo
        v = vimeo.VimeoClient(token=settings.VIMEO_TOKEN, key=settings.VIMEO_KEY, secret=settings.VIMEO_SECRET)
        video_response = v.get('/videos/%s' % video.video_id)
        if video_response.status_code == 200:
            item = video_response.json()

            video.title = item.get('name')
            video.channel_title = item.get('user').get('name')
            video.published_at = item.get('created_time')
            video.view_count = int(item.get('stats').get('plays'))

            video.image_maxres = item.get('pictures').get('sizes')[-1].get('link')
            video.image = item.get('pictures').get('sizes')[-2].get('link')

            if new_video:
                if video.channel_title == 'www.velo.lv':
                    video.is_agency_video = True
                    video.status = 1

    video.save()


@periodic_task(run_every=crontab(minute="3", hour='4'))
def refresh_view_count(_id=None):
    from velo.gallery.models import Video
    videos = Video.objects.filter(status=1).order_by('-id')

    if _id:
        videos = videos.filter(id=_id)

    if not datetime.date.today().day == 1:
        videos = videos[:20]  # Daily we update only last 20 video counters, but once in month we update all.

    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    storage = Storage("gallery/youtube-oauth2.json")
    credentials = storage.get()

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))

    v = vimeo.VimeoClient(token=settings.VIMEO_TOKEN, key=settings.VIMEO_KEY, secret=settings.VIMEO_SECRET)

    for video in videos:
        if video.kind == 1: # youtube
            video_response = youtube.videos().list(
                id=video.video_id,
                part='statistics'
              ).execute()
            item = video_response.get('items')[0]
            video.view_count = int(item.get('statistics').get('viewCount'))

            # TODO: Add YOUTUBE VIDEO Availability checker

        elif video.kind == 2: # vimeo
            video_response = v.get('/videos/%s' % video.video_id)
            if video_response.status_code == 200:
                item = video_response.json()
                video.view_count = int(item.get('stats').get('plays'))
                if item.get('status') != 'available':
                    video.status = 0
            elif video_response.status_code == 404:
                video.status = 0
        video.save()
