from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import DetailView, TemplateView

from velo.core.models import Competition
from velo.manager.excels.income_list import create_income_list
from velo.manager.excels.insured import create_insured_list
from velo.manager.excels.start_list import create_start_list, create_standing_list, team_member_list, \
    create_team_list, payment_list, create_donations_list, start_list_have_participated_this_year, create_temporary_participant_list
from velo.manager.tables import ManageCompetitionTable
from velo.manager.views import ManageApplication
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.payment.models import Payment
from velo.registration.models import Application
from velo.registration.utils import import_lrf_licences_2018 as import_lrf_licences
from velo.velo.mixins.views import SingleTableViewWithRequest, SetCompetitionContextMixin
from velo.manager.tasks import *
from velo.team.tasks import match_team_members_to_participants, copy_registered_teams
from velo.results.tasks import update_helper_result_table


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
        elif request.POST.get('action') == 'create_temporary_participant_list':
            file_obj = create_temporary_participant_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=temporary_participant_list.xls'
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
        elif request.POST.get('action') == 'income_list' and request.user.has_perm('payment.can_see_totals'):
            file_obj = create_income_list(competition=self.competition)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename=income_list.xls'
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
            recalculate_all_points.delay(self.competition.id)
            messages.info(request, 'Veiksmīgi atjaunots')
        elif request.POST.get('action') == 'update_licence_list':
            import_lrf_licences()
            messages.info(request, 'Licenšu saraksts atjaunots.')

        elif request.POST.get('action') == 'update_helper_result_table':
            update_helper_result_table.delay(self.competition.id, update=True)
            messages.info(request, 'Starta saraksta punktu pārrēķināšanas process veiksmīgi palaists.')
        elif request.POST.get('action') == 'marketing_create_csv_seb':
            if request.user.is_superuser:
                # create_csv_seb(request.user) # TODO: Fix this
                messages.info(request, 'Nosūtīts e-pasts')
            else:
                messages.info(request, 'Nav tiesību.')
        elif request.POST.get('action') == 'copy_registered_teams':
            copy_registered_teams(self.competition.id)
            messages.info(request, 'Komandas reģistrētas')

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

        team_content_type = ContentType.objects.get(app_label="team", model="team")
        incomes = []
        if self.competition.level == 2:

            parent_total = Payment.objects.filter(status=Payment.STATUSES.ok, competition=self.competition.parent).aggregate(
                        Sum('total')).get('total__sum')
            parent_donations = Payment.objects.filter(status=Payment.STATUSES.ok, competition=self.competition.parent).aggregate(
                Sum('donation')).get('donation__sum')
            parent_insurance = Application.objects.filter(payment_status=Application.PAY_STATUS.payed, competition=self.competition.parent).aggregate(
                        Sum('total_insurance_fee')).get('total_insurance_fee__sum')

            team_payments = Payment.objects.filter(competition=self.competition.parent, content_type=team_content_type, status=Payment.STATUSES.ok).aggregate(
                        Sum('total')).get('total__sum')
            try:
                incomes.append((self.competition.parent, parent_total-parent_donations-parent_insurance-team_payments))
            except:
                incomes.append((self.competition.parent, 0.0))

            incomes.append(('Ziedojumi', parent_donations))
            incomes.append(('Apdrošināšana', parent_insurance))
            incomes.append(('Komandas maksājumi', team_payments))


        distance_donations = Payment.objects.filter(status=Payment.STATUSES.ok, competition=self.competition).aggregate(
            Sum('donation')).get('donation__sum')
        distance_insurance = Application.objects.filter(payment_status=Application.PAY_STATUS.payed, competition=self.competition).aggregate(
                    Sum('total_insurance_fee')).get('total_insurance_fee__sum')
        distance_total = Payment.objects.filter(status=Payment.STATUSES.ok, competition=self.competition).aggregate(Sum('total')).get('total__sum')

        team_payments = Payment.objects.filter(competition=self.competition, content_type=team_content_type, status=Payment.STATUSES.ok).aggregate(Sum('total')).get('total__sum')
        try:
            incomes.append((self.competition, distance_total-distance_donations-distance_insurance),)
        except:
            incomes.append((self.competition, 0.0))
        incomes.append(('Ziedojumi', distance_donations))
        incomes.append(('Apdrošināšana', distance_insurance))
        incomes.append(('Komandas maksājumi', team_payments))

        context.update({'participant_count': Participant.objects.filter(competition_id__in=self.competition.get_ids() if not self.competition.is_individual else [self.competition.id, ],
                                                                        is_participating=True).count()})
        context.update({'team_count': team_count})
        context.update({'distances_w_counter': distances_w_counter})
        context.update({'distances_teams_w_counter': distances_teams_w_counter})
        context.update({'incomes': incomes})
        return context
