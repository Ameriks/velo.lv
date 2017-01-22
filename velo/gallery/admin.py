from django import forms
from django.contrib import admin

from .models import Album, Photo, Video
from .utils import youtube_video_id
import re


class VideoAddForm(forms.ModelForm):
    link = forms.URLField(label='Link', help_text='Youtube or Vimeo link', required=True)

    class Meta:
        model = Video
        fields = ("competition", )

    def clean_link(self):
        link = self.cleaned_data.get('link')
        if "youtube" not in link and "youtu.be" not in link and "vimeo" not in link:
            raise forms.ValidationError(_("You can add only youtube and vimeo videos."), )

        if "youtube" in link or "youtu.be" in link:
            if not youtube_video_id(link):
                raise forms.ValidationError("Incorrect youtube link.", )
        else:
            video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)
            if not video_id:
                raise forms.ValidationError("Incorrect vimeo link.", )

        return link

    def save(self, commit=True):
        link = self.cleaned_data.get('link')
        if "youtube" in link or "youtu.be" in link:
            self.instance.kind = 1
            self.instance.video_id = youtube_video_id(link)
        else:
            self.instance.kind = 2
            self.instance.video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)

        return super().save(commit)


class VideoAdmin(admin.ModelAdmin):
    # form = StaticPageForm
    add_form = VideoAddForm
    fieldsets = (
        (None, {'fields': ('status', 'kind', 'video_id', 'title', 'channel_title', 'published_at', 'competition')}),
        ('Advanced options', {'classes': ('collapse',), 'fields': ('view_count', 'is_featured', 'is_agency_video', 'ordering', 'image_maxres', 'image')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('competition', 'link'),
        }),
    )
    list_display = ('id', 'title', 'competition', 'kind', 'video_id', 'status', 'is_featured', 'is_agency_video')
    list_filter = ('status', 'is_agency_video', 'competition', 'is_featured', 'kind')
    search_fields = ('title', )
    ordering = ('-id', )

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)


admin.site.register(Album)
admin.site.register(Photo)
admin.site.register(Video, VideoAdmin)
