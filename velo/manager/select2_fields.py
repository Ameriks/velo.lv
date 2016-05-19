# from django.http import Http404
# from django.template.defaultfilters import slugify
# from django.utils import timezone
# from django.utils.encoding import smart_unicode
# from django.utils.timezone import get_current_timezone
# from django_select2 import AutoModelSelect2Field, AutoModelSelect2MultipleField
# from velo.core.models import User, Distance, Competition
# from velo.registration.models import Number, Participant
# from velo.utils import load_class
# import datetime
#
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from slugify import slugify

from velo.core.models import Distance, Competition, User
from velo.registration.models import Number, Participant
from velo.velo.utils import load_class


class NumberMixin(object):
    max_results = 30
    search_fields = ['number__icontains', ]
    get_empty_results = True

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super().build_attrs(extra_attrs=extra_attrs, **kwargs)
        attrs['class'] += '-number'
        return attrs

    def extra_data_from_instance(self, obj, context=None):
        return {
            'distance_id': obj.distance_id,
        }

    def filter_queryset(self, term, queryset=None, context=None):
        if queryset is None:
            queryset = self.get_queryset()

        distance_id = gender = bday = None
        if context:
            competition_id, distance_id, gender, bday = context.split("~~~")
        else:
            # Something wrong. We shouldn't show any numbers
            competition_id = -1

        group = None

        if distance_id:
            distance = Distance.objects.get(id=distance_id)
            class_ = load_class(distance.competition.processing_class)
            processing_class = class_(distance.competition.id)
            group = processing_class.get_group_for_number_search(distance.id, gender, bday)

        queryset = queryset.filter(participant_slug='')

        if competition_id:
            competition = Competition.objects.get(id=competition_id)
            queryset = queryset.filter(distance__competition_id__in=competition.get_ids())

        if distance_id:
            queryset = queryset.filter(distance_id=distance_id)
        if group:
            queryset = queryset.filter(group=group)

        if term == '':
            return queryset
        else:
            return super().filter_queryset(term, queryset)


class NumberChoice(NumberMixin, ModelSelect2Widget):
    model = Number


class NumberChoices(NumberMixin, ModelSelect2MultipleWidget):
    model = Number


class NumberAllChoices(ModelSelect2Widget):
    model = Number
    search_fields = ['number__icontains', ]
    get_empty_results = False

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super().build_attrs(extra_attrs=extra_attrs, **kwargs)
        attrs['class'] += '-number'
        return attrs

    def filter_queryset(self, term, queryset=None, context=None):
        if queryset is None:
            queryset = self.get_queryset()

        if context:
            competition_id, distance_id, gender, bday = context.split("~~~")
        else:
            # Something wrong. We shouldn't show any numbers
            competition_id = -1

        if competition_id:
            competition = Competition.objects.get(id=competition_id)
            queryset = queryset.filter(distance__competition_id__in=competition.get_ids())

        if term == '':
            return queryset
        else:
            return super().filter_queryset(term, queryset)



class UserChoices(ModelSelect2Widget):
    max_results = 10
    model = User
    search_fields = ['first_name__icontains', 'last_name__icontains', 'ssn__icontains', 'full_name__icontains', ]
    get_empty_results = False

    def label_from_instance(self, obj):
        return '%s (id:%i) %s' % (str(obj), obj.id, obj.last_login.date())


class ParticipantChoices(ModelSelect2Widget):
    max_results = 10
    model = Participant
    search_fields = ['slug__icontains', ]
    get_empty_results = False

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super().build_attrs(extra_attrs=extra_attrs, **kwargs)
        attrs['class'] += '-number'
        return attrs

    def filter_queryset(self, term, queryset=None, context=None):
        if queryset is None:
            queryset = self.get_queryset()

        if context:
            competition_id, distance_id, gender, bday = context.split("~~~")
        else:
            # Something wrong. We shouldn't show any numbers
            competition_id = -1

        if competition_id:
            competition = Competition.objects.get(id=competition_id)
            queryset = queryset.filter(distance__competition_id__in=competition.get_ids())

        if term == '':
            return queryset
        else:
            search_term = slugify(term).upper()
            return super().filter_queryset(search_term, queryset)
