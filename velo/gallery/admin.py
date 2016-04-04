from django.contrib import admin

# Register your models here.
from gallery.models import Album, Photo

admin.site.register(Album)
admin.site.register(Photo)
