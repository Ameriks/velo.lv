# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.db.models import Count
from django.template.defaultfilters import slugify
import math
import csv
from django.core.cache import cache
from sitetree.utils import item
from core.models import Competition, Choices, Log
from registration.competition_classes.base import CompetitionScriptBase
from registration.models import Number, Participant
from registration.tables import ParticipantTable
from results.models import LegacySEBStandingsResult, ChipScan, Result, DistanceAdmin, SebStandings, TeamResultStandings
from results.tables import *
from results.tables import ResultDistanceStandingTable
from results.tasks import send
from results.helper import time_to_seconds
from team.models import Team, MemberApplication


class Seb2014(CompetitionScriptBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 24
    TAUTAS_DISTANCE_ID = 25
    BERNU_DISTANCE_ID = 27

    STAGES_COUNT = 7

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-14', 'M-16', 'T M-18', 'T M', 'T M-35', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
            self.BERNU_DISTANCE_ID: ('B 03-02', 'B 05-04', 'B 06', 'B 07', 'B 08', 'B 09', 'B 10-', )
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 350, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 500, 'end': 3500, 'group': ''}, ],
            self.BERNU_DISTANCE_ID: [{'start': 1, 'end': 100, 'group': group} for group in self.groups.get(self.BERNU_DISTANCE_ID)],
        }

    def __init__(self, *args, **kwargs):
        """
        Current competition have multiple stages. We need to set current stage index.
        """
        super(Seb2014, self).__init__(*args, **kwargs)

        if self.competition.level == 2:  # if class is created for parent competition, then we do not have index
            cache_key = 'seb2014_competition_index_ids'
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
                item('{{ object }}', 'manager:applied_team %i object.id' % child.id, in_menu=False, access_loggedin=True),
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

    def get_startlist_table_class(self):
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

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            return sum(points[0:4])
        elif standing.distance_id == self.TAUTAS_DISTANCE_ID:
            return sum(points[0:5])
        elif standing.distance_id == self.BERNU_DISTANCE_ID:
            return sum(points[0:5])


    def recalculate_standing_points(self, standing):
        """
        This function recalculates distance and group total points for provided standing.
        If standing is children distance, then distance total is not calculated.
        """
        if standing.distance_id != self.BERNU_DISTANCE_ID:  # Children competition doesn't have distance_total
            standing.distance_total = self._participant_standings_points(standing, distance=True)
        standing.group_total = self._participant_standings_points(standing)

    def recalculate_standing(self, standing):
        """
        Function used to recalculate standing points, total seconds and to initialize point recalculation
        """
        standing.set_points()
        if standing.distance_id != self.BERNU_DISTANCE_ID:  # Children competition doesn't have time
            standing.set_distance_total_seconds()
        self.recalculate_standing_points(standing)  # Recalculate total points for this standing

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
        self.recalculate_standing(standing)
        standing.save()

    def recalculate_standing_for_results(self):
        """
        Function iterates through all results and recalculates standings.
        """
        all_results = Result.objects.filter(competition=self.competition)
        for result in all_results:
            self.recalculate_standing_for_result(result)

    def assign_distance_and_group_places(self):
        """
        Function iterates through all standings and assign place based on total points, total seconds and points in last stage
        """
        for distance in self.competition.get_distances().exclude(id=self.BERNU_DISTANCE_ID):
            all_standings = SebStandings.objects.filter(competition=self.competition.parent, distance=distance).order_by('-distance_total', 'distance_total_seconds', '-distance_points7')
            for index, standing in enumerate(all_standings, start=1):
                standing.distance_place = index
                standing.save()

        for distance in self.competition.get_distances():
            for group in self.groups.get(distance.id, ()):
                all_standings = SebStandings.objects.filter(competition=self.competition.parent, distance=distance, participant__group=group).order_by('-group_total', 'distance_total_seconds', '-distance_points7')
                for index, standing in enumerate(all_standings, start=1):
                    standing.group_place = index
                    standing.save()

    def recalculate_standings(self):
        """
        Function recalculates all standings for current competition. Function recalculates team results also.
        """
        if self.competition.level == 2:  # if class is called with stage competition, then recalculate all results
            self.recalculate_standing_for_results()

        all_standings = SebStandings.objects.filter(competition=self.competition.parent if self.competition.level == 2 else self.competition)
        for standing in all_standings:
            self.recalculate_standing_points(standing)  # Recalculate standing points
            standing.save()
        self.assign_distance_and_group_places()  # Reassign places

        if self.competition.level == 2:  # if class is called with stage competition, then recalculate all team results
            self.recalculate_team_results()  # Recalculate team total points for current competition
        else:
            pass  # TODO: Create team point recalculation for all stages at the same time


    def process_chip_recalculation(self):
        self.assign_distance_number()
        self.assign_group_number()
        self.recalculate_standings()
        from marketing.utils import send_smses
        send_smses()

    def process_chip_result(self, chip_id, sendsms=True):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        if chip.is_blocked:  # If blocked, then remove result, recalculate standings, recalculate team results
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

        results = Result.objects.filter(competition=chip.competition, number=chip.nr)
        if results:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip ignored. Already have result")
        else:
            participant = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)
            if not participant:
                participant_data = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_all_children_ids(), distance=chip.nr.distance, is_participating=True).order_by('-competition__id')
                if participant_data:
                    participant_data = participant_data.values()[0]

                    for pop_element in ['id', 'application_id', 'comment', 'created', 'created_by_id', 'insurance_id', 'legacy_id', 'modified', 'modified_by_id', 'price_id', 'registrant_id',]:
                        participant_data.pop(pop_element)

                    participant_data.update({'is_temporary': True, 'competition_id': chip.competition.id, })

                    participant = [Participant.objects.create(**participant_data), ]
                    Log.objects.create(content_object=participant[0], action="Chip process", message="Participant was not found, so created temporary one based on previous stage data.")
                    print 'Created participant with ID %i' % participant[0].id

            if participant:
                result = Result.objects.create(competition=chip.competition, participant=participant[0], number=chip.nr, time=result_time, )
                result.set_all()
                result.save()

                # Update standings...
                self.recalculate_standing_for_result(result)
                if participant[0].team:
                    self.recalculate_team_result(team=participant[0].team)
                if sendsms:
                    send(result.id)

            else:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")

        print chip


    def recalculate_all_points(self):
        distances = [self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID]
        recalculate_places = False
        results = Result.objects.filter(competition=self.competition, participant__distance_id__in=distances)
        for result in results:
            print result.id
            if result.set_all():
                recalculate_places = True
                result.save()
            self.recalculate_standing_for_result(result)

        if recalculate_places:
            self.assign_distance_and_group_places()
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

    def assign_distance_number(self):
        distances = self.competition.get_distances()

        for distance in distances:
            if distance.id == 27:
                continue # TODO: implement child competition place assingation
            results = Result.objects.filter(competition=self.competition, number__distance=distance).order_by('status', 'time')  # Status is because if something is written there, then is should be at the end.
            for index, result in enumerate(results, start=1):
                result.result_distance = index
                result.save()

    def assign_group_number(self):
        distances = self.competition.get_distances()

        for distance in distances:
            for group in self.groups.get(distance.id, ()):
                results = Result.objects.filter(competition=self.competition, number__distance=distance, participant__group=group).order_by('time')
                for index, result in enumerate(results, start=1):
                    result.result_group = index
                    result.save()

    def assign_numbers_continuously(self):
        self.assign_numbers(reassign=False, assign_special=False)

    def assign_numbers(self, reassign=False, assign_special=False):
        if reassign:
            Number.objects.filter(competition_id__in=self.competition.get_ids()).update(participant_slug='', number_text='')
            Participant.objects.filter(competition=self.competition, is_participating=True).update(primary_number=None)

        if self.competition.level == 2:
            parent_competition = self.competition.parent
        else:
            parent_competition = self.competition

        if assign_special:
            # first assign special numbers
            special = {
                1: 'peeter-pruus-1989',
                2: 'raido-kodanipork-1969',
                3: 'dimitriy-sorokin-1982',
                4: 'markku-ainsalu-1979',
                5: 'alges-masigmets-1968',
                6: 'caspar-austa-1982',
                7: 'arnis-petersons-1994',
                8: 'raivis-zimelis-1976',
                9: 'peteris-janevics-1994',
                10: 'helmet-tamkrov-1978',
                1111: 'dainis-grantins-1963',
                1555: 'kaspars-karklins-1975',
                1979: 'ingus-grintals-1979',
                2004: 'ugis-joksts-1975',
                2111: 'zigmunds-nurza-1975',
            }
            for nr in special:
                slug = special.get(nr)
                number = Number.objects.get(number=nr, competition=parent_competition)
                print "%s - %s" % (number, slug)
                number.participant_slug = slug
                number.save()


        print 'XXXXXXXXXXXX'
        # And now all others

        participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id__in=(24, 25, 27), primary_number=None).order_by('created')
        for participant in participants:
            group = self.get_group_for_number_search(participant.distance_id, participant.gender, participant.birthday)
            try:
                number = Number.objects.get(participant_slug=participant.slug, distance=participant.distance, group=group)
                if not participant.primary_number:
                    participant.primary_number = number
                    participant.save()
            except:
                next_numbers = Number.objects.filter(participant_slug='', distance=participant.distance, group=group).order_by('number')
                next_number = next_numbers[0]
                next_number.participant_slug = participant.slug
                next_number.number_text = str(participant.created)
                print "%s - %s" % (next_number, participant.slug)
                next_number.save()
                participant.primary_number = next_number
                participant.save()

    def get_group_for_number_search(self, distance_id, gender, birthday):
        if not isinstance(birthday, datetime.date):
            birthday = datetime.datetime.strptime(birthday, "%Y-%m-%d").date()

        if distance_id in (24, 25):
            return ''
        elif distance_id == 27:
            try:
                return self.assign_group(distance_id, gender, birthday)
            except:
                return 'xxx'


    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (24, 25, 27):
            return ''
        elif distance_id == 24:
            if year in (1997, 1996):
                return 'M-18'

            if gender == 'M':
                if 1995 >= year >= 1980:
                    return 'M'
                elif 1979 >= year >= 1975:
                    return 'M-35'
                elif 1974 >= year >= 1970:
                    return 'M-40'
                elif 1969 >= year >= 1965:
                    return 'M-45'
                elif year <= 1964:
                    return 'M-50'
            else:
                return 'W'
        elif distance_id == 25:
            if gender == 'M':
                if 2002 >= year >= 2000:
                    return 'M-14'
                elif 1999 >= year >= 1998:
                    return 'M-16'
                elif 1997 >= year >= 1996:
                    return 'T M-18'
                elif 1995 >= year >= 1980:
                    return 'T M'
                elif 1979 >= year >= 1970:
                    return 'T M-35'
                elif 1969 >= year >= 1965:
                    return 'T M-45'
                elif 1964 >= year >= 1960:
                    return 'T M-50'
                elif 1959 >= year >= 1955:
                    return 'T M-55'
                elif 1954 >= year >= 1950:
                    return 'T M-60'
                elif year <= 1949:
                    return 'T M-65'
            else:
                if 2002 >= year >= 1998:
                    return 'W-16'
                elif 1997 >= year >= 1996:
                    return 'T W-18'
                elif 1995 >= year >= 1980:
                    return 'T W'
                elif 1979 >= year >= 1970:
                    return 'T W-35'
                elif year <= 1969:
                    return 'T W-45'
        elif distance_id == 27:
            # bernu sacensibas
            if year >= 2010:
                return 'B 10-'
            elif year == 2009:
                return 'B 09'
            elif year == 2008:
                return 'B 08'
            elif year == 2007:
                return 'B 07'
            elif year == 2006:
                return 'B 06'
            elif year in (2005, 2004):
                return 'B 05-04'
            elif year in (2003, 2002):
                return 'B 03-02'

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning.')


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
                            data.update({'bike_brand': Choices.objects.get(kind=Choices.KIND_BIKEBRAND, title=row[6]), })
                        except:
                            pass
                    participant = Participant.objects.create(**data)

                # Assign number
                number = Number.objects.filter(competition=self.competition.parent, distance_id=self.BERNU_DISTANCE_ID, number=row[0], group=participant.group).order_by('-id')
                print number.update(participant_slug=participant.slug)
                if number:
                    participant.primary_number = number[0]
                    participant.save()

                if row[24]:
                    result, created = Result.objects.get_or_create(competition=self.competition, participant=participant, number=number.get(), result_group=row[24] if row[24] else None, points_group=row[25] if row[25] else 0, status=row[23])
                    self.recalculate_standing_for_result(result)
                else:
                    print 'didnt participate'
        self.assign_distance_and_group_places()