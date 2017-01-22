import uuid
import os
import zipfile

import environ
from django.conf import settings
from django.contrib import admin
from django import forms
from django.core.cache import cache
from django.utils import timezone
from slugify import slugify

from .models import Banner


class BannerForm(forms.ModelForm):
    zip_file = forms.FileField(label='Zip File', help_text='ZIP File containing html5 banner', required=False)

    class Meta:
        model = Banner
        fields = ("status", "title", "competition", "location", "width", "height", "kind", "converted", "banner_url", "banner", "url", "ordering", "show_start", "show_end", "language")

    def save(self, commit=True):
        if self.cleaned_data.get('zip_file'):
            year = timezone.now().year
            gallery_folder = slugify('%s-%s' % (year, uuid.uuid4()))
            gallery_path = str(environ.Path(settings.MEDIA_ROOT).path('adverts').path('banner').path(gallery_folder))
            if not os.path.exists(gallery_path):
                os.makedirs(gallery_path)

            self.instance.banner_url = '/media/adverts/banner/%s/index.html' % gallery_folder

            zip_file = self.cleaned_data.get('zip_file')

            with zipfile.ZipFile(zip_file, "r") as z:
                z.extractall(gallery_path)

        for code, lang in settings.LANGUAGES:
            cache.delete("banners_news_%s" % code)
            cache.delete("banners_calendar_%s" % code)
            cache.delete("banners_top_%s" % code)
            cache.delete("banners_gallery_%s" % code)

        return super().save(commit)


class BannerAdmin(admin.ModelAdmin):
    list_filter = ('competition', 'status')
    list_display = ('title', 'status', 'competition', 'location', 'kind', 'url', 'view_count', 'click_count')
    form = BannerForm


admin.site.register(Banner, BannerAdmin)
