import datetime
import os
import uuid

from django.db import models
from django.utils import timezone
from django.conf import settings
from model_utils import Choices

from velo.velo.mixins.models import StatusMixin


def get_banner_upload(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("adverts", "banner", "%s%s" % (filename, ext))


def _years_ahead():
    return timezone.now() + datetime.timedelta(days=5*365)


class Banner(StatusMixin, models.Model):
    LANGUAGES = (('', '*'),) + settings.LANGUAGES
    BANNER_LOCATIONS = Choices(
        (10, 'top', 'TOP'),
        (20, 'gallery', 'Gallery'),
        (30, 'gallery_side', 'Gallery Side'),
        (40, 'news', 'News Side'),
        (50, 'calendar', 'Calendar Side'),)

    KIND = Choices(
        (10, 'show_html', 'Show HTML'),
        (20, 'show_url', 'Show URL'),
        (30, 'show_upload_img', 'Show Upload Img'),)

    title = models.CharField(max_length=50, blank=True)

    competition = models.ForeignKey('core.Competition', blank=True, null=True)
    location = models.SmallIntegerField(choices=BANNER_LOCATIONS, default=BANNER_LOCATIONS.top)

    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    kind = models.PositiveSmallIntegerField(choices=KIND, default=KIND.show_html)
    converted = models.TextField(blank=True, help_text='Convert flash to html5 in https://www.google.com/doubleclick/studio/swiffy/')
    banner_url = models.CharField(max_length=200, blank=True, help_text='If URL to banner is provided, then enter it here')
    banner = models.ImageField(upload_to=get_banner_upload, help_text='If image banner is provided, upload it here', blank=True)

    url = models.URLField(blank=True)

    ordering = models.IntegerField(default=0)

    view_count = models.IntegerField(default=0, editable=False)
    click_count = models.IntegerField(default=0, editable=False)

    show_start = models.DateTimeField(default=timezone.now)
    show_end = models.DateTimeField(default=_years_ahead)

    language = models.CharField(max_length=10, choices=LANGUAGES, default='', blank=True)

    class Meta:
        ordering = ('ordering', )

    def __str__(self):
        return self.title
