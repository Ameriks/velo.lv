# coding=utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from gallery.views import PhotoListView, AlbumListView, AlbumAssignNumberView, VideoListView, VideoCreateView, \
    PhotoAlbumCreateView


urlpatterns = patterns('',
                       url(_(r'^video/$'), VideoListView.as_view(), name='video'),
                       url(_(r'^video/add/$'), VideoCreateView.as_view(), name='video_add'),
                       url(_(r'^$'), AlbumListView.as_view(), name='album'),
                       url(_(r'^add/$'), PhotoAlbumCreateView.as_view(), name='album_add'),
                       url(_(r'^(?P<album_pk>\d+)/$'), PhotoListView.as_view(), name='album'),
                       url(_(r'^(?P<album_pk>\d+)/(?P<pk>\d+)/assign_numbers/$'), AlbumAssignNumberView.as_view(), name='photo_number_assign'),
)