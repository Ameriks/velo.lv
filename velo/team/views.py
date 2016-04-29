# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from difflib import get_close_matches
from django_tables2 import SingleTableView
from braces.views import LoginRequiredMixin
from extra_views import NamedFormsetsMixin, CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
import datetime

from velo.core.formsets import CustomBaseInlineFormSet
from velo.core.models import Competition
from velo.registration.models import Participant, Application
from velo.team.forms import MemberInlineForm, TeamForm
from velo.team.models import Team, Member, MemberApplication
from velo.team.tables import TeamTable, TeamMyTable
from velo.velo.mixins.forms import GetClassNameMixin
from velo.velo.mixins.views import SetCompetitionContextMixin, SingleTableViewWithRequest, RequestFormKwargsMixin



class TeamAppliedView(SetCompetitionContextMixin, ListView):
    """
    This class is used to display teams that have applied to competition.
    This is optimized view.
    """
    model = Team
    template_name = 'team/applied.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(TeamAppliedView, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(TeamAppliedView, self).get_queryset()

        queryset = queryset.filter(distance=self.distance, member__memberapplication__competition=self.competition)

        queryset = queryset.order_by('-is_featured', 'title',
                                     'member__memberapplication__kind', 'member__memberapplication__participant__primary_number__number',)

        queryset = queryset.values_list('id', 'title', 'is_featured',
                                        'member__first_name', 'member__last_name', 'member__birthday',
                                        'member__memberapplication__kind',
                                        'member__memberapplication__participant__primary_number__number',
                                        'member__memberapplication__participant_id',
                                        )
        return queryset


class TeamListView(SingleTableViewWithRequest):
    model = Team
    table_class = TeamTable

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))
        return super(TeamListView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        table = self.get_table(request=self.request, request_kwargs=self.kwargs)
        context[self.get_context_table_name(table)] = table
        context.update({'competition': self.competition})
        context.update({'distances': self.distances})
        context.update({'distance_active': self.distance})
        context.update({'banners': self.get_banners()})

        return context

    def get_queryset(self):
        queryset = super(TeamListView, self).get_queryset()
        queryset = queryset.filter(distance=self.distance, distance__competition_id__in=self.competition.get_ids(), status__gte=0)

        if self.request.GET.get("search", None):
            queryset = queryset.filter(title__icontains=self.request.GET.get("search", None))

        return queryset

class TeamView(DetailView):
    model = Team
    pk_url_kwarg = 'pk2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'competition': Competition.objects.get(id=self.kwargs.get('pk'))})
        context.update({'members': self.object.member_set.filter(status=Member.STATUS_ACTIVE).order_by('last_name')})

        return context

class TeamMemberProfileView(DetailView):
    model = Member
    pk_url_kwarg = 'pk3'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'competition': Competition.objects.get(id=self.kwargs.get('pk'))})
        context.update({'members': self.object.team.member_set.filter(status=Member.STATUS_ACTIVE).order_by('last_name')})

        return context


class MyTeamList(LoginRequiredMixin, SingleTableView):
    model = Team
    table_class = TeamMyTable
    template_name = 'team/team_list_my.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user).select_related('distance', 'distance__competition', 'distance__competition__parent')
        return queryset


class MemberInline(GetClassNameMixin, InlineFormSet):
    can_order = False
    model = Member
    formset_class = CustomBaseInlineFormSet
    form_class = MemberInlineForm
    competition = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.object:
            self.competition = self.object.distance.competition

    @property
    def can_delete(self):
        delete_date_obj = datetime.date.today()

        if self.competition and self.competition.params:
            delete_date = self.competition.params_dict.get('team_member_delete_final', None)
            if delete_date:
                delete_date_obj = datetime.datetime.strptime(delete_date, '%Y-%m-%d').date()

        if datetime.date.today() <= delete_date_obj:
            print('CAN DELETE')
            return True
        else:
            print('CANNOT DELETE')
            return False


    @property
    def extra(self):
        if self.object and self.object.member_set.count() > 0:
            return 0
        else:
            return 1

    def get_formset_kwargs(self):
        kwargs = super(MemberInline, self).get_formset_kwargs()
        kwargs.update({'empty_form_class': self.form_class})
        kwargs.update({'required': 1})
        kwargs.update({'can_add_new': True})
        kwargs.update({'max_num': self.competition.params_dict.get('team_member_count', 1000) if self.competition else 1000})
        kwargs.update({'queryset': Member.objects.filter(status=Member.STATUS_ACTIVE) })
        return kwargs

    def get_extra_form_kwargs(self):
        kwargs = super(MemberInline, self).get_extra_form_kwargs()
        kwargs.update({'request': self.request})
        kwargs.update({'request_kwargs': self.kwargs})
        return kwargs


class TeamCreateView(LoginRequiredMixin, RequestFormKwargsMixin, NamedFormsetsMixin, CreateWithInlinesView):
    template_name = 'team/team_form.html'
    inlines = [MemberInline, ]
    inlines_names = ['member']
    model = Team
    form_class = TeamForm

    def get_success_url(self):
        return reverse('accounts:team_list')


class TeamUpdateView(LoginRequiredMixin, RequestFormKwargsMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    template_name = 'team/team_form.html'
    inlines = [MemberInline, ]
    inlines_names = ['member']
    model = Team
    form_class = TeamForm
    pk_url_kwarg = 'pk2'

    def get_success_url(self):
        return reverse('accounts:team_list')

    def get_queryset(self):
        queryset = super(TeamUpdateView, self).get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        ret = super().post(request, *args, **kwargs)
        if request.POST.get('submit_pay', None):

            next_competition = None
            competition = self.object.distance.competition
            if competition.get_root().id == 1:
                next_competition = self.object.distance.competition.children.filter(competition_date__gt=timezone.now())[:1]
            elif competition.competition_date and competition.competition_date > datetime.date.today():
                next_competition = [competition, ]

            if next_competition:
                next_competition = next_competition[0]
                application = Application.objects.create(competition=next_competition, email=request.user.email)
                for member in self.object.member_set.filter(status=Member.STATUS_ACTIVE):
                    application.participant_set.create(first_name=member.first_name,
                                                       last_name=member.last_name,
                                                       country=member.country,
                                                       birthday=member.birthday,
                                                       ssn=member.ssn,
                                                       competition=next_competition,
                                                       distance=self.object.distance,
                                                       team_name=self.object.title,
                                                       )
                return HttpResponseRedirect(reverse('application', kwargs={'slug': application.code}))

        return ret



class TeamApplyList(LoginRequiredMixin, RequestFormKwargsMixin, NamedFormsetsMixin, DetailView):
    model = Team
    template_name = 'team/team_apply_list.html'
    pk_url_kwarg = 'pk2'

    def get_queryset(self):
        queryset = super(TeamApplyList, self).get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        competition = self.object.distance.competition
        child_competitions = competition.get_children()

        if child_competitions:
            competitions = child_competitions
        else:
            competitions = (competition, )

        final_competitions = []
        for competition in competitions:
            members = MemberApplication.objects.filter(competition=competition, member__team=self.object).order_by('kind')
            final_competitions.append((competition, members))
            if competition.competition_date > datetime.date.today():
                break

        context.update({'competitions': final_competitions})

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        pay_members = request.POST.getlist('pay_member')
        if pay_members:
            member_ids = {}
            for pay_member in pay_members:
                competition_id, member_id = pay_member.split('__')
                if not competition_id in member_ids:
                    member_ids.update({competition_id: []})
                member_ids.get(competition_id).append(member_id)
            key = member_ids.keys()[0]

            application = Application.objects.create(competition_id=key, email=request.user.email)
            for member_id in member_ids.get(key):
                member = self.object.member_set.get(id=member_id)
                application.participant_set.create(first_name=member.first_name,
                                                   last_name=member.last_name,
                                                   country=member.country,
                                                   birthday=member.birthday,
                                                   gender=member.gender,
                                                   ssn=member.ssn,
                                                   competition_id=key,
                                                   distance=self.object.distance,
                                                   team_name=self.object.title,
                                                   )

            return HttpResponseRedirect(reverse('application', kwargs={'slug': application.code}))
        else:
            return self.get(request, *args, **kwargs)


class TeamApply(LoginRequiredMixin, RequestFormKwargsMixin, NamedFormsetsMixin, DetailView):
    model = Team
    template_name = 'team/team_apply.html'
    pk_url_kwarg = 'pk2'

    def get_queryset(self):
        queryset = super(TeamApply, self).get_queryset()
        if not self.request.user.has_perm('registration.add_number'):
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TeamApply, self).get_context_data(**kwargs)

        competition = Competition.objects.get(id=self.kwargs.get('competition_pk'))

        team_competition = self.object.distance.competition
        child_competitions = team_competition.get_children()

        if child_competitions:
            competitions = child_competitions
        else:
            competitions = (team_competition, )

        if competition not in competitions:
            raise Http404

        members = Member.objects.filter(team=self.object, status=Member.STATUS_ACTIVE).extra(select={
            'kind': 'Select team_memberapplication.kind from team_memberapplication where team_memberapplication.member_id = team_member.id and team_memberapplication.competition_id=%s'
        }, select_params=(competition.id, ))
        context.update({'members': members, 'competition': competition, 'team_competition': team_competition})
        return context

    def match_applied_to_participant(self, application):
        distance = application.member.team.distance
        application.participant = None
        application.participant_unpaid = None
        application.participant_potential = None
        participant = Participant.objects.filter(competition_id__in=application.competition.get_ids(), slug=application.member.slug, is_participating=True, distance=distance)
        if participant:
            application.participant = participant[0]
        else:
            participant = Participant.objects.filter(competition_id__in=application.competition.get_ids(), slug=application.member.slug, distance=distance)
            if participant:
                application.participant_unpaid = participant[0]
            else:
                slugs = [obj.slug for obj in Participant.objects.filter(competition_id__in=application.competition.get_ids(), distance=distance, is_participating=True)]
                matches = get_close_matches(application.member.slug, slugs, 1, 0.5)
                if matches:
                    participants = Participant.objects.filter(competition=application.competition, slug=matches[0], distance=distance).order_by('-id')
                    if participants:
                        application.participant_potential = participants[0]
        application.save()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        team_competition = context.get('team_competition')
        competition = context.get('competition')

        riders = []
        reserve = []
        nothing = []

        for member in context.get('members'):
            data = int(request.POST.get('member_%i' % member.id))
            if data == MemberApplication.KIND_PARTICIPANT:
                riders.append(member.id)
            elif data == MemberApplication.KIND_RESERVE:
                reserve.append(member.id)
            else:
                nothing.append(member.id)

        max_team_riders = team_competition.params_dict.get('max_team_riders', 1000)
        max_team_reserve = team_competition.params_dict.get('max_team_reserve', 1000)
        if len(riders) > max_team_riders:
            messages.error(request, _('Too many team members marked as participants. MAX-%i') % max_team_riders)
        elif len(reserve) > max_team_reserve:
            messages.error(request, _('Too many team members marked as reserve. MAX-%i') % max_team_reserve)
        else:
            for rider in riders:
                application, created = MemberApplication.objects.get_or_create(member_id=rider, competition=competition, defaults={'kind': MemberApplication.KIND_PARTICIPANT})
                if not created:
                    application.kind = MemberApplication.KIND_PARTICIPANT
                    application.save()

                self.match_applied_to_participant(application)

            for rider in reserve:
                application, created = MemberApplication.objects.get_or_create(member_id=rider, competition=competition, defaults={'kind': MemberApplication.KIND_RESERVE})
                if not created:
                    application.kind = MemberApplication.KIND_RESERVE
                    application.save()

                self.match_applied_to_participant(application)

            MemberApplication.objects.filter(competition=competition).filter(member_id__in=nothing).delete()

            messages.info(request, _('Successfuly saved.'))
            if 'pk' in self.kwargs:
                return HttpResponseRedirect(reverse('manager:team_apply_list', kwargs={'pk2': self.object.id, 'pk': self.kwargs.get('pk')}))
            else:
                return HttpResponseRedirect(reverse('accounts:team_apply_list', kwargs={'pk2': self.object.id}))

        return self.render_to_response(context)
