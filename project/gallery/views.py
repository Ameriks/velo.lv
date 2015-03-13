from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from gallery.forms import AssignNumberForm
from gallery.models import Photo, Album, PhotoNumber


class AlbumListView(ListView):
    model = Album

    def get_queryset(self):
        queryset = super(AlbumListView, self).get_queryset()
        queryset = queryset.select_related('primary_image')
        return queryset


class PhotoListView(ListView):
    model = Photo
    allow_empty = False

    def get_queryset(self):
        queryset = super(PhotoListView, self).get_queryset()
        queryset = queryset.filter(album_id=self.kwargs.get('album_pk'))
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

        form = AssignNumberForm(request=self.request, request_kwargs=self.kwargs)
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
            photo, created = PhotoNumber.objects.get_or_create(number_id=number, photo=self.object, defaults={'created_by': request.user})
            ids.append(photo.id)
        PhotoNumber.objects.filter(photo=self.object).exclude(id__in=ids).delete()

        action = request.POST.get('action')
        if action == 'next':
            return HttpResponseRedirect(reverse('gallery:photo_number_assign', kwargs={'album_pk': self.object.album_id, 'pk': self.get_next().id}))
        elif action == 'prev':
            return HttpResponseRedirect(reverse('gallery:photo_number_assign', kwargs={'album_pk': self.object.album_id, 'pk': self.get_prev().id}))
        else:
            return HttpResponseRedirect(reverse('gallery:photo_number_assign', kwargs={'album_pk': self.object.album_id, 'pk': self.object.id}))

