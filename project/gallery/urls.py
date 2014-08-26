# coding=utf-8
from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from gallery.views import PhotoListView, AlbumListView


urlpatterns = patterns('',
                       url(_(r'^$'), AlbumListView.as_view(), name='album'),
                       url(_(r'^(?P<album_pk>\d+)/$'), PhotoListView.as_view(), name='album'),
)