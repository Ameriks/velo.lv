import datetime
import os
from io import BytesIO

import pytz
from django.utils import timezone
from django.utils.translation import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.models import Log
from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes import RM2017
from velo.registration.models import Participant, PreNumberAssign, UCICategory
from velo.results.models import ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultRMTautaDistanceTable, \
    ResultRM2016SportsDistanceTable, ResultRMGimeneDistanceTable
from velo.results.tasks import create_result_sms


class RM2018(RM2017):
    SPORTA_DISTANCE_ID = 84
    TAUTAS_DISTANCE_ID = 85
    TAUTAS1_DISTANCE_ID = 88  # OUT
    GIMENU_DISTANCE_ID = 87
    BERNU_DISTANCE_ID = 86

    def _update_year(self, year):
        return year + 4

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3700, 'group': ''}, ],
            self.GIMENU_DISTANCE_ID: [{'start': 7001, 'end': 7900, 'group': ''}, ],
        }

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'M-35', 'M-45', 'M-55', 'M-65', 'W'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', 'T M-14', 'T W-14', 'T M-16', 'T W-16', 'T M-18', 'T W-18', ),
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'M-55'
                elif year <= self._update_year(1949):
                    return 'M-65'
            else:
                return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2001) >= year >= self._update_year(2000):
                    return 'T M-14'
                elif self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T M-18'
                elif year <= self._update_year(1995):
                    return 'T M'
            else:
                if self._update_year(2001) >= year >= self._update_year(2000):
                    return 'T W-14'
                elif self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T W-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T W-18'
                elif year <= self._update_year(1995):
                    return 'T W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 1, 500, 0), ],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 20),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 15),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3700, 0),
                                    ],
            self.GIMENU_DISTANCE_ID: [
                (1, 7001, 7901, 0),
            ],
        }

    def number_pdf(self, participant_id):
        activate('lv')
        participant = Participant.objects.get(id=participant_id)
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/RVm_2018_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5*cm, 20.4*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(4*cm, 18.4*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 19.4*cm, str(participant.primary_number))
        # elif participant.distance_id == self.GIMENU_DISTANCE_ID:
        #     c.setFont(_baseFontNameB, 25)
        #     c.drawString(14*cm, 19.4*cm, "Ģimeņu br.")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15.5*cm, 19.4*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def assign_numbers(self, reassign=False, assign_special=False):
        # TODO: Need to find all participants that have started in sport distance and now are in other distances.
        prev_participants = [p.slug for p in Participant.objects.filter(is_participating=True, competition=self.competition, distance_id=65)]
        now_participants = Participant.objects.filter(distance_id=self.TAUTAS_DISTANCE_ID, is_participating=True, slug__in=prev_participants)
        for now in now_participants:
            try:
                PreNumberAssign.objects.get(competition=self.competition, participant_slug=now.slug)
            except:
                PreNumberAssign.objects.create(competition=self.competition, distance=now.distance, participant_slug=now.slug, segment=1)

        # All juniors in 2nd segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T M-16', )).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=2)

        # All juniors in 3rd segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T W-18', 'T W-16', 'T M-14')).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=3)

        # All juniors in 4th segment
        juniors = Participant.objects.filter(competition=self.competition, distance_id=self.TAUTAS_DISTANCE_ID,
                                             is_participating=True, group__in=('T W-14', )).order_by('id')
        for _ in juniors:
            if UCICategory.objects.filter(first_name__icontains=_.first_name, last_name__icontains=_.last_name):
                try:
                    PreNumberAssign.objects.get(competition=self.competition, participant_slug=_.slug)
                except:
                    PreNumberAssign.objects.create(competition=self.competition, distance=_.distance, participant_slug=_.slug, segment=4)

        super(RM2017, self).assign_numbers(reassign, assign_special)


    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()


        result_time_5back = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta - datetime.timedelta(minutes=5)).time()
        if result_time_5back > result_time:
            result_time_5back = datetime.time(0,0,0)
        result_time_5forw = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta + datetime.timedelta(minutes=5)).time()


        seconds = result_time.hour * 60 * 60 + result_time.minute * 60 + result_time.second

        # Do not process if finished in 10 minutes.
        if seconds < 10 * 60 or chip.time < distance_admin.zero: # 10 minutes
            Log.objects.create(content_object=chip, action="Chip process", message="Chip result less than 10 minutes. Ignoring.")
            return None

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None

        participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, slug=chip.nr.participant_slug, distance=chip.nr.distance)

        if not participants:
            Log.objects.create(content_object=chip, action="Chip process", message="Number not assigned to anybody. Ignoring.")
            return None
        else:
            participant = participants[0]

        if participant.is_competing:

            result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant, number=chip.nr)

            already_exists_result = LapResult.objects.filter(result=result, time__gte=result_time_5back, time__lte=result_time_5forw)
            if already_exists_result:
                Log.objects.create(content_object=chip, action="Chip process", message="Chip double scanned.")
            else:
                laps_done = result.lapresult_set.count()
                result.lapresult_set.create(index=(laps_done+1), time=result_time)

                # Fix lap index
                for index, lap in enumerate(result.lapresult_set.order_by('time'), start=1):
                    lap.index = index
                    lap.save()

                if (chip.nr.distance_id == self.SPORTA_DISTANCE_ID and laps_done == 3) or (chip.nr.distance_id == self.TAUTAS_DISTANCE_ID and laps_done == 1) or (chip.nr.distance_id == self.GIMENU_DISTANCE_ID and laps_done == 0):
                    Log.objects.create(content_object=chip, action="Chip process", message="DONE. Lets assign avg speed.")
                    last_laptime = result.lapresult_set.order_by('-time')[0]
                    result.time = last_laptime.time
                    result.set_avg_speed()
                    result.save()

                    self.assign_standing_places()

                    if self.competition.competition_date == datetime.date.today() and sendsms:
                        sms_text = "RM pagaidu rez nr. %(number)i laiks %(time)s, %(distance_result)i.vieta. Rezultati pieejami www.velo.lv."
                        if chip.nr.distance_id == self.GIMENU_DISTANCE_ID:
                            sms_text = "Apsveicam ar izcili nobrauktu Rigas velomaratonu! Nr.%(number)i laiks %(time)s"

                        create_result_sms.apply_async(args=[result.id, sms_text], countdown=120)

        chip.is_processed = True
        chip.save()

        print(chip)

    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception


        riga_tz = pytz.timezone("Europe/Riga")
        now = riga_tz.normalize(timezone.now())
        if (now.date() == self.competition.competition_date) and now.hour < 17:
            total_participants = result.participant.distance.participant_set.filter(is_participating=True).count()
            total_group_participants = result.participant.distance.participant_set.filter(is_participating=True, group=result.participant.group).count()
        else:
            total_participants = result.competition.result_set.filter(participant__distance=result.participant.distance).count()
            total_group_participants = result.competition.result_set.filter(participant__distance=result.participant.distance, participant__group=result.participant.group).count()

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 30)

        if result.participant.distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.GIMENU_DISTANCE_ID):

            c.drawCentredString(c._pagesize[0] / 2, 12.5*cm, result.participant.full_name)
            c.drawString(5.75*cm, 11.1 * cm, str(result.participant.primary_number))

            if result.participant.distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                c.setFont(_baseFontName, 25)
                c.drawCentredString(14*cm, 7.7*cm, str(result.result_distance) if result.result_distance else '-')
                c.drawCentredString(17.5 * cm, 7.7 * cm, str(total_participants))
                c.drawCentredString(5.25*cm, 7.7*cm, str(result.time.replace(microsecond=0)))

                c.drawCentredString(15.75*cm, 4.7*cm, "%s km/h" % result.avg_speed)
                c.drawCentredString(3.4*cm, 4.7*cm, str(result.result_group) if result.result_group else '-')
                c.drawCentredString(7.0 * cm, 4.7 * cm, str(total_group_participants))
            elif result.participant.distance_id in (self.GIMENU_DISTANCE_ID, ):
                c.drawCentredString(5.25 * cm, 7.7 * cm, str(result.time.replace(microsecond=0)))

        else:
            c.drawCentredString(c._pagesize[0] / 2, 10.5 * cm, result.participant.full_name)


        c.showPage()
        c.save()
        output.seek(0)
        return output


    def result_select_extra(self, distance_id):
        return {
            'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
            'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
            'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
            'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
        }

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            if distance.id == self.SPORTA_DISTANCE_ID:
                return ResultRM2016SportsDistanceTable
            elif distance.id in (self.GIMENU_DISTANCE_ID, self.BERNU_DISTANCE_ID):
                return ResultRMGimeneDistanceTable
            else:
                return ResultRMTautaDistanceTable
