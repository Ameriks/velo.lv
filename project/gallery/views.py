from django.views.generic import ListView
from gallery.models import Photo, Album



class AlbumListView(ListView):
    model = Album


class PhotoListView(ListView):
    model = Photo

    def get_queryset(self):
        queryset = super(PhotoListView, self).get_queryset()
        queryset = queryset.filter(album_id=self.kwargs.get('album_pk'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        context.update({'album': Album.objects.get(id=self.kwargs.get('album_pk'))})
        return context