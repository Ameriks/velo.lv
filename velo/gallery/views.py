# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView
from django.utils.translation import ugettext_lazy as _

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from PIL import Image
import datetime
import uuid

from velo.gallery.forms import AssignNumberForm, VideoSearchForm, AddVideoForm, AddPhotoAlbumForm, GallerySearchForm
from velo.gallery.models import Photo, Album, PhotoNumber, Video
from velo.velo.mixins.views import RequestFormKwargsMixin, SearchMixin, SingleTableViewWithRequest
from velo.gallery.tables import AlbumTable


class AlbumListView(ListView):
    model = Album

    search_form = None

    def get_search_form(self):
        if not self.search_form:
            self.search_form = GallerySearchForm(request=self.request)
        return self.search_form

    def get_context_data(self, **kwargs):
        context = super(AlbumListView, self).get_context_data(**kwargs)
        context.update({'search_form': self.get_search_form()})
        return context

    def get_queryset(self):
        queryset = super(AlbumListView, self).get_queryset()

        queryset = queryset.filter(is_processed=True).filter(is_internal=False)

        if self.get_search_form():
            queryset = self.get_search_form().append_queryset(queryset)

        return queryset


class PhotoListView(ListView):
    model = Photo
    allow_empty = False

    def get_queryset(self):
        queryset = super(PhotoListView, self).get_queryset()
        queryset = queryset.filter(album_id=self.kwargs.get('album_pk')).filter(is_processed=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        context.update({'album': Album.objects.get(id=self.kwargs.get('album_pk'))})
        return context


class AlbumAssignNumberView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = 'gallery/photo_assign_numbers.html'
    permission_required = 'gallery.can_assign_numbers'
    model = Photo

    def get_queryset(self):
        queryset = super(AlbumAssignNumberView, self).get_queryset()
        queryset = queryset.filter(album_id=self.kwargs.get('album_pk'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AlbumAssignNumberView, self).get_context_data(**kwargs)
        context.update({'album': Album.objects.get(id=self.kwargs.get('album_pk'))})

        form = AssignNumberForm(request=self.request, request_kwargs=self.kwargs, object=self.object)
        context.update({'form': form})

        context.update({'next': self.get_next()})
        context.update({'prev': self.get_prev()})

        return context

    def get_next(self):
        next = Photo.objects.filter(album_id=self.kwargs.get('album_pk')).filter(id__gt=self.object.id)
        if next:
            return next[0]
        return False

    def get_prev(self):
        prev = Photo.objects.filter(album_id=self.kwargs.get('album_pk')).filter(id__lt=self.object.id).order_by('-id')
        if prev:
            return prev[0]
        return False

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        numbers = request.POST.getlist('numbers')
        ids = []
        for number in numbers:
            photo, created = PhotoNumber.objects.get_or_create(number_id=number, photo=self.object,
                                                               defaults={'created_by': request.user})
            ids.append(photo.id)
        PhotoNumber.objects.filter(photo=self.object).exclude(id__in=ids).delete()

        action = request.POST.get('action')
        if action == 'next':
            return HttpResponseRedirect(reverse('gallery:photo_number_assign',
                                                kwargs={'album_pk': self.object.album_id, 'pk': self.get_next().id}))
        elif action == 'prev':
            return HttpResponseRedirect(reverse('gallery:photo_number_assign',
                                                kwargs={'album_pk': self.object.album_id, 'pk': self.get_prev().id}))
        else:
            return HttpResponseRedirect(
                reverse('gallery:photo_number_assign', kwargs={'album_pk': self.object.album_id, 'pk': self.object.id}))


class VideoListView(ListView):
    model = Video

    search_form = None

    def get_search_form(self):
        if not self.search_form:
            self.search_form = VideoSearchForm(request=self.request)
        return self.search_form

    def get_context_data(self, **kwargs):
        context = super(VideoListView, self).get_context_data(**kwargs)
        context.update({'search_form': self.get_search_form()})
        return context

    def get_queryset(self):
        queryset = super(VideoListView, self).get_queryset()

        if self.get_search_form():
            queryset = self.get_search_form().append_queryset(queryset)

        if self.request.user.is_superuser or self.request.user.has_perm('gallery.can_see_unpublished_video'):
            pass
        elif self.request.user.is_authenticated():
            queryset = queryset.filter(Q(status=1) | Q(created_by=self.request.user))
        else:
            queryset = queryset.filter(status=1)

        return queryset


class VideoCreateView(RequestFormKwargsMixin, CreateView):
    model = Video
    form_class = AddVideoForm

    def get_success_url(self):
        return reverse('gallery:video')


class PhotoAlbumCreateView(RequestFormKwargsMixin, CreateView):
    model = Album
    form_class = AddPhotoAlbumForm
    template_name = 'gallery/video_form.html'

    def get_success_url(self):
        return reverse('gallery:album')


class AlbumPickListView(SearchMixin, PermissionRequiredMixin, LoginRequiredMixin, SingleTableViewWithRequest):
    model = Album
    table_class = AlbumTable
    permission_required = "gallery.add_photo"
    template_name = 'bootstrap/gallery/album_picklist.html'
    created_instance = None

    def get_context_data(self, **kwargs):
        context = super(AlbumPickListView, self).get_context_data(**kwargs)
        context.update({'created_instance': self.created_instance})
        return context

    def get_queryset(self):
        queryset = super(AlbumPickListView, self).get_queryset()
        queryset = queryset.filter(is_processed=True)
        return queryset

    def post(self, request, *args, **kwargs):

        image = request.FILES.get('image')
        try:
            trial_image = Image.open(image)
            trial_image.verify()
        except IOError:
            messages.error(request, _('Uploaded file is not an image.'))
        except AttributeError:
            messages.error(request, _('Please pick file'))
        else:
            album = Album.objects.filter(is_internal=True).first()
            if not album:
                album = Album.objects.create(title="Internal", is_internal=True,
                                             folder="media/gallery/%s" % str(uuid.uuid4()), is_processed=True,
                                             gallery_date=datetime.date.today())
            self.created_instance = Photo.objects.create(image=image, album=album)

        return super(AlbumPickListView, self).get(request, *args, **kwargs)


class PhotoPickListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Photo
    allow_empty = False
    template_name = 'bootstrap/gallery/photo_picklist.html'
    permission_required = "gallery.add_photo"

    def get_queryset(self):
        queryset = super(PhotoPickListView, self).get_queryset()
        queryset = queryset.filter(album_id=self.kwargs.get('album_pk')).filter(is_processed=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PhotoPickListView, self).get_context_data(**kwargs)
        context.update({'album': Album.objects.get(id=self.kwargs.get('album_pk'))})
        return context
