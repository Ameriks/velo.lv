from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from velo.mixins.models import TimestampMixin
from django.dispatch import receiver
from easy_thumbnails.signals import saved_file
from gallery.tasks import generate_thumbnails

import os

# Todo: Finish gallery. Currently - in progress.

def _get_image_upload_path(instance, filename):
    return os.path.join("gallery", instance.album.folder, filename)


class PhotoNumber(TimestampMixin, models.Model):
    photo = models.ForeignKey('gallery.Photo')
    number = models.ForeignKey('registration.Number')

    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)



class Album(TimestampMixin, models.Model):
    title = models.CharField(max_length=255)

    gallery_date = models.DateField()

    photographer = models.CharField(max_length=255, blank=True)

    folder = models.FilePathField(allow_folders=True, allow_files=False, path='media/gallery/', recursive=True)
    competition = models.ForeignKey('core.Competition', blank=True, null=True)
    description = models.TextField(blank=True)

    primary_image = models.OneToOneField('gallery.Photo', related_name='primary_album', blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-gallery_date', 'photographer', )


class Photo(TimestampMixin, models.Model):
    album = models.ForeignKey(Album)
    description = models.TextField(blank=True)
    image = ThumbnailerImageField(upload_to=_get_image_upload_path, blank=True, max_length=255)

    md5 = models.CharField(max_length=32, blank=True)

    is_featured = models.BooleanField(default=False)

    numbers = models.ManyToManyField('registration.Number', through=PhotoNumber)

    def filename(self):
        return os.path.basename(self.image.name)

    class Meta:
        ordering = ('image', )


@receiver(saved_file)
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    generate_thumbnails(
        model=sender, pk=fieldfile.instance.pk,
        field=fieldfile.field.name)