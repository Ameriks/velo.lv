# coding=utf-8
from __future__ import unicode_literals
from crispy_forms.bootstrap import StrictButton, Tab, TabHolder
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div
from django import forms
from django_select2 import AutoHeavySelect2MultipleWidget
from django_select2.util import JSFunctionInContext
from core.models import Competition
from gallery.select2_fields import PhotoNumberChoices
from velo.mixins.forms import RequestKwargModelFormMixin
from django.utils.translation import ugettext_lazy as _


class AssignNumberForm(RequestKwargModelFormMixin, forms.Form):

    numbers = PhotoNumberChoices(required=False, widget=AutoHeavySelect2MultipleWidget(select2_options={
        'ajax': {
            'dataType': 'json',
            'quietMillis': 100,
            'data': JSFunctionInContext('get_number_params'),
            'results': JSFunctionInContext('django_select2.process_results'),
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
                    css_class='col-sm-3',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span>', css_class="btn-primary search-button-margin", type="submit"),
                        css_class="buttons",
                    ),
                    css_class='col-sm-1',
                ),
        )