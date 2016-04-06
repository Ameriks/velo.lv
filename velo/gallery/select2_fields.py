# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

# from django_select2 import AutoModelSelect2MultipleField

from velo.core.models import Competition
from velo.registration.models import Number


class NumberMixin(object):
    max_results = 30
    search_fields = ['number__icontains', ]
    get_empty_results = False

    def prepare_qs_params(self, request, search_term, search_fields):
        distance_id = request.GET.get('distance_id', None)

        if search_term:
            qs = super(NumberMixin, self).prepare_qs_params(request, search_term, search_fields)
        else:
            qs = {'or': [], 'and': {}}
        if distance_id:
            qs['and'].update({'distance_id': distance_id})

        competition_id = request.GET.get('competition_id', None)
        if competition_id:
            competition = Competition.objects.get(id=competition_id)
            qs['and'].update({'distance__competition_id__in': competition.get_ids()})

        return qs


# class PhotoNumberChoices(NumberMixin, AutoModelSelect2MultipleField):
#     queryset = Number.objects.exclude(participant_slug='')
