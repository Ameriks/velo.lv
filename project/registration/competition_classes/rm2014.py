# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.core.cache.utils import make_template_fragment_key
from django.db.models import Count
from django.template.defaultfilters import slugify
import math
import csv
from django.core.cache import cache
from sitetree.utils import item
import StringIO
from core.models import Competition, Choices, Log
from marketing.utils import send_sms_to_participant, send_number_email, send_smses, send_sms_to_family_participant
from registration.competition_classes.base import CompetitionScriptBase
from registration.models import Number, Participant
from registration.tables import ParticipantTableWithResult, ParticipantTable
from results.models import LegacySEBStandingsResult, ChipScan, Result, DistanceAdmin, SebStandings, TeamResultStandings, \
    LapResult
from results.tables import *
from results.tables import ResultDistanceStandingTable, ResultRMSportsDistanceTable, ResultRMTautaDistanceTable, \
    ResultRMGroupTable
from results.tasks import send
from results.helper import time_to_seconds
from team.models import Team, MemberApplication
from marketing.tasks import send_mailgun
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from core.pdf import get_image, getSampleStyleSheet, base_table_style, fill_page_with_image, _baseFontName, \
    _baseFontNameB
from django.conf import settings
from django.db import connection
import os.path


class RM2014(CompetitionScriptBase):
    SPORTA_DISTANCE_ID = 28
    TAUTAS_DISTANCE_ID = 29
    GIMENU_DISTANCE_ID = 30
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
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if 1999 >= year >= 1998:
                    return 'Jaunieši'
                elif 1997 >= year >= 1996:
                    return 'Juniori'
                elif 1995 >= year >= 1980:
                    return 'Vīrieši'
                elif 1979 >= year >= 1975:
                    return 'Seniori I'
                elif 1974 >= year >= 1970:
                    return 'Seniori II'
                elif 1969 >= year >= 1965:
                    return 'Veterāni I'
                elif year <= 1964:
                    return 'Veterāni II'
            else:
                if 1999 >= year >= 1998:
                    return 'Jaunietes'
                elif 1997 >= year >= 1996:
                    return 'Juniores'
                elif 1995 >= year >= 1980:
                    return 'Sievietes'
                elif year <= 1979:
                    return 'Sievietes II'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T M'
            else:
                return 'T W'

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))


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

    def get_startlist_table_class(self):
        return ParticipantTable


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        styles = getSampleStyleSheet()
        output = StringIO.StringIO()

        doc = SimpleDocTemplate(output, pagesize=A4, showBoundary=0)
        elements = []
        elements.append(get_image(self.competition.logo.path, width=10*cm))
        elements.append(Paragraph(u"Apsveicam ar sekmīgu reģistrēšanos 31.Rīgas Velomaratonam, kas notiks šo svētdien, 1.jūnijā 11.novembra Krastmalā!", styles['h3']))

        data = [['Vārds, uzvārds:', participant.full_name],
                ['Dzimšanas gads:', participant.birthday.year],
                ['Distance:', participant.distance], ]
        if participant.primary_number:
            data.append(['Starta numurs', participant.primary_number.number])

        table_style = base_table_style[:]
        table_style.append(['FONTSIZE', (0, 0), (-1, -1), 16])
        table_style.append(['BOTTOMPADDING', (0, 0), (-1, -1), 10])


        elements.append(Table(data, style=table_style, hAlign='LEFT'))

        elements.append(Paragraph(u"Šo vēstuli, lūdzam saglabāt un izprintēt un ņemt līdzi uz Rīgas Velomaratona Expo centru, kas darbosies pie tirdzniecības centra „Spice” A ieejas 30. un 31.maijā no pkst.10:00-21:00.", styles['h3']))
        elements.append(Paragraph(u"Uzrādot šo vēstuli, Jūs varēsiet saņemt aploksni ar savu starta numuru. Lūdzam paņemt no reģistrācijas darbiniekiem instrukciju par pareizu numura piestiprināšanu.", styles['h3']))
        elements.append(Paragraph(u"Papildus informāciju meklējiet www.velo.lv", styles['h3']))
        elements.append(Paragraph(u"Vēlreiz apsveicam ar reģistrēšanos Rīgas Velomaratonam un novēlam veiksmīgu startu!", styles['h3']))

        elements.append(Paragraph(u"Rīga ir mūsu!", styles['title']))

        elements.append(Paragraph(u"Rīgas Velomaratona organizatori", styles['h3']))

        elements.append(Paragraph(u"Jautājumi?", styles['h2']))
        elements.append(Paragraph(u"Neskaidrību gadījumā sazinieties ar mums: pieteikumi@velo.lv", styles['h3']))

        doc.build(elements)
        return output

    def assign_numbers_continuously(self):
        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            last_number = Participant.objects.filter(distance_id=distance_id, is_participating=True).exclude(primary_number=None).order_by('-primary_number__number')[0].primary_number.number
            if distance_id == self.TAUTAS_DISTANCE_ID:
                last_number = 3590
            participants = Participant.objects.filter(distance_id=distance_id, is_participating=True, primary_number=None).order_by('created')

            for participant in participants:
                next_number = Number.objects.filter(distance_id=distance_id, number__gt=last_number, participant_slug='')[0]
                next_number.participant_slug = participant.slug
                next_number.save()
                participant.primary_number = next_number
                participant.save()
                send_sms_to_participant(participant)
                mailgun = send_number_email(participant)
                if mailgun:
                    send_mailgun(mailgun.id)

        participants = Participant.objects.filter(competition_id=34, is_participating=True, is_sent_number_sms=False, distance_id=30).order_by('created')
        for participant in participants:
            send_sms_to_family_participant(participant)

        participants = Participant.objects.filter(competition_id=34, distance_id=30, is_participating=True, is_sent_number_email=False).order_by('created')
        for participant in participants:
            mailgun = send_number_email(participant)
            if mailgun:
                send_mailgun(mailgun.id)

        send_smses()



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
                            send(result.id)

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

    def assign_distance_and_group_places(self):
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
        output = StringIO.StringIO()
        path = 'results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            return Exception

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 35)
        c.drawCentredString(c._pagesize[0] / 2, 16.3*cm, result.participant.full_name)
        c.setFont(_baseFontName, 25)
        c.drawCentredString(c._pagesize[0] / 2, 15*cm, "%i.vieta" % result.result_distance)
        c.setFont(_baseFontName, 18)
        c.drawCentredString(c._pagesize[0] / 2, 14*cm, "Laiks: %s" % result.time.replace(microsecond=0))
        c.drawCentredString(c._pagesize[0] / 2, 13*cm, "Vidējais ātrums: %s km/h" % result.avg_speed)

        # if result.zero_time:
        #     zero_time = datetime.datetime.combine(datetime.date.today(), result.zero_time)
        #     delta = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0)) - zero_time
        #     zero_time = (datetime.datetime.combine(datetime.date.today(), result.time) + delta).time().replace(microsecond=0)
        #     c.drawCentredString(c._pagesize[0] / 2, 12*cm, "Čipa laiks: %s" % zero_time)

        c.showPage()
        c.save()
        output.seek(0)
        return output


