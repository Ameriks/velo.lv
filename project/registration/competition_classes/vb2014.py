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
from registration.models import Number, Participant, PreNumberAssign
from registration.tables import ParticipantTableWithResult, ParticipantTable
from results.models import LegacySEBStandingsResult, ChipScan, Result, DistanceAdmin, SebStandings, TeamResultStandings, \
    LapResult
from results.tables import *
from results.tables import ResultDistanceStandingTable, ResultRMSportsDistanceTable, ResultRMTautaDistanceTable, \
    ResultRMGroupTable, ResultRMDistanceTable
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


class VB2014(CompetitionScriptBase):
    SOSEJAS_DISTANCE_ID = 32
    MTB_DISTANCE_ID = 33
    TAUTAS_DISTANCE_ID = 34
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: ('W-18', 'M-16', 'M-18', 'M-Elite', 'W', 'M-40', 'M-50', 'M-60', 'M-70'),
            self.MTB_DISTANCE_ID: ('MTB M-14', 'MTB W-18', 'MTB M-16', 'MTB M-18', 'MTB M-Elite', 'MTB W', 'MTB M-40', 'MTB M-50', 'MTB M-60', 'MTB M-70', ),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SOSEJAS_DISTANCE_ID:
            if gender == 'M':
                if 1999 >= year >= 1998:
                    return 'M-16'
                elif 1997 >= year >= 1996:
                    return 'M-18'
                elif 1995 >= year >= 1980:
                    return 'M-Elite'
                elif 1979 >= year >= 1970:
                    return 'M-40'
                elif 1969 >= year >= 1960:
                    return 'M-50'
                elif year <= 1959:
                    return 'M-60'
            else:
                if 1999 >= year >= 1996:
                    return 'W-18'
                elif year <= 1995:
                    return 'W'
        elif distance_id == self.MTB_DISTANCE_ID:
            if gender == 'M':
                if 2002 >= year >= 2000:
                    return 'MTB M-14'
                elif 1999 >= year >= 1998:
                    return 'MTB M-16'
                elif 1997 >= year >= 1996:
                    return 'MTB M-18'
                elif 1995 >= year >= 1980:
                    return 'MTB M-Elite'
                elif 1979 >= year >= 1970:
                    return 'MTB M-40'
                elif 1969 >= year >= 1960:
                    return 'MTB M-50'
                elif year <= 1959:
                    return 'MTB M-60'
            else:
                if 2002 >= year >= 1996:
                    return 'MTB W-18'
                elif year <= 1995:
                    return 'MTB W'
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
        return item(unicode(self.competition), 'manager:competition %i' % self.competition.id, children=child_items, in_menu=self.competition.is_in_menu, access_loggedin=True)



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
            self.SOSEJAS_DISTANCE_ID: [{'start': 1, 'end': 350, 'group': ''}, ],
            self.MTB_DISTANCE_ID: [{'start': 401, 'end': 1200, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 7000, 'group': ''}, ],
        }


    def passages(self):
        return {
            self.SOSEJAS_DISTANCE_ID: [(1, 1, 350, 0), ],
            self.MTB_DISTANCE_ID: [
                                    (1, 401, 600, 10),
                                    (2, 601, 800, 10),
                                    (3, 801, 1000, 5),
                                    (4, 1001, 1200, 0),
                                    ],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 10),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 20),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3400, 0),
                                    (8, 3401, 3600, 0),
                                    (9, 3601, 3800, 0),
                                    (10, 3801, 4000, 0),
                                    (11, 4001, 4200, 0),
                                    (12, 4201, 4400, 0),
                                    (13, 4401, 4600, 0),
                                    (14, 4601, 4800, 0),
                                    (15, 4801, 5000, 0),
                                    (16, 5001, 5200, 0),
                                    (17, 5201, 5400, 0),
                                    (18, 5401, 5600, 0),
                                    (19, 5601, 5800, 0),
                                    (20, 5801, 6000, 0),
                                    ],
        }


    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultRMDistanceTable

    def get_startlist_table_class(self):
        return ParticipantTable


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        styles = getSampleStyleSheet()
        output = StringIO.StringIO()

        doc = SimpleDocTemplate(output, pagesize=A4, showBoundary=0)
        elements = []

        if self.competition.logo:
            elements.append(get_image(self.competition.logo.path, width=10*cm))
        elements.append(Paragraph(u"Apsveicam ar sekmīgu reģistrēšanos 24.Latvijas riteņbraucēju Vienības braucienam, kas notiks šo svētdien, 7.septembrī Siguldā!", styles['h3']))

        data = [['Vārds, uzvārds:', participant.full_name],
                ['Dzimšanas gads:', participant.birthday.year],
                ['Distance:', participant.distance], ]
        if participant.primary_number:
            data.append(['Starta numurs', participant.primary_number.number])

        table_style = base_table_style[:]
        table_style.append(['FONTSIZE', (0, 0), (-1, -1), 16])
        table_style.append(['BOTTOMPADDING', (0, 0), (-1, -1), 10])

        elements.append(Spacer(10, 10))
        elements.append(Table(data, style=table_style, hAlign='LEFT'))
        elements.append(Spacer(10, 10))
        elements.append(Paragraph(u"Šo vēstuli lūdzam saglabāt, izprintēt un uzrādīt saņemot starta numuru.", styles['h3']))
        elements.append(Paragraph(u"Starta numurus iespējams saņemt 5. un 6.septembrī pie u/v Elkor Plaza (Brīvības gatve 201, Rīga) laikā no 10:00 līdz 20:00 vai arī 7.septembrī Siguldā, reģistrācijas teltī no 09:00.", styles['h3']))

        elements.append(Paragraph(u"Lūdzam paņemt no reģistrācijas darbiniekiem instrukciju par pareizu numura piestiprināšanu.", styles['h3']))
        elements.append(Paragraph(u"Papildus informāciju meklējiet www.velo.lv", styles['h3']))

        elements.append(Paragraph(u"Vēlreiz apsveicam ar reģistrēšanos Vienības braucienam un novēlam veiksmīgu startu!", styles['h3']))

        elements.append(Paragraph(u"Sajūti kopīgo spēku!", styles['title']))

        elements.append(Paragraph(u"Sacensību organizatori", styles['h3']))

        elements.append(Paragraph(u"Jautājumi?", styles['h2']))
        elements.append(Paragraph(u"Neskaidrību gadījumā sazinieties ar mums: pieteikumi@velo.lv", styles['h3']))

        doc.build(elements)
        return output

    def assign_numbers_continuously(self):
        raise NotImplementedError
        for distance_id in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            last_number = Participant.objects.filter(distance_id=distance_id, is_participating=True).exclude(primary_number=None).order_by('-primary_number__number')[0].primary_number.number

            participants = Participant.objects.filter(distance_id=distance_id, is_participating=True, primary_number=None).order_by('registration_dt')

            for participant in participants:
                next_number = Number.objects.filter(distance_id=distance_id, number__gt=4186, participant_slug='')[0]
                next_number.participant_slug = participant.slug
                next_number.save()
                participant.primary_number = next_number
                participant.save()



    def assign_numbers(self, reassign=False, assign_special=False):
        if reassign:
            Number.objects.filter(competition=self.competition).update(participant_slug='', number_text='')
            Participant.objects.filter(competition=self.competition, is_participating=True).update(primary_number=None)

        if assign_special:
            # first assign special numbers
            pre_numbers = PreNumberAssign.objects.filter(competition=self.competition).exclude(number=None)
            for nr in pre_numbers:
                number = Number.objects.get(number=nr.number, competition=self.competition)
                print "%s - %s" % (number, nr.participant_slug)
                number.participant_slug = nr.participant_slug
                number.save()

                participant = Participant.objects.filter(slug=nr.participant_slug, competition=self.competition, distance=number.distance, is_participating=True)
                if participant:
                    participant = participant[0]
                    participant.primary_number = number
                    participant.save()

        for distance_id in (self.TAUTAS_DISTANCE_ID, ): #self.TAUTAS_DISTANCE_ID):

            exclude_slugs = [obj.participant_slug for obj in PreNumberAssign.objects.filter(competition=self.competition, distance_id=distance_id).exclude(group_together=None)]

            for passage_nr, passage_start, passage_end, passage_extra in self.passages().get(distance_id):
                special_in_passage_count = PreNumberAssign.objects.filter(competition=self.competition).exclude(number=None).filter(number__gte=passage_start, number__lte=passage_end).count()
                places = passage_end - passage_start - passage_extra + 1 - special_in_passage_count

                pre_numbers = PreNumberAssign.objects.filter(competition=self.competition, number=None, distance_id=distance_id, segment=passage_nr)
                slugs_in_passage = [obj.participant_slug for obj in pre_numbers]

                # Filter those slugs that already have number:
                final_slugs_in_passage = slugs_in_passage[:]
                for slug in slugs_in_passage:
                    if Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, slug=slug).exclude(primary_number=None).exclude(slug__in=exclude_slugs):
                        print 'removing slug %s' % slug
                        final_slugs_in_passage.remove(slug)

                participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, primary_number=None).exclude(legacyresult__id=None).exclude(slug__in=exclude_slugs).order_by('legacyresult__result_distance', 'registration_dt')[:places]
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

        results = Result.objects.filter(competition=chip.competition, number=chip.nr)
        if results:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip ignored. Already have result")
        else:
            participant = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)

            if participant:
                result = Result.objects.create(competition=chip.competition, participant=participant[0], number=chip.nr, time=result_time, )
                result.set_avg_speed()
                result.save()

                if sendsms and participant[0].is_competing and self.competition.competition_date == datetime.date.today():
                    send(result.id)

                chip.is_processed = True
                chip.save()

            else:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")

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

        super(VB2014, self).reset_cache()


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


