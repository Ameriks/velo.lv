# coding=utf-8
from __future__ import unicode_literals
import uuid
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect

from django.template.defaultfilters import slugify
from django.utils import timezone

from django.views.generic import CreateView, ListView, View, DetailView, TemplateView, UpdateView
from django_tables2 import SingleTableView
from extra_views import UpdateWithInlinesView, NamedFormsetsMixin, InlineFormSet, CreateWithInlinesView
from braces.views import JsonRequestResponseMixin, LoginRequiredMixin, JSONResponseMixin
from extra_views.advanced import BaseUpdateWithInlinesView, BaseCreateWithInlinesView
from core.formsets import CustomBaseInlineFormSet, OnlyAddBaseInlineFormSet
from core.models import Distance, CustomSlug, Competition

from registration.forms import ApplicationCreateForm, ApplicationUpdateForm, ParticipantInlineForm, \
    ParticipantInlineRestrictedForm, ParticipantInlineFullyRestrictedForm, CompanyApplicationCreateForm, \
    CompanyParticipantInlineForm, CompanyApplicationEmptyForm
from registration.models import Participant, Application, CompanyApplication, CompanyParticipant
from registration.tables import ParticipantTable, ApplicationTable, CompanyParticipantTable, CompanyApplicationTable
from team.models import Team, Member
from velo.mixins.forms import GetClassNameMixin
from velo.mixins.views import SetCompetitionContextMixin, RequestFormKwargsMixin
from django.utils.translation import ugettext_lazy as _


class ParticipantList(SetCompetitionContextMixin, SingleTableView):
    model = Participant
    table_class = ParticipantTable
    template_name = 'registration/participant_list.html'

    def get_table_class(self):
        return self.get_competition_class().get_startlist_table_class(self.distance)

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

        # Workaround to create outer join with additional ON statement workaround
        queryset = queryset.annotate(Count('helperresults')).extra(
                select={
                    'calculated_total': 'results_helperresults.calculated_total',
                    'passage_assigned': 'results_helperresults.passage_assigned',
                    },
                where=["(results_helperresults.competition_id = %s OR results_helperresults.competition_id is null)"],
                params=[self.competition.id, ]
            )

        # if self.competition.id == 34:
        #     queryset = queryset.extra(select={
        #         'last_year_result': "Select result_distance from results_legacyresult where results_legacyresult.slug = registration_participant.slug and results_legacyresult.distance_id = registration_participant.distance_id",
        #         # 'last_year_result_fixed': "case not exists(Select points_distance from results_legacyresult where results_legacyresult.slug = registration_participant.slug and results_legacyresult.distance_id = registration_participant.distance_id) when true then '' else last_year_result end"
        #     })

        return queryset


class CompanyApplicationCreate(LoginRequiredMixin, RequestFormKwargsMixin, CreateView):
    template_name = 'registration/company_application_create.html'
    model = CompanyApplication
    form_class = CompanyApplicationCreateForm

    def get_success_url(self):
        return reverse('companyapplication', kwargs={'slug': self.object.code})

class CompanyApplicationUpdate(LoginRequiredMixin, RequestFormKwargsMixin, UpdateView):
    template_name = 'registration/company_application_create.html'
    model = CompanyApplication
    form_class = CompanyApplicationCreateForm
    slug_field = 'code'

    def get_queryset(self):
        queryset = super(CompanyApplicationUpdate, self).get_queryset()
        queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def get_success_url(self):
        return reverse('companyapplication', kwargs={'slug': self.object.code})


class CompanyApplicationDetail(LoginRequiredMixin, SingleTableView):
    model = CompanyParticipant
    table_class = CompanyParticipantTable
    template_name = 'registration/company_application_detail.html'
    companyapplication = None

    def post(self, request, *args, **kwargs):
        self.companyapplication = CompanyApplication.objects.get(code=kwargs.get('slug'), created_by=self.request.user)
        competition = self.companyapplication.competition
        team_member_count = 0
        max_team_members = self.companyapplication.competition.params.get('team_member_count', 1000)

        action = request.POST.get('action', 'none')
        pay_for = request.POST.get('pay_for', '')
        selected = request.POST.getlist('selection')
        participants = self.companyapplication.participant_set.filter(id__in=selected)

        if not selected:
            messages.info(request, _('Select at least one participant.'))
            return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))
        if len(pay_for) > 0:
            participants = participants.filter(is_participating=False)
            if not participants:
                messages.info(request, _('Select at least one participant.'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))


            # Double check if competition ID is valid
            try:
                competition = self.get_payable_competitions().get(id=pay_for)
            except:
                messages.info(request, _('Competition selected for payment is not available.'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))


            new_application = Application.objects.create(competition=competition, email=self.companyapplication.email, created_by=request.user,)
            for participant in participants:
                new_application.participant_set.create(company_participant=participant,
                                                       competition=competition,
                                                       distance=participant.distance,
                                                       first_name=participant.first_name,
                                                       last_name=participant.last_name,
                                                       birthday=participant.birthday,
                                                       ssn=participant.ssn,
                                                       country=participant.country,
                                                       gender=participant.gender,
                                                       bike_brand2=participant.bike_brand2,
                                                       email=participant.email,
                                                       phone_number=participant.phone_number,
                                                       team_name=self.companyapplication.team_name,
                                                       created_by=request.user,
                                                       )
            return HttpResponseRedirect(reverse('application', kwargs={'slug': new_application.code}))


        if action == 'add_to_team':
            team_id = request.POST.get('team', None)
            try:
                team = Team.objects.get(id=team_id, owner=request.user)
                team_member_count = team.member_set.filter(status=1).count()
                distance = team.distance
            except:
                messages.error(request, _('Select team'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))


        if action == 'create_team':
            distance_id = request.POST.get('distance', None)
            distance = Distance.objects.filter(can_have_teams=True, competition__is_in_menu=True, competition=competition).exclude(competition__competition_date__lt=timezone.now()).select_related('competition').get(id=distance_id)
            title = request.POST.get('title', None)
            if not title:
                messages.info(request, _('Add team title.'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))
            team = Team.objects.filter(slug=slugify(title), distance__competition=distance.competition)
            if team:
                messages.info(request, _('Team with title %s already exists. Pick different title.') % title)
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))

        if action in ('create_team', 'add_to_team'):
            participants = participants.filter(distance=distance)

            if not participants:
                messages.info(request, _('Select participants in selected competition distance.'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))

            if team_member_count + len(participants) > max_team_members:
                messages.info(request, _('Maximum team member count in this competition is %s. Please select less participants to add to team.') % max_team_members)
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))


            participant_already_in_teams = []
            for participant in participants:
                member = Member.objects.filter(status=Member.STATUS_ACTIVE, team__distance__competition_id=distance.competition_id, slug=participant.slug)

                if member:
                    participant_already_in_teams.append(participant.id)

            if len(participant_already_in_teams) == participants.count():
                messages.info(request, _('All selected participants are already participants in teams. One participant can be in only one team.'))
                return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))

        if action == 'create_team':
            team = Team.objects.create(distance=distance, title=title, email=self.companyapplication.email, owner=request.user, created_by=request.user, country='LV')

        if action in ('create_team', 'add_to_team'):
            for participant in participants:
                if participant.id in participant_already_in_teams:
                    messages.info(request, _("Member %s %s is already registered in other team.") % (participant.first_name, participant.last_name))
                else:
                    team.member_set.create(first_name=participant.first_name,
                                           last_name=participant.last_name,
                                           birthday=participant.birthday,
                                           gender=participant.gender,
                                           slug=participant.slug,
                                           ssn=participant.ssn,
                                           country=participant.country,
                                           status=Member.STATUS_ACTIVE)
            return HttpResponseRedirect(reverse('accounts:team', kwargs={'pk2': team.id}))

        return HttpResponseRedirect(reverse('companyapplication', kwargs={'slug': self.companyapplication.code}))



    def get_queryset(self):
        queryset = super(CompanyApplicationDetail, self).get_queryset()
        queryset = queryset.filter(application__code=self.kwargs.get('slug', '!'))
        queryset = queryset.filter(application__created_by=self.request.user).select_related('distance')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CompanyApplicationDetail, self).get_context_data(**kwargs)
        context.update({'companyapplication': self.companyapplication})

        competition = self.companyapplication.competition


        my_teams = Team.objects.filter(created_by=self.request.user, distance__competition=competition)
        context.update({'my_teams': my_teams})

        distances = Distance.objects.filter(can_have_teams=True, competition__is_in_menu=True, competition=competition).exclude(
            competition__competition_date__lt=timezone.now())
        distance_choices = [
            (unicode(distance.id), "{0} - {1}".format(distance.competition.__unicode__(), distance.__unicode__())) for
            distance in distances]

        context.update({'distance_choices': distance_choices})

        payable_competitions = self.get_payable_competitions()
        context.update({'payable_competitions': payable_competitions})


        return context

    def get_payable_competitions(self):
        now = timezone.now()
        competition = self.companyapplication.competition
        return Competition.objects.filter(Q(id=competition.id) | Q(parent_id=competition.id)).filter(Q(complex_payment_enddate__gt=now) | Q(price__end_registering__gt=now, price__start_registering__lte=now)).distinct().order_by('complex_payment_enddate', 'competition_date')


    def get(self, request, *args, **kwargs):
        self.companyapplication = CompanyApplication.objects.get(code=kwargs.get('slug'), created_by=self.request.user)
        return super(CompanyApplicationDetail, self).get(request, *args, **kwargs)


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





class CompanyParticipantInline(GetClassNameMixin, InlineFormSet):
    can_order = False
    model = CompanyParticipant
    formset_class = OnlyAddBaseInlineFormSet
    form_class = CompanyParticipantInlineForm
    extra = 1

    @property
    def can_delete(self):
        return True

    def get_formset_kwargs(self):
        kwargs = super(CompanyParticipantInline, self).get_formset_kwargs()
        kwargs.update({'application': self.view.object})
        kwargs.update({'empty_form_class': self.form_class})
        kwargs.update({'required': 1})
        kwargs.update({'can_add_new': True})
        return kwargs

    def get_extra_form_kwargs(self):
        kwargs = super(CompanyParticipantInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        kwargs.update({'application': self.view.object})
        return kwargs



class CompanyApplicationParticipantAdd(RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    template_name = 'registration/company_application_add.html'
    inlines = [CompanyParticipantInline, ]
    inlines_names = ['participant']
    model = CompanyApplication
    form_class = CompanyApplicationEmptyForm
    slug_field = 'code'

    def get_queryset(self):
        queryset = super(CompanyApplicationParticipantAdd, self).get_queryset()
        queryset = queryset.filter(status=1)
        return queryset

    def get_success_url(self):
        if self.object.created_by == self.request.user:
            return reverse('companyapplication', kwargs={'slug': self.object.code})
        else:
            return reverse('companyapplication_ok', kwargs={'slug': self.object.code})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.competition.is_past_due:
            messages.error(request, _('Competition already passed. Cannot register to historic competitions.'))
            return HttpResponseRedirect(reverse('companyapplication_add', kwargs={'slug': self.object.code}))
        else:
            return super(BaseUpdateWithInlinesView, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        return super(BaseUpdateWithInlinesView, self).get(request, *args, **kwargs)


class MyCompanyApplicationList(LoginRequiredMixin, SingleTableView):
    model = CompanyApplication
    table_class = CompanyApplicationTable
    template_name = 'registration/company_application_my.html'

    def get_queryset(self):
        queryset = super(MyCompanyApplicationList, self).get_queryset()
        queryset = queryset.filter(created_by=self.request.user).select_related('competition', 'competition__parent')

        return queryset


class CompanyApplicationParticipantAddOK(TemplateView):
    template_name = 'registration/company_application_added.html'