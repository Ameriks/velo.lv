# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from velo.gallery.views import PhotoListView, AlbumListView, AlbumAssignNumberView, VideoListView, VideoCreateView, \
    PhotoAlbumCreateView, AlbumPickListView, PhotoPickListView

urlpatterns = [
                       url(_(r'^video/$'), VideoListView.as_view(), name='video'),
                       url(_(r'^video/add/$'), VideoCreateView.as_view(), name='video_add'),
                       url(_(r'^$'), AlbumListView.as_view(), name='album'),
                       url(_(r'^add/$'), PhotoAlbumCreateView.as_view(), name='album_add'),
                       url(_(r'^(?P<album_pk>\d+)/$'), PhotoListView.as_view(), name='album'),
                       url(_(r'^(?P<album_pk>\d+)/(?P<pk>\d+)/assign_numbers/$'), AlbumAssignNumberView.as_view(),
                           name='photo_number_assign'),

                       url(_(r'^pick/$'), AlbumPickListView.as_view(), name='album_pick'),
                       url(_(r'^pick/(?P<album_pk>\d+)/$'), PhotoPickListView.as_view(), name='album_pick'),

                      ]
