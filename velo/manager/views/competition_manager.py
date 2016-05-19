# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import DetailView, TemplateView

from velo.core.models import Competition
from velo.manager.excels.insured import create_insured_list
from velo.manager.excels.start_list import create_start_list, create_standing_list, team_member_list, \
    create_team_list, payment_list, create_donations_list, start_list_have_participated_this_year
from velo.manager.tables import ManageCompetitionTable
from velo.manager.views import ManageApplication
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.registration.models import Participant, Application
from velo.velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin
from velo.velo.utils import load_class
from velo.manager.tasks import *
from velo.team.tasks import match_team_members_to_participants

__all__ = [
    'ManageCompetitionList', 'ManageCompetitionDetail', 'ManageApplicationExternalPay'
]


class IncomeObject(object):
    distance = None
    parent_income = None
    income = None
    total = None

    parent_count = 0
    count = 0
    total_count = 0

    def __init__(self, distance, parent_income, income, parent_count, count):
        self.distance = distance
        if parent_income:
            self.parent_income = float(parent_income)
        self.income = float(income)
        if parent_income:
            self.total = self.parent_income + self.income
        else:
            self.total = self.income

        self.parent_count = parent_count
        self.count = count
        if self.parent_count:
            self.total_count = self.parent_count + self.count
        else:
            self.total_count = self.count


class ManageApplicationExternalPay(ManageApplication):
    template_name = 'bootstrap/manager/external_application_update.html'

    @method_decorator(xframe_options_exempt)
    def post(self, request, *args, **kwargs):
        super(ManageApplicationExternalPay, self).post(request, *args, **kwargs)
        return super(ManageApplicationExternalPay, self).get(request, *args, **kwargs)


class ManageCompetitionList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Competition
    table_class = ManageCompetitionTable
    template_name = 'bootstrap/manager/table.html'


class ManageCompetitionDetail(ManagerPermissionMixin, SetCompetitionContextMixin, DetailView):
    model = Competition
    template_name = 'bootstrap/manager/competition_detail.html'

    def post(self, request, *args, **kwargs):
        self.competition = Competition.objects.get(id=kwargs.get('pk'))
        class_ = load_class(self.competition.processing_class)
        self._competition_class = class_(self.competition.id)
        if request.POST.get('action') == 'assign_numbers_continuously':
            self._competition_class.assign_numbers_continuously()
        elif request.POST.get('action') == 'legacy_sync':
            pass # TODO: Fix this
            # messages.add_message(request, messages.INFO,
            #                      'Sinhronizācija sākta. Gaidiet e-pastu uz %s ar paziņojumu par beigām.' % request.user.email)
            # legacy_sync.delay(request.user.email)
        elif request.POST.get('action') == 'start_list':
            file_obj = create_start_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=start_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'start_list_have_participated_this_year':
            file_obj = start_list_have_participated_this_year(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=have_participated_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'donations_list':
            file_obj = create_donations_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=donations_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response


        elif request.POST.get('action') == 'payment_list':
            file_obj = payment_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=payment_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response

        elif request.POST.get('action') == 'create_standing_list':
            file_obj = create_standing_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=standing_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'team_member_list':
            file_obj = team_member_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=team_member_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'create_team_list':
            file_obj = create_team_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=applied_teams.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'create_insured_list':
            file_obj = create_insured_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=insured_list.xls'
            response.write(file_obj.getvalue())
            file_obj.close()
            return response
        elif request.POST.get('action') == 'match_team_members_to_participants':
            match_team_members_to_participants.delay(self.competition.id)
            messages.info(request, 'Sinhronizācijas process veiksmīgi palaists.')
        elif request.POST.get('action') == 'recalculate_all_points':
            self._competition_class.recalculate_all_points()
            messages.info(request, 'Veiksmīgi atjaunots')
        elif request.POST.get('action') == 'marketing_create_csv_seb':
            if request.user.is_superuser:
                # create_csv_seb(request.user) # TODO: Fix this
                messages.info(request, 'Nosūtīts e-pasts')
            else:
                messages.info(request, 'Nav tiesību.')

        return super(ManageCompetitionDetail, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ManageCompetitionDetail, self).get_context_data(**kwargs)

        distances = self.competition.get_distances()

        distances_w_counter = []
        for distance in distances:
            distances_w_counter.append(
                (distance, distance.get_participants(self.competition.get_ids()).filter(is_participating=True).count()))

        distances_teams_w_counter = []
        team_count = 0
        for distance in distances.filter(can_have_teams=True):
            counter = distance.get_teams().count()
            team_count += counter
            distances_teams_w_counter.append((distance, counter))

        incomes = []
        # Income calculator

        for distance in distances:
            # calculate parent income.
            parent_income = None
            parent_count = None
            if self.object.level == 2:
                parent_dict = Participant.objects.filter(is_participating=True, competition=self.competition.parent,
                                                         distance=distance).exclude(price=None).aggregate(
                    Sum('price__price'), Count('id'))
                parent_count = parent_dict.get('id__count')
                try:
                    parent_income = parent_dict.get('price__price__sum', 0) * (
                    100 - self.competition.parent.complex_discount) / 100
                except TypeError:
                    parent_income = None

            income_dict = Participant.objects.filter(is_participating=True, competition=self.competition,
                                                     distance=distance).exclude(price=None).aggregate(
                Sum('price__price'), Sum('discount_amount'), Count('id'))
            income = (income_dict.get('price__price__sum') or 0) - (income_dict.get('discount_amount__sum') or 0)
            incomes.append(IncomeObject(distance, parent_income, income, parent_count, income_dict.get('id__count')))

        context.update({'participant_count': Participant.objects.filter(competition_id__in=self.competition.get_ids(),
                                                                        is_participating=True).count()})
        context.update({'team_count': team_count})
        context.update({'distances_w_counter': distances_w_counter})
        context.update({'distances_teams_w_counter': distances_teams_w_counter})
        context.update({'incomes': incomes})
        return context
