# coding=utf-8
from __future__ import unicode_literals
import re
from crispy_forms.bootstrap import StrictButton, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div, HTML
import datetime
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django_select2 import AutoHeavySelect2MultipleWidget
import os
from core.models import Competition
from gallery.models import Video, Photo, Album
from gallery.select2_fields import PhotoNumberChoices
from gallery.utils import youtube_video_id, sync_album
from velo.mixins.forms import RequestKwargModelFormMixin
from django.utils.translation import ugettext_lazy as _
import zipfile


class AssignNumberForm(RequestKwargModelFormMixin, forms.Form):

    numbers = PhotoNumberChoices(required=False, widget=AutoHeavySelect2MultipleWidget(select2_options={
        'ajax': {
            'dataType': 'json',
            'quietMillis': 100,
            'data': '*START*django_select2.runInContextHelper(get_number_params, selector)*END*',
            'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
        },
        "minimumResultsForSearch": 0,
        "minimumInputLength": 0,
        "closeOnSelect": True
    }))

    def __init__(self, *args, **kwargs):

        self.object = kwargs.pop('object', None)
        super(AssignNumberForm, self).__init__(*args, **kwargs)

        numbers = self.object.numbers.all()
        val = []
        for number in numbers:
            val.append(number.id)

        self.fields['numbers'].initial = val


class AddVideoForm(RequestKwargModelFormMixin, forms.ModelForm):
    link = forms.URLField(label=_('Link'), help_text=_('Youtube or Vimeo link'), required=True)
    class Meta:
        model = Video
        fields = ['competition', ]

    def __init__(self, *args, **kwargs):
        super(AddVideoForm, self).__init__(*args, **kwargs)
        competitions = Competition.objects.filter(competition_date__year=datetime.datetime.now().year)
        self.fields['competition'].choices = ((obj.id, obj.get_full_name) for obj in competitions)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
                    'competition',
                    'link',
                        StrictButton('Add', css_class="btn-primary search-button-margin", type="submit"),
        )

    def clean_link(self):
        link = self.cleaned_data.get('link')
        if "youtube" not in link and "youtu.be" not in link and "vimeo" not in link:
            raise forms.ValidationError(_("You can add only youtube and vimeo videos."),)

        if "youtube" in link or "youtu.be" in link:
            if not youtube_video_id(link):
                raise forms.ValidationError(_("Incorrect youtube link."),)
        else:
            video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)
            if not video_id:
                raise forms.ValidationError(_("Incorrect vimeo link."),)

        return link


    def save(self, commit=True):
        link = self.cleaned_data.get('link')
        if "youtube" in link or "youtu.be" in link:
            self.instance.kind = 1
            self.instance.video_id = youtube_video_id(link)
        else:
            self.instance.kind = 2
            self.instance.video_id = re.search(r'^((http|https)://)?(www\.)?(vimeo\.com/)?(\d+)', link).group(5)

        if self.request and self.request.user.is_authenticated():
            self.instance.created_by = self.request.user
            self.instance.modified_by = self.request.user

        messages.info(self.request, _('Video successfully added. Video must be approved by agency to be available to public.'))

        return super(AddVideoForm, self).save(commit)



class AddPhotoAlbumForm(RequestKwargModelFormMixin, forms.ModelForm):
    zip_file = forms.FileField(label=_('Zip File'), help_text=_('ZIP File containing photos'), required=True)
    class Meta:
        model = Album
        fields = ['title', 'gallery_date', 'photographer', 'competition', 'description']

    def __init__(self, *args, **kwargs):
        super(AddPhotoAlbumForm, self).__init__(*args, **kwargs)
        competitions = Competition.objects.filter(competition_date__year=datetime.datetime.now().year)
        self.fields['competition'].choices = ((obj.id, obj.get_full_name) for obj in competitions)

        if self.request.user.is_authenticated():
            self.fields['photographer'].initial = self.request.user.full_name

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
                    Row(
                        Div(
                            'title',
                            css_class='col-sm-6'
                        ),
                        Div(
                            'photographer',
                            css_class='col-sm-6'
                        ),
                    ),
                    Row(
                        Div(
                            'competition',
                            css_class='col-sm-6'
                        ),
                        Div(
                            'gallery_date',
                            css_class='col-sm-6'
                        ),
                    ),
                    'description',
                    'zip_file',
                        StrictButton('Add', css_class="btn-primary search-button-margin", type="submit"),
        )

    def get_members(self, zip):
        parts = []
        for name in zip.namelist():
            name = name.decode('utf-8')
            if name.startswith('__MACOSX'):
                continue
            if not name.endswith('/'):
                parts.append(name.split('/')[:-1])

        prefix = os.path.commonprefix(parts) or ''
        if prefix:
            prefix = '/'.join(prefix) + '/'
        offset = len(prefix)
        for zipinfo in zip.infolist():
            name = zipinfo.filename.decode('utf-8')

            if name.startswith('__MACOSX'):
                continue

            ext = os.path.splitext(name)[1].lower()
            if len(name) > offset and ext in ('.jpg', '.jpeg'):
                zipinfo.filename = "%s%s" % (slugify(name[offset:-len(ext)]), ext)
                yield zipinfo


    def save(self, commit=True):
        obj = super(AddPhotoAlbumForm, self).save(commit)

        year = obj.gallery_date.year
        gallery_folder = slugify('%s-%s' % (obj.id, obj.title))
        gallery_path = settings.MEDIA_ROOT.child('gallery').child(str(year)).child(gallery_folder)
        if not os.path.exists(gallery_path):
            os.makedirs(gallery_path)

        obj.folder = 'media/gallery/%i/%s' % (year, gallery_folder)
        obj.save()

        zip_file = self.cleaned_data.get('zip_file')

        with zipfile.ZipFile(zip_file.temporary_file_path(), "r") as z:
            z.extractall(gallery_path, self.get_members(z))

        sync_album(obj.id)

        return obj





class VideoSearchForm(RequestKwargModelFormMixin, forms.Form):
    competition = forms.ChoiceField(choices=(), required=False, label=_('Competition'))
    show = forms.ChoiceField(choices=(), required=False, label=_('Show'))
    search = forms.CharField(required=False, label=_('Search'))

    sort = forms.CharField(required=False, widget=forms.HiddenInput)

    def append_queryset(self, queryset):
        query_attrs = self.fields

        if query_attrs.get('competition').initial:
            competition = Competition.objects.get(id=query_attrs.get('competition').initial)
            ids = competition.get_all_children_ids() + (competition.id, )
            queryset = queryset.filter(competition_id__in=ids)

        if query_attrs.get('show').initial:
            queryset = queryset.filter(is_agency_video=query_attrs.get('show').initial)

        if query_attrs.get('search').initial:
            queryset = queryset.filter(title__icontains=query_attrs.get('search').initial)

        if query_attrs.get('sort').initial:
            queryset = queryset.order_by(*query_attrs.get('sort').initial.split(','))

        queryset = queryset.distinct()

        return queryset

    def __init__(self, *args, **kwargs):
        super(VideoSearchForm, self).__init__(*args, **kwargs)


        competitions = Competition.objects.exclude(video=None)
        self.fields['competition'].choices = [('', '------')] + [(obj.id, obj.get_full_name) for obj in competitions]

        self.fields['show'].choices = [('', '------'), (1, _('Show only agency videos')), (0, _('Show only user videos'))]



        self.fields['sort'].initial = self.request.GET.get('sort', '-published_at')

        self.fields['search'].initial = self.request.GET.get('search', '')
        self.fields['competition'].initial = self.request.GET.get('competition', '')
        self.fields['show'].initial = self.request.GET.get('show', '')

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
                Div(
                    'show',
                    css_class='col-sm-2 hidden-xs',
                ),
                Div(
                    'competition',
                    css_class='col-sm-2 hidden-xs',
                ),
                Div(
                    'search',
                    'sort',
                    css_class='col-sm-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span>', css_class="btn-primary search-button-margin", type="submit"),
                        HTML('<a href="%s" class="btn btn-primary search-button-margin"><i class="glyphicon glyphicon-plus"></i></a>' % reverse('gallery:video_add')),
                        css_class="buttons pull-right",
                    ),
                    css_class='col-sm-2',
                ),
        )