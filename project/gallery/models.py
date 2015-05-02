from django.conf import settings
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from velo.mixins.models import TimestampMixin, StatusMixin
from django.dispatch import receiver
from easy_thumbnails.signals import saved_file
from gallery.tasks import generate_thumbnails, get_video_info

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


class Video(StatusMixin, TimestampMixin, models.Model):
    VIDEO_KIND = (
        (1, 'YouTube'),
        (2, 'Vimeo'),
    )
    kind = models.PositiveSmallIntegerField(default=1, choices=VIDEO_KIND)
    video_id = models.CharField(max_length=50)

    title = models.CharField(max_length=255, blank=True)
    published_at = models.DateTimeField(blank=True, null=True)
    channel_title = models.CharField(max_length=255, blank=True)

    competition = models.ForeignKey('core.Competition', blank=True, null=True)

    view_count = models.IntegerField(default=0)

    is_featured = models.BooleanField(default=False)
    is_agency_video = models.BooleanField(default=False)

    ordering = models.IntegerField(default=0)

    image_maxres = models.URLField(blank=True)
    image = models.URLField(blank=True)

    class Meta:
        ordering = ('is_featured', 'ordering', 'title')
        unique_together = (('kind', 'video_id'), )
        permissions = (
            ("can_see_unpublished_video", "Can see unpublished video"),
        )

    @property
    def url_embed(self):
        if self.kind == 1:
            return 'https://www.youtube.com/embed/%s' % self.video_id
        elif self.kind == 2:
            return 'https://player.vimeo.com/video/%s' % self.video_id

    def save(self, *args, **kwargs):
        new_record = not self.id
        obj = super(Video, self).save(*args, **kwargs)

        if new_record and self.id:
            get_video_info.delay(self.id)

        return obj



class Album(TimestampMixin, models.Model):
    title = models.CharField(max_length=255)

    gallery_date = models.DateField()

    photographer = models.CharField(max_length=255, blank=True)

    folder = models.FilePathField(allow_folders=True, allow_files=False, path='media/gallery/', recursive=True)
    competition = models.ForeignKey('core.Competition', blank=True, null=True)
    description = models.TextField(blank=True)

    is_processed = models.BooleanField(default=False)  # Are thumbnails created?
    is_internal = models.BooleanField(default=False)  # For images to be used in news/front pages. etc.

    primary_image = models.OneToOneField('gallery.Photo', related_name='primary_album', blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-gallery_date', '-id', )


class Photo(TimestampMixin, models.Model):
    album = models.ForeignKey(Album)
    description = models.TextField(blank=True)
    image = ThumbnailerImageField(upload_to=_get_image_upload_path, blank=True, max_length=255)

    md5 = models.CharField(max_length=32, blank=True)

    is_featured = models.BooleanField(default=False)

    is_numbered = models.BooleanField(default=False)  # Are numbers added to this picture?
    is_processed = models.BooleanField(default=False)  # Are thumbnails generated?

    numbers = models.ManyToManyField('registration.Number', through=PhotoNumber)

    is_vertical = models.NullBooleanField(default=None)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    def filename(self):
        return os.path.basename(self.image.name)

    def save(self, *args, **kwargs):
        if not self.is_vertical:
            self.is_vertical = True
            if self.image.width > self.image.height:
                self.is_vertical = False

        if not self.width or not self.height:
            variable = 1000
            if self.is_vertical:
                self.height = variable if self.image.height > variable else self.image.height
                self.width = (self.image.width * self.height) / self.image.height
            else:
                self.width = variable if self.image.width > variable else self.image.width
                self.height = (self.image.height * self.width) / self.image.width

        return super(Photo, self).save(*args, **kwargs)


    class Meta:
        ordering = ('image', )
        permissions = (
            ("can_assign_numbers", "Can assign numbers"),
        )

@receiver(saved_file)
def generate_thumbnails_async(sender, fieldfile, **kwargs):
    generate_thumbnails(
        model=sender, pk=fieldfile.instance.pk,
        field=fieldfile.field.name)