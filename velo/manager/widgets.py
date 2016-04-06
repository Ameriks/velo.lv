# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.encoding import force_text
from django.utils.html import format_html

from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from velo.gallery.models import Photo


class PhotoPickWidget(TextInput):
    input_type = 'text'

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_type = attrs.pop('type', self.input_type)
        super(TextInput, self).__init__(attrs)


    def render(self, name, value, attrs=None):

        if value is None:
            value = ''
            photo_src = ''
        else:
            photo = Photo.objects.get(id=value)
            photo_src = thumbnail_url(photo.image, 'img')

        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(value))

        if not photo_src:
            photo_src = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="

        final_attrs.update({'type': 'hidden'})

        return format_html('<div class="row"><div class="col-sm-6"><img class="img-responsive" src="{0}" id="id_image_img" /></div><div class="col-sm-6"><button class="btn btn-primary" type="button" onclick="openGalleryPopup();">Pick image</button><input{1} /></div></div>', photo_src, flatatt(final_attrs))
