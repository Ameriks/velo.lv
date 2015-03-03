# coding=utf-8
from __future__ import unicode_literals
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect

from django.template.defaultfilters import slugify

from django.views.generic import CreateView, ListView, View
from django_tables2 import SingleTableView
from extra_views import UpdateWithInlinesView, NamedFormsetsMixin, InlineFormSet
from braces.views import JsonRequestResponseMixin, LoginRequiredMixin, JSONResponseMixin
from extra_views.advanced import BaseUpdateWithInlinesView
from core.formsets import CustomBaseInlineFormSet

from registration.forms import ApplicationCreateForm, ApplicationUpdateForm, ParticipantInlineForm, \
    ParticipantInlineRestrictedForm, ParticipantInlineFullyRestrictedForm
from registration.models import Participant, Application
from registration.tables import ParticipantTable, ApplicationTable
from velo.mixins.forms import GetClassNameMixin
from velo.mixins.views import SetCompetitionContextMixin, RequestFormKwargsMixin
from django.utils.translation import ugettext_lazy as _


class ParticipantList(SetCompetitionContextMixin, SingleTableView):
    model = Participant
    table_class = ParticipantTable
    template_name = 'registration/participant_list.html'

    def get_table_class(self):
        return self.get_competition_class().get_startlist_table_class()

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances()  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(ParticipantList, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(ParticipantList, self).get_queryset()
        queryset = queryset.filter(is_participating=True)

        if self.distance:
            queryset = queryset.filter(distance=self.distance)

        search = self.request.GET.get('search', None)
        if search:
            search_slug = slugify(search)
            queryset = queryset.filter(
                Q(slug__icontains=search_slug) | Q(primary_number__number__icontains=search_slug) | Q(team_name__icontains=search.upper()))


        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        queryset = queryset.select_related('competition', 'distance', 'team', 'primary_number')

        # if self.competition.id == 34:
        #     queryset = queryset.extra(select={
        #         'last_year_result': "Select result_distance from results_legacyresult where results_legacyresult.slug = registration_participant.slug and results_legacyresult.distance_id = registration_participant.distance_id",
        #         # 'last_year_result_fixed': "case not exists(Select points_distance from results_legacyresult where results_legacyresult.slug = registration_participant.slug and results_legacyresult.distance_id = registration_participant.distance_id) when true then '' else last_year_result end"
        #     })

        return queryset


class ApplicationCreate(RequestFormKwargsMixin, CreateView):
    template_name = 'registration/application_create.html'
    model = Application
    form_class = ApplicationCreateForm

    def get_success_url(self):
        return reverse('application', kwargs={'slug': self.object.code})

class ParticipantInline(GetClassNameMixin, InlineFormSet):
    can_order = False
    model = Participant
    formset_class = CustomBaseInlineFormSet

    @property
    def can_delete(self):
        if self.view.object.payment_status == self.view.object.PAY_STATUS_NOT_PAYED:
            return True
        return False


    @property
    def form_class(self):
        if self.view.object.competition.is_past_due:
            return ParticipantInlineFullyRestrictedForm
        if self.view.object.payment_status == self.view.object.PAY_STATUS_NOT_PAYED:
            return ParticipantInlineForm
        return ParticipantInlineRestrictedForm

    @property
    def extra(self):
        if self.object.participant_set.count() > 0:
            return 0
        else:
            return 1

    def get_formset_kwargs(self):
        kwargs = super(ParticipantInline, self).get_formset_kwargs()
        kwargs.update({'application': self.view.object})
        kwargs.update({'empty_form_class': self.form_class})
        kwargs.update({'required': 1})
        kwargs.update({'can_add_new': self.view.object.payment_status == self.view.object.PAY_STATUS_NOT_PAYED})
        return kwargs

    def get_extra_form_kwargs(self):
        kwargs = super(ParticipantInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        kwargs.update({'application': self.view.object})
        return kwargs



class ApplicationUpdate(RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    template_name = 'registration/application_update.html'
    inlines = [ParticipantInline, ]
    inlines_names = ['participant']
    model = Application
    form_class = ApplicationUpdateForm
    slug_field = 'code'

    def get_context_data(self, **kwargs):
        context = super(ApplicationUpdate, self).get_context_data(**kwargs)
        return context

    def get_success_url(self):
        if self.request.POST.get('submit_draft'):
            if self.object.payment_status == Application.PAY_STATUS_PAYED:
                messages.info(self.request, _('Saved'))
            else:
                messages.info(self.request, _('Draft saved'))
            return ''
        else:
            return reverse('application_pay', kwargs={'slug': self.object.code})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.competition.is_past_due:
            return HttpResponseRedirect(reverse('application', kwargs={'slug': self.object.code}))
        else:
            return super(BaseUpdateWithInlinesView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.created_by and self.object.created_by != request.user:
            messages.error(request, _("Currently logged in user doesn't have access to this application. Please, login with user that you used to create application."))
            return HttpResponseRedirect("%s?next=%s" % (reverse('accounts:login'), request.path))

        return super(BaseUpdateWithInlinesView, self).get(request, *args, **kwargs)


class TeamJsonList(JsonRequestResponseMixin, SetCompetitionContextMixin, ListView):
    model = Participant

    def get_queryset(self):
        queryset = super(TeamJsonList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids()).filter(is_participating=True).exclude(team_name='').values('team_name').annotate(num=Count('id'))
        queryset = queryset.order_by('-num')

        team_name_text = self.request.GET.get('search', '')
        if team_name_text:
            team_name = slugify(team_name_text.replace(' ', ''))
            queryset = queryset.filter(team_name_slug__icontains=team_name)
        else:
            queryset = queryset.filter(num__gte=2)

        return queryset

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.object_list = self.get_queryset()
        return self.render_json_response(list(self.object_list))


class BikeBrandJsonList(JsonRequestResponseMixin, ListView):
    model = Participant

    def get_queryset(self):
        queryset = super(BikeBrandJsonList, self).get_queryset()
        queryset = queryset.filter(is_participating=True).exclude(bike_brand2='').exclude(bike_brand2='Cits').values('bike_brand2').annotate(num=Count('id'))
        queryset = queryset.order_by('-num')

        search_text = self.request.GET.get('search', '')
        if search_text:
            team_name = slugify(search_text.replace(' ', ''))
            queryset = queryset.filter(bike_brand2__icontains=team_name)
        else:
            queryset = queryset.filter(num__gte=2)

        return queryset

    def get(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_json_response(list(self.object_list))



class ParticipantSearchView(JsonRequestResponseMixin, ListView):
    model = Participant

    def get_queryset(self):
        queryset = super(ParticipantSearchView, self).get_queryset()

        queryset = queryset.filter(is_participating=True)

        queryset = queryset.select_related('competition', 'distance').order_by('-competition__competition_date', 'last_name')

        kind = self.kwargs.get('kind')
        search = self.request.GET.get('search', '')

        search_slug = ''
        if search:
            search_slug = slugify(search)



        queryset = queryset.extra(where=["to_char(birthday, 'YYYY-MM-DD') LIKE %s OR ssn LIKE %s OR slug LIKE %s"], params=["%{0}%".format(search), "%{0}%".format(search.replace('-', '')), "%{0}%".format(search_slug), ])

        if not self.request.user.is_authenticated():
            queryset = queryset.filter(created_by=-1)
        elif not self.request.user.has_perm('registration.add_number'):
            queryset = queryset.filter(created_by=self.request.user)

        queryset = queryset[:20]

        queryset = queryset.values('birthday', 'full_name', 'country', 'first_name', 'last_name', 'gender', 'ssn', 'team_name', 'phone_number', 'email', 'city', 'occupation', 'bike_brand2', 'competition__name')

        return queryset

    def get(self, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_json_response(list(self.object_list))




class MyApplicationList(LoginRequiredMixin, SingleTableView):
    model = Application
    table_class = ApplicationTable
    template_name = 'registration/application_my.html'

    def get_queryset(self):
        queryset = super(MyApplicationList, self).get_queryset()
        queryset = queryset.filter(created_by=self.request.user).select_related('competition', 'competition__parent')

        return queryset


class DataForExternalTotal(JSONResponseMixin, SetCompetitionContextMixin, View):
    content_type = "application/json"

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        data = Participant.objects.filter(competition=self.competition).filter(is_participating=True).aggregate(participants=Count('id'), total_km=Sum('distance__distance_m'))
        return self.render_json_response(data)


class DataForExternalAll(JSONResponseMixin, SetCompetitionContextMixin, View):
    content_type = "application/json"

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        data = list(Participant.objects.filter(competition=self.competition).filter(is_participating=True).values('id', 'distance__distance_m'))
        return self.render_json_response(data)





