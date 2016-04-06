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
#
# class NumberMixin(object):
#     max_results = 30
#     search_fields = ['number__icontains', ]
#     get_empty_results = True
#
#     def extra_data_from_instance(self, obj):
#         return {
#             'distance_id': obj.distance_id,
#         }
#
#     def prepare_qs_params(self, request, search_term, search_fields):
#         distance_id = request.GET.get('distance_id', None)
#         group = None
#         if distance_id:
#             distance = Distance.objects.get(id=request.GET.get('distance_id'))
#             class_ = load_class(distance.competition.processing_class)
#             processing_class = class_(distance.competition.id)
#             group = processing_class.get_group_for_number_search(distance.id, request.GET.get('gender', ''), request.GET.get('birthday', None))
#
#         if search_term:
#             qs = super(NumberMixin, self).prepare_qs_params(request, search_term, search_fields)
#         else:
#             qs = {'or': [], 'and': {}}
#         qs['and'].update({'participant_slug': ''})
#         if distance_id:
#             qs['and'].update({'distance_id': distance_id})
#         if group:
#             qs['and'].update({'group': group})
#
#         competition_id = request.GET.get('competition_id', None)
#         if competition_id:
#             competition = Competition.objects.get(id=competition_id)
#             qs['and'].update({'distance__competition_id__in': competition.get_ids()})
#
#         return qs
#
#
# class NumberChoice(NumberMixin, AutoModelSelect2Field):
#     queryset = Number.objects.all()
#
#
# class NumberChoices(NumberMixin, AutoModelSelect2MultipleField):
#     queryset = Number.objects.all()
#
#
#
# class NumberAllChoices(AutoModelSelect2Field):
#     max_results = 10
#     queryset = Number.objects.all()
#     search_fields = ['number__icontains', ]
#     get_empty_results = False
#
#     def prepare_qs_params(self, request, search_term, search_fields):
#         competition = None
#         competition_id = request.GET.get('competition_id', None)
#         if competition_id:
#             competition = Competition.objects.get(id=competition_id)
#
#         if search_term:
#             qs = super(NumberAllChoices, self).prepare_qs_params(request, search_term, search_fields)
#         else:
#             qs = {'or': [], 'and': {}}
#
#         if competition:
#             qs['and'].update({'competition_id__in': competition.get_ids()})
#
#         return qs
#
#
#
#
# class UserChoices(AutoModelSelect2Field):
#     max_results = 10
#     queryset = User.objects.all()
#     search_fields = ['first_name__icontains', 'last_name__icontains', 'ssn__icontains', 'full_name__icontains', ]
#     get_empty_results = False
#
#     def label_from_instance(self, obj):
#         return '%s (id:%i) %s' % (smart_unicode(obj), obj.id, obj.last_login.date())
#
#
# class ParticipantChoices(AutoModelSelect2Field):
#     max_results = 10
#     queryset = Participant.objects.all()
#     search_fields = ['slug__icontains', ]
#     get_empty_results = False
#
#     def prepare_qs_params(self, request, search_term, search_fields):
#         competition = None
#         competition_id = request.GET.get('competition_id', None)
#         if competition_id:
#             competition = Competition.objects.get(id=competition_id)
#
#         if search_term:
#             search_term = slugify(search_term).upper()
#             qs = super(ParticipantChoices, self).prepare_qs_params(request, search_term, search_fields)
#         else:
#             qs = {'or': [], 'and': {}}
#
#         if competition:
#             qs['and'].update({'competition_id__in': competition.get_ids()})
#
#         return qs
