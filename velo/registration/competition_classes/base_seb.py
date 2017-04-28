import datetime
import math
import csv
from django.db import connection
from django.utils.translation import activate
from django.utils import timezone
from sitetree.utils import item
from velo.core.models import Log

from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Number, Participant, PreNumberAssign
from django.core.cache import cache
from velo.registration.tables import ParticipantTable
from velo.results.helper import time_to_seconds
from velo.results.models import Result, ChipScan, SebStandings, TeamResultStandings, HelperResults
from velo.results.tables import ResultChildrenGroupTable, ResultGroupTable, ResultDistanceTable, \
    ResultChildrenGroupStandingTable, ResultGroupStandingTable, ResultDistanceStandingTable
from velo.results.tasks import create_result_sms, recalculate_standing_for_result, update_helper_result_table
from velo.team.models import MemberApplication, Team
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class SEBCompetitionBase(CompetitionScriptBase):
    def __init__(self, *args, **kwargs):
        """
        Current competition have multiple stages. We need to set current stage index.
        """
        super(SEBCompetitionBase, self).__init__(*args, **kwargs)

        if self.competition.level == 2:  # if class is created for parent competition, then we do not have index
            classname = self.__class__.__name__
            cache_key = '%s_competition_index_ids' % classname
            child_ids = cache.get(cache_key)
            if not child_ids:
                child_ids = [c.id for c in self.competition.parent.get_children()]
                cache.set(cache_key, child_ids)

            self.competition_index = child_ids.index(self.competition_id) + 1


    def build_manager_menu(self):
        child_items = []
        for child in self.competition.get_children():
            children = []
            children.append(item('Dalībnieki', '#', url_as_pattern=False, access_loggedin=True, in_menu=False, children=[
                item('Pieteikt dalībnieku', 'manager:participant_create %i' % child.id, access_loggedin=True),
                item('Dalībnieku saraksts', 'manager:participant_list %i' % child.id, access_loggedin=True),
                item('Dalībnieku numuri', 'manager:number_list %i' % child.id, access_loggedin=True),
                item('{{ object }}', 'manager:participant %i object.id' % child.id, in_menu=False, access_loggedin=True),
            ]))
            children.append(item('Komandas', '#', url_as_pattern=False, access_loggedin=True, in_menu=False, children=[
                item('Pieteiktās komandas', 'manager:applied_team_list %i' % child.id, access_loggedin=True),
                item('{{ object }}', 'manager:edit_team %i object.id' % child.id, in_menu=False, access_loggedin=True),
                item('Dalībnieku saraksts', 'manager:team_applied_participant_list %i' % child.id, in_menu=False, access_loggedin=True),


                # item('Dalībnieku saraksts', 'manager:participant_list %i' % child.id, access_loggedin=True),
                # item('Dalībnieku numuri', 'manager:number_list %i' % child.id, access_loggedin=True),
                # item('{{ object }}', 'manager:participant %i object.id' % child.id, in_menu=False, access_loggedin=True),
            ]))
            children.append(item('Rezultāti', '#', url_as_pattern=False, in_menu=False, access_loggedin=True, children=[
                item('Saraksts', 'manager:result_list %i' % child.id, access_loggedin=True),
                item('Pievienot jaunu', 'manager:result %i' % child.id, access_loggedin=True),
                item('Atskaites', 'manager:result_reports %i' % child.id, access_loggedin=True),
            ]))
            children.append(item('Analīze', '#', url_as_pattern=False, in_menu=False, access_loggedin=True, children=[
                item('Vienādie ALIASi', 'manager:analytics_same_slug %i' % child.id, access_loggedin=True),
                item('Vairāki numuri', 'manager:analytics_multiple_numbers %i' % child.id, access_loggedin=True),
                item('Nestartē, bet numurs', 'manager:analytics_results_incorrect %i' % child.id, access_loggedin=True),
                item('Atšķiras ALIASI no numura', 'manager:analytics_different_slugs %i' % child.id, access_loggedin=True),
                item('Atšķiras ALIASI no numura2', 'manager:match_participant_number %i' % child.id, access_loggedin=True),

                item('Piesaistīt dalībnieku numuram (labot gramatiku)', 'manager:analytics_find_unmatched_participant %i' % child.id, access_loggedin=True),



            ]))
            children.append(item('Parametri', '#', url_as_pattern=False, in_menu=False, access_loggedin=True, children=[
                item('Distance admin', 'manager:distance_admin_list %i' % child.id, access_loggedin=True),
            ]))
            child_items.append(item(str(child), 'manager:competition %i' % child.id, access_loggedin=True, children=children))


        return item(str(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu, access_loggedin=True)

    def build_menu(self, lang):
        activate(lang)
        current_date = datetime.date.today()

        allchildren = list(self.competition.get_children().order_by('-competition_date'))

        child_items = [
            item(_("Teams"), 'competition:team %i' % self.competition.id, children=[
                item('{{ object }}', 'competition:team %i object.id' % self.competition.id, in_menu=False),
            ]),
            item(_("Standings"), 'competition:standings_list %i' % self.competition.id),
            item(_("Team Standings"), 'competition:team_standings_list %i' % self.competition.id, in_menu=False),
        ]

        # If there is still active complex payment, then we should show start list from 1st stage.
        if self.competition.complex_payment_enddate > timezone.now():
            child_items.append(item(_("Start List"), 'competition:participant_list %i' % allchildren[-1].id))

        self.build_flat_pages(self.competition, child_items, lang)

        for index, child in enumerate(allchildren, start=1):
            if index < len(allchildren) and allchildren[index].competition_date > current_date:
                continue

            children = [
                item(_("Competition"), 'competition:competition %i' % child.id, in_menu=False),
                item(_("Teams"), 'competition:team %i' % child.id, children=[
                    item('{{ object }}', 'competition:team %i object.id' % child.id, in_menu=False),
                ]),
                item(_("Standings"), 'competition:standings_list %i' % child.id),
                item(_("Team Standings"), 'competition:team_standings_list %i' % child.id, in_menu=False),
                item(_("Start List"), 'competition:participant_list %i' % child.id),
                item(_("Applied Teams"), 'competition:applied_teams_list %i' % child.id),
                item(_("Maps"), 'competition:maps %i' % child.id),
            ]

            self.build_flat_pages(child, children, lang)

            if child.competition_date <= current_date + datetime.timedelta(days=1):
                children.append(item(_("Results"), 'competition:result_distance_list %i' % child.id))
                children.append(item(_("Team Results"), 'competition:result_team_list %i' % child.id, in_menu=False))

            child_items.append(item(str(child), '#', children=children))

        return item(self.competition.name, 'competition:competition %i' % self.competition.id, url_as_pattern=True, children=child_items, in_menu=self.competition.is_in_menu)

    def get_startlist_table_class(self, distance=None):
        return ParticipantTable


    def recalculate_team_results(self):
        """
        Function to recalculate all team results for current competition.
        """
        teams = Team.objects.filter(member__memberapplication__competition=self.competition, member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT).order_by('id').distinct('id')
        for team in teams:
            print(team.id)
            self.recalculate_team_result(team=team)

    def recalculate_team_result(self, team_id=None, team=None):
        """
        Function to recalculate team's result for current competition.
        After current competition point recalculation, standing total points are recalculated as well.
        """
        if not team and not team_id:
            raise Exception('Team or Team Id must be set')
        if not team:
            team = Team.objects.get(id=team_id)
        else:
            team_id = team.id

        team_member_results = Team.objects.filter(
            id=team_id,
            member__memberapplication__competition=self.competition,
            member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT,
            member__memberapplication__participant__result__competition=self.competition).order_by('-member__memberapplication__participant__result__points_distance').values_list('member__memberapplication__participant__result__points_distance')[:4]
        standing, created = TeamResultStandings.objects.get_or_create(team_id=team_id)

        # Set current competition points to best 4 riders sum
        setattr(standing, 'points%i' % self.competition_index, sum([val[0] for val in team_member_results if val[0]]))

        # Recalculate total sum.
        point_list = [standing.points1, standing.points2, standing.points3, standing.points4, standing.points5, standing.points6, standing.points7]
        if team.distance_id == self.SPORTA_DISTANCE_ID:
            point_list.pop(3)  # 4.stage is not taken because it is UCI category

        point_list = filter(None, point_list)  # remove None from list
        setattr(standing, 'points_total', sum(point_list))

        standing.save()

        # Log information about calculated values
        Log.objects.create(content_object=team, action="Recalculated team standing", params={
            'points_total': standing.points_total,
            'points%i' % self.competition_index: getattr(standing, 'points%i' % self.competition_index)
        })

        return standing

    def _participant_standings_points(self, standing, distance=False):
        """
        This is private function that calculates points for participant based on distance.
        """
        stages = range(1, self.STAGES_COUNT+1)

        #if standing.distance_id == self.SPORTA_DISTANCE_ID:
        #    stages.remove(4)  # 4.stage is not taken because it is UCI category
        if distance:
            points = sorted((getattr(standing, 'distance_points%i' % stage) for stage in stages), reverse=True)
        else:
            points = sorted((getattr(standing, 'group_points%i' % stage) for stage in stages), reverse=True)

        return sum(points[0:5])


    def recalculate_standing_points(self, standing):
        """
        This function recalculates distance and group total points for provided standing.
        If standing is children distance, then distance total is not calculated.
        """
        if standing.distance_id != self.BERNU_DISTANCE_ID:  # Children competition doesn't have distance_total
            standing.distance_total = self._participant_standings_points(standing, distance=True)
        standing.group_total = self._participant_standings_points(standing)

    def recalculate_standing_for_result(self, result):
        """
        This function received result in input and assigned result to standing object.
        Afterwards function calls recalculate_standing_points to recalculate points for standing
        """
        if not result.standings_object:
            print(result.id)
            standing, created = SebStandings.objects.get_or_create(competition=result.competition.parent, participant_slug=result.participant.slug, distance=result.participant.distance, defaults={'participant': result.participant})
            result.standings_object = standing
            result.save()
        else:
            standing = result.standings_object
        standing.set_points()
        self.recalculate_standing_points(standing)
        standing.save()

        if result.participant.team:
            self.recalculate_team_result(team=result.participant.team)


    def recalculate_standing_for_results(self):
        """
        Function iterates through all results and recalculates standings.
        """
        all_results = Result.objects.filter(competition=self.competition)
        for result in all_results:
            self.recalculate_standing_for_result(result)

        self.assign_standing_places()  # Reassign places

    def assign_standing_places(self):
        """
        Function iterates through all standings and assign place based on total points, total seconds and points in last stage
        """
        cursor = connection.cursor()

        # TODO: Exclude children from assigning distance place

        # First assign distance place
        cursor.execute("""
        UPDATE
            results_sebstandings r
        SET
            distance_place = res2.distance_row_nr,
            group_place = res2.group_row_nr
        FROM
        (
        Select res.id, res.competition_id, res.distance_id, res.group_total, res.distance_total,
        row_number() OVER (PARTITION BY res.competition_id, res.distance_id ORDER BY
        res.distance_id, res.distance_total desc,
        res.distance_points7 desc, res.distance_points6 desc, res.distance_points5 desc, res.distance_points4 desc,
        res.distance_points3 desc, res.distance_points2 desc, res.distance_points1 desc) as distance_row_nr,
        row_number() OVER (PARTITION BY res.competition_id, res.distance_id, p.group ORDER BY
        res.distance_id, p.group, res.group_total desc, res.group_points7 desc, res.group_points6 desc, res.group_points5 desc,
        res.group_points4 desc, res.group_points3 desc, res.group_points2 desc, res.group_points1 desc
        ) as group_row_nr
        FROM results_sebstandings As res
        INNER JOIN registration_participant p ON res.participant_id = p.id
        ) res2
        WHERE res2.competition_id = %s AND r.id = res2.id
        """, [self.competition.parent.id, ])


    def recalculate_all_standings(self):
        """
        ===== MAIN FUNCTION =====
        Function recalculates all standings for current competition. Function recalculates team results also.
        """
        if self.competition.level == 2:  # if class is called with stage competition, then recalculate all results
            self.recalculate_standing_for_results()
            self.recalculate_team_results()  # Recalculate team total points for current competition
        else:
            pass  # TODO: Create team point recalculation for all stages at the same time


    def process_chip_create_participant(self, chip):
        participant = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)
        if not participant:
            participant_data = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_all_children_ids(), distance=chip.nr.distance, is_participating=True).order_by('-competition__id')
            if participant_data:
                participant_data = participant_data.values()[0]
                # TODO: Refresh list
                for pop_element in ['id', 'application_id', 'comment', 'created', 'created_by_id', 'insurance_id', 'legacy_id', 'modified', 'modified_by_id', 'price_id', 'registrant_id', 'is_sent_number_sms', 'is_sent_number_email', 'registration_dt']:
                    participant_data.pop(pop_element)

                participant_data.update({'is_temporary': True, 'competition_id': chip.competition.id, })

                participant = [Participant.objects.create(**participant_data), ]
                Log.objects.create(content_object=participant[0], action="Chip process", message="Participant was not found, so created temporary one based on previous stage data.")
                print('Created participant with ID %i' % participant[0].id)
            else:
                return False
        return participant

    def process_chip_result(self, chip_id, sendsms=True):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        result_time, seconds = self.calculate_time(chip)

        # Do not process if finished in 10 minutes.
        if seconds < 10 * 60: # 10 minutes
            Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
            return None

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        results = Result.objects.filter(competition=chip.competition, number=chip.nr).exclude(time=None)
        if results:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip ignored. Already have result")
        else:
            participant = self.process_chip_create_participant(chip)
            if participant:
                result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant[0], number=chip.nr, )
                result.time = result_time
                result.set_all()
                result.save()

                # Update standings... Asynchronously
                recalculate_standing_for_result.delay(self.competition_id, result.id)

                # To send out SMS we need place set.
                self.assign_result_place()

                if sendsms:
                    create_result_sms(result.id)

            else:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")

        print(chip)


    def recalculate_all_points(self):
        """
        MAIN FUNCTION FROM MANAGER
        This function is called from manager view to manually recalculate points.
        This function is called in case there are errors in given points.
        """
        distances = [self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.VESELIBAS_DISTANCE_ID]
        recalculate_places = False
        results = Result.objects.filter(competition=self.competition, participant__distance_id__in=distances)
        for result in results:
            print(result.id)
            if result.set_all():
                recalculate_places = True
                result.save()
            self.recalculate_standing_for_result(result)

        if recalculate_places:
            self.assign_standing_places()
            self.recalculate_team_results()

        self.assign_result_place()

    def calculate_points_distance(self, result, top_result=None):
        """
        Function used to calculate distance points
        """
        if result.number.distance_id == self.BERNU_DISTANCE_ID:
            return result.points_distance  # For children lets return the same number.

        if result.status:  # If result has the status then that means that result is 0
            return 0

        if not top_result:
            try:
                top_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance).exclude(time=None).order_by('time')[0]
            except IndexError:
                return 1000

        if result.time is None:
            return 0

        return math.trunc((float(math.trunc(time_to_seconds(top_result.time))) / float(math.trunc(time_to_seconds(result.time)))) * 1000)

    def calculate_points_group(self, result):
        """
        Function used to recalculate group points
        """
        if result.number.distance_id == self.BERNU_DISTANCE_ID:
            return result.points_group  # For children lets return the same number.

        if result.status:
            return 0

        try:
            top_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance, participant__group=result.participant.group, status='').exclude(time=None).order_by('time')[0]
        except IndexError:
            return 1000

        if result.time is None:
            return 0

        return math.trunc((float(math.trunc(time_to_seconds(top_result.time))) / float(math.trunc(time_to_seconds(result.time)))) * 1000)

    def get_result_table_class(self, distance, group=None):
        if distance.id == self.BERNU_DISTANCE_ID:  # children distance
            return ResultChildrenGroupTable
        if group:
            return ResultGroupTable
        else:
            return ResultDistanceTable

    def get_standing_table_class(self, distance, group=None):
        if distance.id == self.BERNU_DISTANCE_ID:  # children distance
            return ResultChildrenGroupStandingTable
        if group:
            return ResultGroupStandingTable
        else:
            return ResultDistanceStandingTable




    def assign_result_place(self):
        """
        Assign result place based on result time. Optimized to use raw SQL.
        """
        cursor = connection.cursor()

        # First assign distance place
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = res2.distance_row_nr,
    result_group = res2.group_row_nr
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing, p.distance_id,
row_number() OVER (PARTITION BY res.competition_id, nr.distance_id ORDER BY nr.distance_id, res.status asc, res.time, res.id) as distance_row_nr,
row_number() OVER (PARTITION BY res.competition_id, nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status asc, res.time, res.id) as group_row_nr
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
WHERE p.is_competing is true and res.time IS NOT NULL
) res2
WHERE res2.competition_id = %s and res2.distance_id <> %s and res2.time IS NOT NULL and res2.is_competing is true
AND r.id = res2.id
""", [self.competition_id, self.BERNU_DISTANCE_ID])
        # Then unset places to others
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = NULL,
    result_group = NULL
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing, p.distance_id
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
) res2
WHERE res2.competition_id = %s and res2.distance_id <> %s and (res2.time IS NULL or res2.is_competing is false)
AND r.id = res2.id
""", [self.competition_id, self.BERNU_DISTANCE_ID])


    def assign_passage(self, reset=False):
        if self.competition.level != 2:
            raise Exception('We allow assigning passages only for stages.')

        if reset:
            HelperResults.objects.filter(competition=self.competition).update(passage_assigned=None)

        update_helper_result_table(self.competition_id, update=True)

        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            helperresults = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None).select_related('participant').order_by('-calculated_total', 'participant__registration_dt')
            for passage_nr, total, passage_extra in self.passages.get(distance_id):
                specials = [obj.participant_slug for obj in PreNumberAssign.objects.filter(competition=self.competition, distance_id=distance_id).filter(segment=passage_nr)]
                # Assign passage for specials
                HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, participant__slug__in=specials, passage_assigned=None).update(passage_assigned=passage_nr)

                places = total - passage_extra

                for result in helperresults[0:places]:
                    result.passage_assigned = passage_nr
                    result.save()

                # Exceptions

                # In 1.stage 10 girls and 50 women that are not in first 3 passages will be assigned to 4.passage
                if passage_nr == 4 and self.competition_index == 1 and distance_id == self.TAUTAS_DISTANCE_ID:
                    girls = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('W-16', 'T W-18')).order_by('-calculated_total', 'participant__registration_dt')[0:10]
                    for _ in girls:
                        _.passage_assigned = passage_nr
                        _.save()
                    women = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('T W', 'T W-35', 'T W-45')).order_by('-calculated_total', 'participant__registration_dt')[0:50]
                    for _ in women:
                        _.passage_assigned = passage_nr
                        _.save()


    def assign_numbers_continuously(self):
        self.assign_numbers(reassign=False, assign_special=False)


    def assign_numbers(self, reassign=False, assign_special=False, assign_children=True):

        # Update helper results before assigning
        update_helper_result_table(self.competition_id, update=True)

        if self.competition.level != 2:
            raise Exception('We allow assigning numbers only for stages.')

        if reassign:
            Number.objects.filter(competition_id__in=self.competition.get_ids()).update(participant_slug='', number_text='')
            Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True).update(primary_number=None)

        parent_competition = self.competition.parent

        if assign_special:
            # first assign special numbers
            pre_numbers = PreNumberAssign.objects.filter(competition_id__in=self.competition.get_ids()).exclude(number=None)
            for nr in pre_numbers:
                number = Number.objects.get(number=nr.number, competition=parent_competition, distance=nr.distance)
                print("%s - %s" % (number, nr.participant_slug))
                number.participant_slug = nr.participant_slug
                number.save()
                Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance=number.distance, slug=number.participant_slug).update(primary_number=number)


        helperresults = HelperResults.objects.filter(competition=self.competition, participant__is_participating=True, participant__primary_number=None).select_related('participant').order_by('participant__distance', '-calculated_total', 'participant__registration_dt')

        for result in helperresults:
            participant = result.participant

            if not assign_children and participant.distance_id == self.BERNU_DISTANCE_ID:
                continue

            if participant.distance_id == self.VESELIBAS_DISTANCE_ID and participant.birthday.year not in (2001, 2002, 2003):
                continue # In Helth distance we assign only to those participants that have born on 2001, 2002, 2003

            group = self.get_group_for_number_search(participant.distance_id, participant.gender, participant.birthday)
            try:
                number = Number.objects.get(participant_slug=participant.slug, distance=participant.distance, group=group)
                if not participant.primary_number:
                    participant.primary_number = number
                    participant.save()
            except:
                order_by = 'number'
                if participant.group in self.groups[self.BERNU_DISTANCE_ID][:2] and participant.gender == 'M':
                    order_by = '-number'

                next_number = Number.objects.filter(participant_slug='', distance=participant.distance, group=group).order_by(order_by)[0]
                next_number.participant_slug = participant.slug
                next_number.number_text = str(participant.registration_dt)
                print("%s - %s" % (next_number, participant.slug))
                next_number.save()
                participant.primary_number = next_number
                participant.save()

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
        if not isinstance(birthday, datetime.date) and birthday:
            try:
                birthday = datetime.datetime.strptime(birthday, "%Y-%m-%d").date()
            except:
                return 'error-no-group'

        if distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.VESELIBAS_DISTANCE_ID):
            return ''
        elif distance_id == self.BERNU_DISTANCE_ID:
            try:
                return self.assign_group(distance_id, gender, birthday)
            except:
                return 'error-no-group'



    def import_children_csv(self, filename): # berni1p14.xls

        result_column = 7 + (self.competition_index * 3)

        with open(filename, 'rb') as csvfile:
            results = csv.reader(csvfile)
            results.next()  # header line
            for row in results:
                assign_number = False

                slug = slugify("%s-%s-%s" % (row[2].decode('utf-8'), row[3].decode('utf-8'), row[4].decode('utf-8')))
                print(row)
                participant = Participant.objects.filter(slug=slug, competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=self.BERNU_DISTANCE_ID)
                if participant:
                    participant = participant.get()
                else:
                    data = {
                        'competition_id': self.competition_id,
                        'distance_id': self.BERNU_DISTANCE_ID,
                        'team_name': row[6].decode('utf-8'),
                        'is_participating': True,
                        'first_name': row[2].decode('utf-8'),
                        'last_name': row[3].decode('utf-8'),
                        'birthday': datetime.date(int(row[4]), 1, 1),
                        'is_only_year': True,
                        'phone_number': row[8],
                        'gender': '',
                    }
                    if row[7]:
                        try:
                            data.update({'bike_brand2': row[7], })
                        except:
                            pass

                    if row[5] == 'B 05-04 M':
                        data.update({'gender': 'W'})
                    elif row[5] == 'B 05-04 Z':
                        data.update({'gender': 'M'})

                    participant = Participant.objects.create(**data)

                number_group = participant.group
                if number_group in ('B 05-04 M', 'B 05-04 Z'):
                    number_group = 'B 05-04'
                # Assign number
                number = Number.objects.filter(competition=self.competition.parent, distance_id=self.BERNU_DISTANCE_ID, number=row[1], group=number_group).order_by('-id')
                number.update(participant_slug=participant.slug)
                if number:
                    participant.primary_number = number.get()
                    participant.save()

                if row[result_column]:
                    result, created = Result.objects.get_or_create(competition=self.competition, participant=participant, number=number.get(), result_group=row[result_column] if row[result_column] else None, points_group=row[result_column+1] if row[result_column+1] else 0, status=row[result_column-1])
                    self.recalculate_standing_for_result(result)
                else:
                    print('didnt participate')
        self.assign_standing_places()
