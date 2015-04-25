# coding=utf-8
from __future__ import unicode_literals
import datetime
import math
import csv
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
from django.db import connection
from sitetree.utils import item
from core.models import Competition, Log, Choices
from registration.models import Number, Participant, PreNumberAssign
from django.core.cache import cache
from registration.tables import ParticipantTable
from results.helper import time_to_seconds
from results.models import Result, DistanceAdmin, ChipScan, SebStandings, TeamResultStandings, LapResult, HelperResults
from results.tables import ResultChildrenGroupTable, ResultGroupTable, ResultDistanceTable, \
    ResultChildrenGroupStandingTable, ResultGroupStandingTable, ResultDistanceStandingTable, ResultRMGroupTable, \
    ResultRMSportsDistanceTable, ResultRMTautaDistanceTable
from results.tasks import create_result_sms, recalculate_standing_for_result
from team.models import MemberApplication, Team
from django.template.defaultfilters import slugify


class CompetitionScriptBase(object):
    competition_id = None
    competition = None

    def __init__(self, competition_id=None, competition=None):
        if not competition_id and not competition:
            raise Exception('At least one variable is required.')

        self.competition = competition or Competition.objects.get(id=competition_id)
        self.competition_id = self.competition.id

    def assign_group(self, distance_id, gender, birthday):
        raise NotImplementedError()

    def number_ranges(self):
        raise NotImplementedError()

    def generate_diploma(self, result):
        raise NotImplementedError()

    def apply_number_ranges(self):
        assert self.competition_id is not None
        ranges = self.number_ranges()
        for distance_id in ranges:
            numbers = ranges.get(distance_id)
            for number_dict in numbers:
                for number in range(number_dict.get('start'), number_dict.get('end')):
                    print Number.objects.get_or_create(competition_id=self.competition_id, group=number_dict.get('group', ''), distance_id=distance_id, number=number, defaults={'status': 1})


    def reset_cache(self):
        cache.delete('sitetrees')
        cache.delete('tree_aliases')
        # TODO: Add all other caches that are added manually

    def calculate_points_distance(self, result):
        return 0

    def calculate_points_group(self, result):
        return 0

    def build_flat_pages(self, competition, items):
        for page in competition.flatpage_set.filter(is_published=True):
            items.append(item(page.title, 'competition:flatpage %i %s' % (competition.id, page.url)))


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
            child_items.append(item(unicode(child), 'manager:competition %i' % child.id, access_loggedin=True, children=children))


        return item(unicode(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu, access_loggedin=True)

    def build_menu(self):
        current_date = datetime.date.today()
        child_items = [
            item('Atbalstītāji', 'competition:supporters %i' % self.competition.id),
            item('Komandas', 'competition:team %i' % self.competition.id, children=[
                item('{{ object }}', 'competition:team %i object.id' % self.competition.id, in_menu=False),
            ]),
            item('Kopvērtējums', 'competition:standings_list %i' % self.competition.id),
            item('Komandu kopvērtējums', 'competition:team_standings_list %i' % self.competition.id)
        ]
        self.build_flat_pages(self.competition, child_items)
        last = False
        for child in self.competition.get_children():
            if last:
                break
            if child.competition_date > current_date:
                last = True

            children = []
            children.append(item('Starta saraksts', 'competition:participant_list %i' % child.id))
            children.append(item('Pieteiktās komandas', 'competition:applied_teams_list %i' % child.id))
            children.append(item('Kartes', 'competition:maps %i' % child.id))
            self.build_flat_pages(child, children)

            if child.competition_date <= current_date:
                children.append(item('Rezultāti', 'competition:result_distance_list %i' % child.id))
                children.append(item('Komandu rezultāti', 'competition:result_team_list %i' % child.id))

            child_items.append(item(unicode(child), '#', url_as_pattern=False, children=children))

        return item(unicode(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu)

    def get_startlist_table_class(self, distance=None):
        return ParticipantTable


    def recalculate_team_results(self):
        """
        Function to recalculate all team results for current competition.
        """
        teams = Team.objects.filter(member__memberapplication__competition=self.competition, member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT).order_by('id').distinct('id')
        for team in teams:
            print team.id
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

    def _participant_standings_points(self, standing, distance=False):
        """
        This is private function that calculates points for participant based on distance.
        """
        stages = range(1, self.STAGES_COUNT+1)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            stages.remove(4)  # 4.stage is not taken because it is UCI category
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
            standing, created = SebStandings.objects.get_or_create(competition=result.competition.parent, participant_slug=result.participant.slug, distance=result.number.distance, defaults={'participant': result.participant})
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
        row_number() OVER (PARTITION BY res.distance_id ORDER BY
        res.distance_id, res.distance_total desc,
        res.distance_points7 desc, res.distance_points6 desc, res.distance_points5 desc, res.distance_points4 desc,
        res.distance_points3 desc, res.distance_points2 desc, res.distance_points1 desc) as distance_row_nr,
        row_number() OVER (PARTITION BY res.distance_id, p.group ORDER BY
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


    def process_chip_result(self, chip_id, sendsms=True):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        seconds = result_time.hour * 60 * 60 + result_time.minute * 60 + result_time.second

        # Do not process if finished in 10 minutes.
        if seconds < 10 * 60: # 10 minutes
            Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
            return None

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        results = Result.objects.filter(competition=chip.competition, number=chip.nr)
        if results:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip ignored. Already have result")
        else:
            participant = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)
            if not participant:
                participant_data = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_all_children_ids(), distance=chip.nr.distance, is_participating=True).order_by('-competition__id')
                if participant_data:
                    participant_data = participant_data.values()[0]
                    # TODO: Refresh list
                    for pop_element in ['id', 'application_id', 'comment', 'created', 'created_by_id', 'insurance_id', 'legacy_id', 'modified', 'modified_by_id', 'price_id', 'registrant_id', 'is_sent_number_sms', 'is_sent_number_email', ]:
                        participant_data.pop(pop_element)

                    participant_data.update({'is_temporary': True, 'competition_id': chip.competition.id, })

                    participant = [Participant.objects.create(**participant_data), ]
                    Log.objects.create(content_object=participant[0], action="Chip process", message="Participant was not found, so created temporary one based on previous stage data.")
                    print 'Created participant with ID %i' % participant[0].id
                else:
                    return False
            if participant:
                result = Result.objects.create(competition=chip.competition, participant=participant[0], number=chip.nr, time=result_time, )
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

        print chip


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
            print result.id
            if result.set_all():
                recalculate_places = True
                result.save()
            self.recalculate_standing_for_result(result)

        if recalculate_places:
            self.assign_standing_places()
            self.recalculate_team_results()

    def calculate_points_distance(self, result):
        """
        Function used to calculate distance points
        """
        if result.number.distance_id == self.BERNU_DISTANCE_ID:
            return result.points_distance  # For children lets return the same number.

        if result.status:  # If result has the status then that means that result is 0
            return 0

        try:
            top_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance).order_by('time')[0]
        except IndexError:
            return 1000

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
            top_result = Result.objects.filter(competition=result.competition, number__distance=result.number.distance, participant__group=result.participant.group).order_by('time')[0]
        except IndexError:
            return 1000

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
Select res.id, result_distance, res.competition_id, res.time, p.is_competing,
row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
WHERE p.is_competing is true and res.time IS NOT NULL
) res2
WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
AND r.id = res2.id
""", [self.competition_id, ])
        # Then unset places to others
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = NULL
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
) res2
WHERE res2.competition_id = %s and (res2.time IS NULL or res2.is_competing is false)
AND r.id = res2.id
""", [self.competition_id, ])

        cursor.execute("""
UPDATE
    results_result r
SET
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
            return Exception('We allow assigning passages only for stages.')

        if reset:
            HelperResults.objects.filter(competition=self.competition).update(passage_assigned=None)

        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            helperresults = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None).select_related('participant').order_by('-calculated_total', 'participant__registration_dt')
            for passage_nr, total, passage_extra in self.passages.get(distance_id):
                specials = [obj.participant_slug for obj in PreNumberAssign.objects.filter(competition=self.competition, distance_id=distance_id).filter(segment=passage_nr)]
                # Assign passage for specials
                HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, participant__slug__in=specials, passage_assigned=None).update(passage_assigned=passage_nr)

                specials_not_vip_count = PreNumberAssign.objects.filter(competition=self.competition, distance_id=distance_id).filter(segment=passage_nr).exclude(description__icontains='vip').count()

                places = total - specials_not_vip_count - passage_extra

                for result in helperresults[0:places]:
                    result.passage_assigned = passage_nr
                    result.save()

                # Exceptions

                # In 1.stage all women will be starting from 3.passage (except those with better results and already in better passage)
                if passage_nr == 3 and self.competition_index == 1 and distance_id == self.SPORTA_DISTANCE_ID:
                    women = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__gender='F').order_by('-calculated_total', 'participant__registration_dt')
                    women.update(passage_assigned=passage_nr)

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


    def assign_numbers(self, reassign=False, assign_special=False):

        if self.competition.level != 2:
            return Exception('We allow assigning numbers only for stages.')

        if reassign:
            Number.objects.filter(competition_id__in=self.competition.get_ids()).update(participant_slug='', number_text='')
            Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True).update(primary_number=None)

        parent_competition = self.competition.parent

        if assign_special:
            # first assign special numbers
            pre_numbers = PreNumberAssign.objects.filter(competition_id__in=self.competition.get_ids()).exclude(number=None)
            for nr in pre_numbers:
                number = Number.objects.get(number=nr.number, competition=parent_competition, distance=nr.distance)
                print "%s - %s" % (number, nr.participant_slug)
                number.participant_slug = nr.participant_slug
                number.save()
                Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance=number.distance, slug=number.participant_slug).update(primary_number=number)


        helperresults = HelperResults.objects.filter(competition=self.competition, participant__is_participating=True, participant__primary_number=None).select_related('participant').order_by('participant__distance', '-calculated_total', 'participant__registration_dt')

        for result in helperresults:
            participant = result.participant

            if participant.distance_id == self.VESELIBAS_DISTANCE_ID and participant.birthday.year not in (2001, 2002, 2003):
                continue # In Helth distance we assign only to those participants that have born on 2001, 2002, 2003

            group = self.get_group_for_number_search(participant.distance_id, participant.gender, participant.birthday)
            try:
                number = Number.objects.get(participant_slug=participant.slug, distance=participant.distance, group=group)
                if not participant.primary_number:
                    participant.primary_number = number
                    participant.save()
            except:
                next_number = Number.objects.filter(participant_slug='', distance=participant.distance, group=group).order_by('number')[0]
                next_number.participant_slug = participant.slug
                next_number.number_text = str(participant.registration_dt)
                print "%s - %s" % (next_number, participant.slug)
                next_number.save()
                participant.primary_number = next_number
                participant.save()

    def get_group_for_number_search(self, distance_id, gender, birthday):
        if not isinstance(birthday, datetime.date):
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
        with open(filename, 'rb') as csvfile:
            results = csv.reader(csvfile)
            results.next()  # header line
            for row in results:
                slug = slugify("%s-%s-%s" % (row[1].decode('utf-8'), row[2].decode('utf-8'), row[3].decode('utf-8')))
                print row
                participant = Participant.objects.filter(slug=slug, competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=self.BERNU_DISTANCE_ID)
                if participant:
                    participant = participant.get()
                else:
                    data = {
                        'competition_id': self.competition_id,
                        'distance_id': self.BERNU_DISTANCE_ID,
                        'team_name': row[5].decode('utf-8'),
                        'is_participating': True,
                        'first_name': row[1].decode('utf-8'),
                        'last_name': row[2].decode('utf-8'),
                        'birthday': datetime.date(int(row[3]), 1, 1),
                        'is_only_year': True,
                        'phone_number': row[7],
                        'gender': '',
                    }
                    if row[7]:
                        try:
                            data.update({'bike_brand2': row[6], })
                        except:
                            pass
                    participant = Participant.objects.create(**data)

                # Assign number
                number = Number.objects.filter(competition=self.competition.parent, distance_id=self.BERNU_DISTANCE_ID, number=row[0], group=participant.group).order_by('-id')
                print number.update(participant_slug=participant.slug)
                if number:
                    participant.primary_number = number[0]
                    participant.save()

                if row[27]:
                    result, created = Result.objects.get_or_create(competition=self.competition, participant=participant, number=number.get(), result_group=row[27] if row[27] else None, points_group=row[28] if row[28] else 0, status=row[26])
                    self.recalculate_standing_for_result(result)
                else:
                    print 'didnt participate'
        self.assign_standing_places()




class RMCompetitionBase(CompetitionScriptBase):
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('Jaunieši', 'Jaunietes', 'Juniori', 'Juniores', 'Vīrieši', 'Sievietes', 'Sievietes II', 'Seniori I', 'Seniori II', 'Veterāni I', 'Veterāni II'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def assign_group(self, distance_id, gender, birthday):
        return NotImplementedError

    def build_manager_menu(self):
        child_items = []
        # for child in self.competition.get_children():
        #     children = []
        #     children.append(item('Dalībnieki', '#', url_as_pattern=False, access_loggedin=True, children=[
        #         item('Pieteikt dalībnieku', 'manager:participant_create %i' % child.id, access_loggedin=True),
        #         item('Dalībnieku saraksts', 'manager:participant_list %i' % child.id, access_loggedin=True),
        #         item('{{ object }}', 'manager:participant %i object.id' % child.id, in_menu=False, access_loggedin=True),
        #     ]))
        return item(unicode(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu, access_loggedin=True)


    def build_menu(self):
        current_date = datetime.date.today()
        child_items = [
            item('Atbalstītāji', 'competition:supporters %i' % self.competition.id),
            item('Komandas', 'competition:team %i' % self.competition.id, children=[
                item('{{ object }}', 'competition:team %i object.id' % self.competition.id, in_menu=False),
            ]),
            item('Starta saraksts', 'competition:participant_list %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items)
        if self.competition.map_set.count():
            child_items.append(item('Kartes', 'competition:maps %i' % self.competition.id))

        if self.competition.competition_date <= current_date:
            child_items.append(item('Rezultāti', 'competition:result_distance_list %i' % self.competition.id))
            child_items.append(item('Komandu rezultāti', 'competition:result_team_by_name %i' % self.competition.id))
        return item(unicode(self.competition), '#', url_as_pattern=False, children=child_items, in_menu=self.competition.is_in_menu)


    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 900, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 5000, 'group': ''}, ],
        }

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 201, 400, 0), (2, 401, 600, 0), (3, 601, 800, 0)],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 5),
                                    (2, 2201, 2400, 30),
                                    (3, 2401, 2600, 20),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3400, 10),
                                    (8, 3401, 3600, 10),
                                    (9, 3601, 3800, 10),
                                    (10, 3801, 4000, 10),
                                    (11, 4001, 4200, 10),
                                    (12, 4201, 4400, 10),
                                    (13, 4401, 4600, 10),
                                    (14, 4601, 4800, 10),
                                    (15, 4801, 5000, 10),
                                    ],
        }


    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            if distance.id == self.SPORTA_DISTANCE_ID:
                return ResultRMSportsDistanceTable
            else:
                return ResultRMTautaDistanceTable

    def get_startlist_table_class(self, distance=None):
        return ParticipantTable


    def assign_numbers_continuously(self):
        return NotImplementedError

    def get_group_for_number_search(self, distance_id, gender, birthday):
            return ''


    def recalculate_team_results(self):
        raise NotImplementedError
        """
        Function to recalculate all team results for current competition.
        """
        teams = Team.objects.filter(member__memberapplication__competition=self.competition, member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT).order_by('id').distinct('id')
        for team in teams:
            print team.id
            self.recalculate_team_result(team=team)

    def recalculate_team_result(self, team_id=None, team=None):
        raise NotImplementedError
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

    def _participant_standings_points(self, standing, distance=False):
        raise NotImplementedError
        """
        This is private function that calculates points for participant based on distance.
        """
        stages = range(1, self.STAGES_COUNT+1)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            stages.remove(4)  # 4.stage is not taken because it is UCI category
        if distance:
            points = sorted((getattr(standing, 'distance_points%i' % stage) for stage in stages), reverse=True)
        else:
            points = sorted((getattr(standing, 'group_points%i' % stage) for stage in stages), reverse=True)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            return sum(points[0:4])
        elif standing.distance_id == self.TAUTAS_DISTANCE_ID:
            return sum(points[0:5])
        elif standing.distance_id == self.BERNU_DISTANCE_ID:
            return sum(points[0:5])

    def process_chip_result(self, chip_id, sendsms=True):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)


        zero_minus_10secs = (datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.timedelta(seconds=10)).time()
        if chip.time < zero_minus_10secs:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip scanned before start")
            return False

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        result_time_5back = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(minutes=5)).time()
        if result_time_5back > result_time:
            result_time_5back = datetime.time(0,0,0)
        result_time_5forw = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta + datetime.timedelta(minutes=5)).time()

        if chip.is_blocked:  # If blocked, then remove result, recalculate standings, recalculate team results
            raise NotImplementedError
            results = Result.objects.filter(competition=chip.competition, number=chip.nr, time=result_time)
            if results:
                result = results[0]
                participant = result.participant
                if result.standings_object:
                    standing = result.standings_object
                    result.delete()
                    self.recalculate_standing(standing)  # Recalculate standings for this participant
                    standing.save()
                    if participant.team:  # If blocked participant was in a team, then recalculate team results.
                        self.recalculate_team_result(team=participant.team)
                Log.objects.create(content_object=chip, action="Chip process", message="Processed blocked chip")
            return None
        elif chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        try:
            participant = Participant.objects.get(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)
        except Participant.DoesNotExist:
            Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")
            return False

        try:
            result = Result.objects.get(competition=chip.competition, number=chip.nr)

            zero_time_update = Result.objects.filter(competition=chip.competition, number=chip.nr, zero_time__gte=result_time_5back, zero_time__lte=result_time_5forw)
            if zero_time_update:
                zero_time_update.update(zero_time=result_time)
                Log.objects.create(content_object=chip, action="Chip process", message="Lets update zero time")
            else:
                already_exists_result = LapResult.objects.filter(result=result, time__gte=result_time_5back, time__lte=result_time_5forw)
                if already_exists_result:
                    Log.objects.create(content_object=chip, action="Chip process", message="Chip double scanned.")
                else:
                    laps_done = LapResult.objects.filter(result=result).count()
                    LapResult.objects.create(result=result, index=(laps_done+1), time=result_time)
                    if (chip.nr.distance_id == self.SPORTA_DISTANCE_ID and laps_done == 4) or (chip.nr.distance_id == self.TAUTAS_DISTANCE_ID and laps_done == 1):
                        Log.objects.create(content_object=chip, action="Chip process", message="DONE. Lets assign avg speed.")
                        result.time = result_time
                        result.set_avg_speed()
                        result.save()
                        if participant.is_competing and self.competition.competition_date == datetime.date.today():
                            create_result_sms(result.id)

        except Result.DoesNotExist:
            Log.objects.create(content_object=chip, action="Chip process", message="Lets set zero time")
            Result.objects.create(competition=chip.competition, participant=participant, number=chip.nr, zero_time=result_time, )


        chip.is_processed = True
        chip.save()


        print chip


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
Select res.id, result_distance, res.competition_id, res.time, p.is_competing,
row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
WHERE p.is_competing is true and res.time IS NOT NULL
) res2
WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
AND r.id = res2.id
""", [self.competition_id, ])
        # Then unset places to others
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = NULL,
    result_group = NULL
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
) res2
WHERE res2.competition_id = %s and (res2.time IS NULL or res2.is_competing is false)
AND r.id = res2.id
""", [self.competition_id, ])


    def recalculate_standing_for_result(self, result):
        pass  # TODO: recalculate if group is changed.

    def assign_standing_places(self):
        self.assign_result_place()
        self.reset_cache_results()

    def reset_cache(self):
        cache.clear()  # This cleans all cache.
        return True
        # Reset team results.
        self.reset_cache_results()

        super(RM2014, self).reset_cache()


    def reset_cache_results(self):
        for lang_key, lang_name in settings.LANGUAGES:
            for distance in self.competition.get_distances():
                cache_key = make_template_fragment_key('results_team_by_teamname', [lang_key, self.competition, distance])
                cache.delete(cache_key)
        for distance in self.competition.get_distances():
            cache.delete('team_results_by_name_%i_%i' % (self.competition.id, distance.id))


    def process_unprocessed_chips(self, send_sms=False):
        for chip in self.competition.chipscan_set.filter(is_processed=False).order_by('time'):
            self.process_chip_result(chip.id, send_sms)

    def generate_diploma(self, result):
        raise NotImplementedError


    def assign_numbers(self, reassign=False, assign_special=False):
        if reassign:
            Number.objects.filter(competition=self.competition).update(participant_slug='', number_text='')
            Participant.objects.filter(competition=self.competition, is_participating=True).update(primary_number=None)

        if assign_special:
            # first assign special numbers
            special = {
                # moved to database # TODO: rebuild querying for this data from database
            }
            for nr in special:
                slug = special.get(nr)
                number = Number.objects.get(number=nr, competition=self.competition)
                print "%s - %s" % (number, slug)
                number.participant_slug = slug
                number.save()

                participant = Participant.objects.filter(slug=slug, competition=self.competition, distance=number.distance, is_participating=True)
                if participant:
                    participant = participant[0]
                    participant.primary_number = number
                    participant.save()

        special_passages = {
            # moved to database # TODO: rebuild querying for this data from database
        }

        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):


            for passage_nr, passage_start, passage_end, passage_extra in self.passages().get(distance_id):
                special_in_passage = [val for val in special.keys() if val>=passage_start and val<=passage_end]
                places = passage_end - passage_start - passage_extra + 1 - len(special_in_passage)

                passage = special_passages.get(distance_id)

                slugs_in_passage = [key for key in passage if passage.get(key) == passage_nr]

                # Filter those slugs that already have number:
                final_slugs_in_passage = slugs_in_passage[:]
                for slug in slugs_in_passage:
                    if Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, slug=slug).exclude(primary_number=None):
                        print 'removing slug %s' % slug
                        final_slugs_in_passage.remove(slug)

                participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, primary_number=None).order_by('legacyresult__result_distance', 'created')[:places]
                participant_slugs = [obj.slug for obj in participants]

                extra_count = 0
                slugs_in_passage = final_slugs_in_passage[:]
                for slug in slugs_in_passage:
                    if slug in participant_slugs:
                        print 'FOUND %s' % slug
                        final_slugs_in_passage.remove(slug)
                    else:
                        print 'not in'
                        extra_count += 1


                final_slugs = [obj.slug for obj in participants[:places-extra_count]] + final_slugs_in_passage

                final_numbers = [nr for nr in range(passage_start, passage_end+1) if Number.objects.filter(number=nr, competition=self.competition, participant_slug='')]


                for nr, slug in zip(final_numbers, final_slugs):
                    print '%i - %s' % (nr, slug)
                    number = Number.objects.get(number=nr, competition=self.competition, participant_slug='')
                    number.participant_slug = slug
                    number.save()
                    participant = Participant.objects.filter(slug=slug, competition=self.competition, distance=number.distance, is_participating=True)
                    if participant:
                        participant = participant[0]
                        participant.primary_number = number
                        participant.save()

