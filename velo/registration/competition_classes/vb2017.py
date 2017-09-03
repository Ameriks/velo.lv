import datetime
from io import BytesIO

import os
from django.utils.translation import activate
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.models import Log
from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes import VB2016
from velo.registration.models import UCICategory, Participant
from velo.results.models import ChipScan, Result
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultRMTautaDistanceTable
from velo.team.models import Team, Member


class VB2017(VB2016):
    SOSEJAS_DISTANCE_ID = 69
    MTB_DISTANCE_ID = 70
    TAUTAS_DISTANCE_ID = 71
    RETRO_DISTANCE_ID = 78
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: ('W-18', 'M-18', 'M CFA', 'M-Elite', 'W', 'M-35', 'M-45', 'M-55', 'M-65'),
            self.MTB_DISTANCE_ID: ('MTB W-18', 'MTB M-18', 'MTB M', 'MTB W', 'MTB M-35', 'MTB M-45', 'MTB M-55', 'MTB M-65', ),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def _update_year(self, year):
        return year + 3

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SOSEJAS_DISTANCE_ID:
            if gender == 'M':

                if year <= self._update_year(1995) and UCICategory.objects.filter(group__in=["Elite vīrieši", "U23"], slug=participant.slug):
                    return 'M-Elite'

                if self._update_year(1997) >= year >= self._update_year(1996): #ok
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980) and UCICategory.objects.filter(category="CYCLING FOR ALL", slug=participant.slug):
                    return 'M CFA'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'M-55'
                elif year <= self._update_year(1949):
                    return 'M-65'

                if year <= self._update_year(1995):
                    print("Problematic group - %s" % participant)
                    return 'M CFA'

            else:
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'W-18'
                elif year <= self._update_year(1995):
                    return 'W'
        elif distance_id == self.MTB_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'MTB M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'MTB M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'MTB M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'MTB M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'MTB M-55'
                elif year <= self._update_year(1949):
                    return 'MTB M-65'
            else:
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'MTB W-18'
                elif year <= self._update_year(1995):
                    return 'MTB W'
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T M'
            else:
                return 'T W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))

    def pre_competition_run(self):
        t = Team.objects.filter(distance__competition=self.competition)
        members = Member.objects.filter(team__in=t)
        for member in members:
            try:
                p = Participant.objects.get(slug=member.slug, is_participating=True, distance=member.team.distance)
                if p.team_name != member.team.title:
                    print("%i %s %s %s" % (p.id, p.slug, p.team_name, member.team.title))
                    p.team_name = member.team.title
                    p.save()
            except:
                print('Not %s' % member.slug)

    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        activate(participant.application.language if participant.application else 'lv')
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/VB2017.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(9.0*cm, 21.35*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(6.4*cm, 19.1*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(16*cm, 20.1*cm, str(participant.primary_number))
        # elif participant.distance_id == self.GIMENU_DISTANCE_ID:
        #     c.setFont(_baseFontNameB, 25)
        #     c.drawString(15*cm, 18.5*cm, "Amway")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(16*cm, 20.1*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def result_select_extra(self, distance_id):
        return {
            'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
        }


    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception

        total_participants = result.competition.result_set.filter(participant__distance=result.participant.distance).count()
        total_group_participants = result.competition.result_set.filter(participant__distance=result.participant.distance, participant__group=result.participant.group).count()

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 28)
        c.setFillColor(HexColor(0x9F2B36))
        c.drawString(7 * cm, 13 * cm, str(result.participant.primary_number))

        c.setFont(_baseFontNameB, 25)
        c.setFillColor(HexColor(0x46445c))
        c.drawCentredString(c._pagesize[0]/2, 14.5*cm, result.participant.full_name)
        print(c._pagesize[0])
        c.setFont(_baseFontName, 25)
        c.drawCentredString(176, 10.2 * cm, str(result.time.replace(microsecond=0)))

        c.drawCentredString(128, 7*cm, str(result.result_group))
        c.drawCentredString(230, 7*cm, str(total_group_participants))

        c.drawCentredString(420, 7*cm, "%s km/h" % result.avg_speed)

        c.drawCentredString(370, 10.2*cm, str(result.result_distance))
        c.drawCentredString(472, 10.2*cm, str(total_participants))

        c.setFont(_baseFontName, 16)
        c.setFillColor(HexColor(0x9F2B36))
        c.drawRightString(523, 11.6 * cm, str(result.participant.group))

        c.showPage()
        c.save()
        output.seek(0)
        return output

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
            # Function used to fetch data - who is fastest in the last hill.
            result = Result.objects.get(competition=chip.competition, number=chip.nr)

            delta = datetime.datetime.combine(datetime.date.today(), result.time) - datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0, 0))
            result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

            lap, created = result.lapresult_set.get_or_create(index=chip.url_sync.index)
            if lap.time and not recalc:
                Log.objects.create(content_object=chip, action="Chip process", message="Lap time already set.")
                return None

            lap.time = result_time
            lap.save()

        print(chip)

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultRMTautaDistanceTable
