import csv
import os
from difflib import get_close_matches
import datetime
from io import BytesIO

import pytz
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from slugify import slugify

from velo.core.models import Log, Distance
from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes.base_seb import SEBCompetitionBase
from velo.registration.models import Application, ChangedName, Number, Participant, UCICategory, PreNumberAssign
from django import forms
from django.utils.translation import ugettext_lazy as _
from velo.registration.tables import ParticipantTableWithPoints, ParticipantTableWithPassage, ParticipantTable
from velo.results.helper import time_to_seconds, seconds_to_time
from velo.results.models import SebStandings, HelperResults, ChipScan, Result
from velo.results.tables import ResultDistanceCheckpointTable, ResultXCODistanceCheckpointSEBTable
from velo.results.tasks import update_helper_result_table


class Seb2020(SEBCompetitionBase):
    SPORTA_DISTANCE_ID = 106
    TAUTAS_DISTANCE_ID = 107
    VESELIBAS_DISTANCE_ID = 108
    BERNU_DISTANCE_ID = 109
    VESELIBAS_DISTANCE2_ID = 110
    STAGES_COUNT = 7
    CALCULATE_STANDING_FROM_STAGES = 5

    @property
    def passages(self):
        return {
            # Passage, participant count, reserve
            self.SPORTA_DISTANCE_ID: [
                (1, 50, 0),
                (2, 50, 0),
                (3, 100, 0),
                (4, 100, 0),
                (5, 100, 0),
                (6, 100, 0)],
            self.TAUTAS_DISTANCE_ID: [
                (1,  50,  0),
                (2,  50,  0),
                (3,  100, 0),
                (4,  100, 0),
                (5,  200, 0),
                (6,  200, 0),
                (7,  200, 0),
                (8,  200, 0),
                (9,  200, 0),
                (10, 200, 0),
                (11, 200, 0),
                (12, 200, 0),
                (13, 200, 0),
                (14, 200, 0),
                (15, 200, 0),
                ],
        }

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M', 'W', 'M-35', 'M-40', 'M-45', 'M-50+'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', 'M-16', 'W-16', 'T M-18', 'T W-18', 'T W-35', 'T W-45+', 'T M-35',
                                      'T M-40', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65+', "FAT"),
            self.VESELIBAS_DISTANCE2_ID: ('M-12', 'W-12', 'M-14', 'W-14',),
            self.BERNU_DISTANCE_ID: ('B 15-', 'B 14', 'B 13', 'B 12', 'B 11', 'B 10', 'B 09-08 Z', 'B 09-08 M',)
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 701, 'end': 3000, 'group': ''}, ],
            self.VESELIBAS_DISTANCE_ID: [{'start': 4001, 'end': 4700, 'group': ''}, ],
            self.VESELIBAS_DISTANCE2_ID: [{'start': 5001, 'end': 5400, 'group': ''}, ],
            self.BERNU_DISTANCE_ID: [{'start': (1000*index)+1, 'end': (1000*index)+150, 'group': group} for index, group in enumerate(self.groups.get(self.BERNU_DISTANCE_ID), start=1)],
        }

    def result_select_extra(self, distance_id):
        return {
            'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
        }

    def get_startlist_table_class(self, distance=None):
        if distance.id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            are_passages_assigned = HelperResults.objects.filter(competition=self.competition).exclude(passage_assigned=None).count()
            if are_passages_assigned:
                return ParticipantTableWithPassage
            else:
                return ParticipantTableWithPoints
        else:
            return ParticipantTable

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1984) >= year >= self._update_year(1980):
                    return 'M-35'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'M-40'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'M-45'
                elif self._update_year(1969) >= year:
                    return 'M-50+'
                else:
                    return 'M'
            else:
                return 'W'  # ok

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if participant.bike_brand2.upper() == "FATBIKE":
                return "FAT"
            elif gender == 'M':
                if self._update_year(2004) >= year >= self._update_year(2003):
                    return 'M-16' # ok
                elif self._update_year(2002) >= year >= self._update_year(2001):
                    return 'T M-18'
                elif self._update_year(2000) >= year >= self._update_year(1985):
                    return 'T M'
                elif self._update_year(1984) >= year >= self._update_year(1980):
                    return 'T M-35'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'T M-40'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'T M-45'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'T M-50'
                elif self._update_year(1964) >= year >= self._update_year(1960):
                    return 'T M-55'
                elif self._update_year(1959) >= year >= self._update_year(1955):
                    return 'T M-60'
                elif year <= self._update_year(1954):
                    return 'T M-65+'
            else:
                if self._update_year(2004) >= year >= self._update_year(2003):
                    return 'W-16'
                elif self._update_year(2002) >= year >= self._update_year(2001):
                    return 'T W-18'
                elif self._update_year(2000) >= year >= self._update_year(1985):
                    return 'T W'
                elif self._update_year(1984) >= year >= self._update_year(1975):
                    return 'T W-35'
                elif self._update_year(1974) >= year:
                    return 'T W-45+'

        elif distance_id == self.BERNU_DISTANCE_ID:
            # bernu sacensibas
            if year >= 2015:
                return 'B 15-'
            elif year == 2014:
                return 'B 14'
            elif year == 2013:
                return 'B 13'
            elif year == 2012:
                return 'B 12'
            elif year == 2011:
                return 'B 11'
            elif year == 2010:
                return 'B 10'
            elif year in (2008, 2009):
                if gender == 'M':
                    return 'B 09-08 Z'
                else:
                    return 'B 09-08 M'

        elif distance_id == self.VESELIBAS_DISTANCE2_ID:
            if gender == 'M':
                if self._update_year(2008) >= year >= self._update_year(2007):
                    return 'M-12'
                elif self._update_year(2006) >= year >= self._update_year(2005):
                    return 'M-14'
            else:
                if self._update_year(2008) >= year >= self._update_year(2007):
                    return 'W-12'
                elif self._update_year(2006) >= year >= self._update_year(2005):
                    return 'W-14'

        elif distance_id == self.VESELIBAS_DISTANCE_ID:
            return ''

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning.')


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


                # # In 4.stage all licenced juniors are put in 1st and 3rd passage
                # if passage_nr == 1 and self.competition_index == 4 and distance_id == self.TAUTAS_DISTANCE_ID:
                #     juniors = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('T M-18', )).order_by('-calculated_total', 'participant__registration_dt')
                #     for _ in juniors:
                #         slug = slugify('%s-%s' % (_.participant.first_name, _.participant.last_name), only_ascii=True)
                #         if UCICategory.objects.filter(slug__icontains=slug):
                #             _.passage_assigned = passage_nr
                #             _.save()
                # if passage_nr == 3 and self.competition_index == 4 and distance_id == self.TAUTAS_DISTANCE_ID:
                #     juniors = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('T W-18', )).order_by('-calculated_total', 'participant__registration_dt')
                #     for _ in juniors:
                #         slug = slugify('%s-%s' % (_.participant.first_name, _.participant.last_name), only_ascii=True)
                #         if UCICategory.objects.filter(slug__icontains=slug):
                #             _.passage_assigned = passage_nr
                #             _.save()


                # In 1.stage all licenced juniors are put in 3rd passage
                if passage_nr == 3 and self.competition_index == 1 and distance_id == self.TAUTAS_DISTANCE_ID:
                    juniors = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('M-16', 'T M-18')).order_by('-calculated_total', 'participant__registration_dt')
                    for _ in juniors:
                        slug = slugify('%s-%s' % (_.participant.first_name, _.participant.last_name), only_ascii=True)
                        if UCICategory.objects.filter(slug__icontains=slug):
                            _.passage_assigned = passage_nr
                            _.save()

                # In 1.stage all licenced girls and 50 women that are not in first 3 passages will be assigned to 4.passage
                if passage_nr == 4 and self.competition_index == 1 and distance_id == self.TAUTAS_DISTANCE_ID:
                    girls = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('W-16', 'T W-18')).order_by('-calculated_total', 'participant__registration_dt')
                    for _ in girls:
                        slug = slugify('%s-%s' % (_.participant.first_name, _.participant.last_name), only_ascii=True)
                        if UCICategory.objects.filter(slug__icontains=slug):
                            _.passage_assigned = passage_nr
                            _.save()

                    women = HelperResults.objects.filter(competition=self.competition, participant__distance_id=distance_id, participant__is_participating=True, passage_assigned=None, participant__group__in=('T W', 'T W-35')).order_by('-calculated_total', 'participant__registration_dt')[0:50]
                    for _ in women:
                        _.passage_assigned = passage_nr
                        _.save()


    def payment_additional_checkboxes(self, application_id=None, application=None):
        # if not application:
        #     application = Application.objects.get(id=application_id)

        # if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
        #     distance = Distance.objects.get(id=self.SPORTA_DISTANCE_ID)
        #     return ('sport_approval', forms.BooleanField(label=_("I am informed that participation in %s requires LRF licence. More info - http://lrf.lv") % distance, required=True)),

        return ()

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
        if distance_id == self.VESELIBAS_DISTANCE2_ID:
            return ''
        if group is None:
            group = super().get_group_for_number_search(distance_id, gender, birthday)
        return group

    def create_helper_results(self, participants):
        if self.competition.level != 2:
            raise Exception('We allow creating helper results only for stages.')


        # participants = participants.filter(distance_id__in=(self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID))

        current_competition = self.competition.parent
        prev_competition = current_competition.get_previous_sibling()

        # used for matching similar participants (grammar errors)
        prev_slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=prev_competition)]

        def get_prev_standings(participant):
            standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=participant.slug).order_by('-distance_total')

            if not standings:
                # 1. check if participant have changed name
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=changed.slug).order_by('-distance_total')
                except:
                    pass
            return standings

        def get_current_standing(participant):
            standings = SebStandings.objects.filter(competition=current_competition, participant_slug=participant.slug).order_by('-distance_total').exclude(distance__kind__in=('M', 'MC'))

            if not standings:
                return None

            standings = standings.aggregate(distance_points1=Sum('distance_points1'),
                                            distance_points2=Sum('distance_points2'),
                                            distance_points3=Sum('distance_points3'),
                                            distance_points4=Sum('distance_points4'),
                                            distance_points5=Sum('distance_points5'),
                                            distance_points6=Sum('distance_points6'),
                                            distance_points7=Sum('distance_points7'))
            return standings

        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

            current = helper.calculated_total

            if participant.distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.VESELIBAS_DISTANCE2_ID):
                continue

            # Calculate stage points only if last stage have finished + 2 days.
            if self.competition_index > 1:
                if self.competition.get_previous_sibling().competition_date  + datetime.timedelta(days=2) > datetime.date.today():
                    continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            current_standing = get_current_standing(participant)

            if self.competition_index == 1 or (self.competition_index == 2 and (not current_standing or current_standing.get('distance_points1') == 0)):
                standings = get_prev_standings(participant)
                try:
                    standing = standings[0]
                except:
                    standing = None

                helper.matches_slug = ''
                if standing:

                    # If participant have participated in all stages, but changed distances, we restore points
                    divide_by = 5.0
                    if standing.stages_participated < 5 and standings.count() > 1:
                        if standing.stages_participated + standings[1].stages_participated >= 5:
                            divide_by = float(standing.stages_participated)

                    helper.calculated_total = (standing.distance_total or 0.0) / divide_by

                    # if standing.distance.kind == 'T' or (standing.distance.kind == 'MC' and participant.distance.kind == 'T'):
                    #     helper.calculated_total -= 100

                    # If last year participant was riding in Tautas and this year he is riding in Sport distance, then he must be after those who where riding sport distance.
                    # To sort participants correctly we have to give less points to them but still keep order based on last years results.
                    # If we divide by 10, then we will get them at the end of list.
                    # If participant from Mammadaba now participates in tauta distance, then their points are reduced.
                    if standing.distance.kind in ('M', 'MC') and participant.distance.kind in ('T', 'S'):  # (standing.distance.kind == 'T' and participant.distance.kind == 'S') or
                        helper.calculated_total /= 10.0

                    if self.competition_index == 2:
                        helper.calculated_total /= 1.15

                    helper.result_used = standing
                else:
                    helper.calculated_total = 0.0
                    matches = get_close_matches(participant.slug, prev_slugs)
                    if matches:
                        helper.matches_slug = matches[0]
            elif current_standing:
                skipped_count = 0
                total_points_array = []

                stages = range(1, self.competition_index)
                for stage in stages:
                    points = current_standing.get('distance_points%i' % stage)
                    if points > 1000:
                        points /= 2  # There shouldn't be such a case, but still, if so, then we divide points by 2
                    if points > 0:
                        total_points_array.append(points)
                    else:
                        skipped_count += 1

                if len(total_points_array):
                    avg = float(sum(total_points_array)) / float(len(total_points_array))
                    if skipped_count in (1, 2):
                        total_points_array.append(avg / 1.15)

                    if skipped_count in (2, 3, 4):
                        total_points_array.append(avg / 1.25)

                    total_points_array = sorted(total_points_array, reverse=True)
                    if skipped_count > 2:
                        helper.calculated_total = sum(total_points_array[0:5]) / (len(total_points_array) + (skipped_count - 2))
                    else:
                        count = float(len(total_points_array))
                        if count > 5:
                            count = 5.0
                        helper.calculated_total = float(sum(total_points_array[0:5])) / count
                else:
                    helper.calculated_total = 0.0

                standings = SebStandings.objects.filter(competition=current_competition,
                                                       participant_slug=participant.slug).order_by('-distance_total')
                if standings.count() == 1:
                    standings = standings[0]
                    if standings.distance.kind == 'T' and participant.distance.kind == 'S' and helper.calculated_total > 0:
                        helper.calculated_total /= 10.0
                    #     If participants comming from Mammadaba, then points = 0
                    #  TODO: Need to check if there are more than 1 standing.
                    if standings.distance.kind in ('M', 'MC') and participant.distance.kind in ('S', 'T') and helper.calculated_total > 0:
                        helper.calculated_total = 0.0

            elif not participant.primary_number:
                matches = get_close_matches(participant.slug, prev_slugs)
                if matches:
                    helper.matches_slug = matches[0]

            if helper.calculated_total is None:
                helper.calculated_total = 0.0

            helper.calculated_total = round(helper.calculated_total, 2)

            helper.save()

    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """

        chip = ChipScan.objects.get(id=chip_id)

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        if chip.url_sync.kind == 'FINISH':
            return super().process_chip_result(chip_id, sendsms, recalc)
        else:
            result_time, seconds = self.calculate_time(chip)

            # Do not process if finished in 10 minutes.
            if seconds < 10 * 60: # 10 minutes
                Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
                return None

            participant = self.process_chip_create_participant(chip)

            if not participant:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")
                return False

            result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant[0], number=chip.nr, )
            lap, created = result.lapresult_set.get_or_create(index=chip.url_sync.index)
            if lap.time and not recalc:
                Log.objects.create(content_object=chip, action="Chip process", message="Lap time already set.")
                return None

            lap.time = result_time
            lap.save()

        print(chip)

    def get_result_table_class(self, distance, group=None):
        if distance.id != self.BERNU_DISTANCE_ID and not group:
            return ResultDistanceCheckpointTable

        return super().get_result_table_class(distance, group)

    def setup(self):
        uci = UCICategory.objects.filter(category="CYCLING FOR ALL", birthday__gte="1982-01-01", birthday__lt="1998-01-01")
        for u in uci:
            Participant.objects.filter(competition=self.competition, distance_id=49, is_participating=True, slug=u.slug, gender="M").update(group='M 19-34 CFA')

    def import_children_csv(self, filename):
        with transaction.atomic():
            with open(filename, 'r') as csvfile:
                results = csv.reader(csvfile)
                next(results)  # header line
                for row in results:

                    nr = int(row[0])
                    first_name = row[1]
                    last_name = row[2]
                    birthyear = int(row[3])
                    team_name = row[4]
                    index = int(row[5])
                    status = row[6]
                    time = row[7]
                    place = row[8]
                    points = row[9]
                    group = row[12]

                    if not place:
                        place = None
                    if not points:
                        points = None

                    print(row)

                    if index != self.competition_index:
                        print("Not processing.")
                        continue

                    if not first_name or not last_name or not birthyear:
                        print("Don't have all required data. Skipping.")
                        continue

                    if not time:
                        print("Don't have time data. Skipping.")
                        continue

                    number = Number.objects.get(distance_id=self.BERNU_DISTANCE_ID, number=nr)
                    if not number.participant_slug:
                        number.participant_slug = slugify("%s-%s-%s" % (row[1], row[2], row[3]), only_ascii=True)
                        number.save()

                    chip = ChipScan(competition=self.competition, nr=number, time=datetime.time(*map(int, time.split(':'))))

                    results = Result.objects.filter(competition=chip.competition, number=chip.nr).exclude(time=None)
                    # if results:
                    #     Log.objects.create(content_object=chip, action="Chip process",
                    #                        message="Chip ignored. Already have result")
                    #     continue
                    if True:
                        participant = self.process_chip_create_participant(chip)

                        # If participant is not previously created in system, we create it using data provided in CSV
                        if not participant:
                            data = {
                                'competition_id': self.competition_id,
                                'distance_id': self.BERNU_DISTANCE_ID,
                                'team_name': team_name,
                                'is_participating': True,
                                'first_name': first_name,
                                'last_name': last_name,
                                'birthday': datetime.date(birthyear, 1, 1),
                                'is_only_year': True,
                                'gender': '',
                                'primary_number': number
                            }
                            participant = [Participant.objects.create(**data), ]

                    result_time, seconds = self.calculate_time(chip)
                    result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant[0], number=chip.nr)
                    result.time = time  # result_time
                    # TODO: function to calculate the place and points.
                    result.result_group = place
                    result.points_group = points
                    if status:
                        result.status = status
                    result.save()

                    self.recalculate_standing_for_result(result)
            self.assign_standing_places()



    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception

        # Until most of participants have finished, we show total registered participants.
        riga_tz = pytz.timezone("Europe/Riga")
        now = riga_tz.normalize(timezone.now())
        if (now.date() == self.competition.competition_date) and now.hour < 17:
            total_participants = result.participant.distance.participant_set.filter(is_participating=True).count()
            total_group_participants = result.participant.distance.participant_set.filter(is_participating=True, group=result.participant.group).count()
        else:
            total_participants = result.competition.result_set.filter(participant__distance=result.participant.distance).count()
            total_group_participants = result.competition.result_set.filter(participant__distance=result.participant.distance, participant__group=result.participant.group).count()

        c = canvas.Canvas(output, pagesize=(21*cm, 29.7*cm))

        fill_page_with_image(path, c)

        if self.competition_id in (90, 91, 94):

            c.setFont(_baseFontNameB, 32)
            c.setFillColor(HexColor(0x47455b))
            c.drawString(c._pagesize[0] - 9.3 * cm, 16.1 * cm, str(result.participant.primary_number))

            c.setFont(_baseFontNameB, 26)
            c.setFillColor(HexColor(0x47455b))
            c.drawCentredString(c._pagesize[0] - 9.8 * cm, 17.7*cm, result.participant.full_name)

            c.setFont(_baseFontName, 28)
            c.drawCentredString(c._pagesize[0] - 10.2 * cm, 12.6 * cm, str(result.time.replace(microsecond=0)))

            if result.participant.distance_id != self.VESELIBAS_DISTANCE_ID:
                c.drawCentredString(c._pagesize[0] - 12.1 * cm, 9.5 * cm, str(result.result_distance))
                c.drawCentredString(c._pagesize[0] - 8.4 * cm, 9.5 * cm, str(total_participants))

                c.drawCentredString(c._pagesize[0] - 10 * cm, 3.7 * cm, "%s km/h" % result.avg_speed)

                c.drawCentredString(c._pagesize[0] - 12.1 * cm, 6.5*cm, str(result.result_group))
                c.drawCentredString(c._pagesize[0] - 8.4 * cm, 6.5*cm, str(total_group_participants))

        else:
            c.setFont(_baseFontNameB, 32)
            c.setFillColor(HexColor(0x47455b))

            if self.competition_id == 96:
                c.drawString(c._pagesize[0] - 13 * cm, 10.7 * cm, str(result.participant.primary_number))
            else:
                c.drawString(c._pagesize[0] - 13 * cm, 11.0 * cm, str(result.participant.primary_number))

            c.setFont(_baseFontNameB, 26)
            c.setFillColor(HexColor(0x47455b))

            if self.competition_id == 96:
                c.drawCentredString(c._pagesize[0] - 10.2 * cm, 12.3 * cm, result.participant.full_name)
            else:
                c.drawCentredString(c._pagesize[0] - 10.2 * cm, 12.6 * cm, result.participant.full_name)


            c.setFont(_baseFontName, 28)
            c.drawCentredString(c._pagesize[0] - 15.9 * cm, 7.2 * cm, str(result.time.replace(microsecond=0)))

            if result.participant.distance_id != self.VESELIBAS_DISTANCE_ID:
                c.drawCentredString(c._pagesize[0] - 17.8 * cm, 4.0 * cm, str(result.result_distance))
                c.drawCentredString(c._pagesize[0] - 14 * cm, 4.0 * cm, str(total_participants))

                c.drawCentredString(c._pagesize[0] - 5.5 * cm, 4.0 * cm, "%s km/h" % result.avg_speed)

                c.drawCentredString(c._pagesize[0] - 7.3 * cm, 7.0*cm, str(result.result_group))
                c.drawCentredString(c._pagesize[0] - 3.5 * cm, 7.0*cm, str(total_group_participants))



        c.showPage()
        c.save()
        output.seek(0)
        return output
