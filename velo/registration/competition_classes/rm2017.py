import datetime
from django.utils.translation import activate
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.results.tasks import create_result_sms
from velo.core.models import Log
from velo.core.pdf import fill_page_with_image, _baseFontNameB
from velo.registration.competition_classes import RM2016
from velo.registration.models import UCICategory, Participant, PreNumberAssign
from velo.results.models import ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultRMTautaDistanceTable


class RM2017(RM2016):
    SPORTA_DISTANCE_ID = 65
    TAUTAS_DISTANCE_ID = 66
    TAUTAS1_DISTANCE_ID = 77
    GIMENU_DISTANCE_ID = 68
    BERNU_DISTANCE_ID = 67

    def _update_year(self, year):
        return year + 3

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'Masters', 'M 19-34 CFA', 'W'),
            self.TAUTAS_DISTANCE_ID: ('T M-16', 'T W-16', 'T M', 'T W', 'T M-35', 'T M-45', 'T M-55', 'T M-65'),
            self.TAUTAS1_DISTANCE_ID: ('T1 M', 'T1 W',)
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 500, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3400, 'group': ''}, ],
            self.TAUTAS1_DISTANCE_ID: [{'start': 3401, 'end': 4000, 'group': ''}, ],
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.TAUTAS1_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if participant and (self._update_year(1995) >= year >= self._update_year(1980)) and UCICategory.objects.filter(category="CYCLING FOR ALL", slug=participant.slug):
                    return 'M 19-34 CFA'
                if self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif year <= self._update_year(1979):
                    return 'Masters'
                else:
                    return 'M'
            else:
                return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'T M-16'
                elif self._update_year(1997) >= year >= self._update_year(1980):
                    return 'T M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'T M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'T M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'T M-55'
                elif year <= self._update_year(1949):
                    return 'T M-65'
            else:
                if self._update_year(1999) >= year >= self._update_year(1996):
                    return 'T W-16'
                elif year <= self._update_year(1997):
                    return 'T W'

        elif distance_id == self.TAUTAS1_DISTANCE_ID:
            if gender == 'M':
                return 'T1 M'
            else:
                return 'T1 W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 1, 200, 0), (2, 201, 500, 0)],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 20),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 15),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 5),
                                    (7, 3201, 3400, 5),
                                    ],
            self.TAUTAS1_DISTANCE_ID: [
                (1, 3401, 3600, 5),
                (2, 3601, 3800, 5),
                (3, 3801, 4000, 5),
            ],
        }

    def number_pdf(self, participant_id):
        activate('lv')
        participant = Participant.objects.get(id=participant_id)
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/RVm_2017_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(6*cm, 20.6*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(5*cm, 18.6*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(16*cm, 19.6*cm, str(participant.primary_number))
        elif participant.distance_id == self.GIMENU_DISTANCE_ID:
            c.setFont(_baseFontNameB, 25)
            c.drawString(15*cm, 19.6*cm, "Ģimeņu br.")
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(16.5*cm, 19.6*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def assign_numbers(self, reassign=False, assign_special=False):
        # TODO: Need to find all participants that have started in sport distance and now are in other distances.
        prev_participants = [p.slug for p in Participant.objects.filter(is_participating=True, competition=self.competition, distance_id=53)]
        now_participants = Participant.objects.filter(distance_id=self.TAUTAS_DISTANCE_ID, is_participating=True, slug__in=prev_participants)
        for now in now_participants:
            try:
                PreNumberAssign.objects.get(competition=self.competition, participant_slug=now.slug)
            except:
                PreNumberAssign.objects.create(competition=self.competition, distance=now.distance, participant_slug=now.slug, segment=1)

        super().assign_numbers(reassign, assign_special)

    def result_select_extra(self, distance_id):
        return {
            'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
        }

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            if distance.id in (self.SPORTA_DISTANCE_ID, self.TAUTAS1_DISTANCE_ID):
                return ResultRMDistanceTable
            else:
                return ResultRMTautaDistanceTable

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

                if (chip.nr.distance_id == self.SPORTA_DISTANCE_ID and laps_done == 0) or (chip.nr.distance_id == self.TAUTAS_DISTANCE_ID and laps_done == 1) or (chip.nr.distance_id == self.TAUTAS1_DISTANCE_ID and laps_done == 0):
                    Log.objects.create(content_object=chip, action="Chip process", message="DONE. Lets assign avg speed.")
                    last_laptime = result.lapresult_set.order_by('-time')[0]
                    result.time = last_laptime.time
                    result.set_avg_speed()
                    result.save()

                    self.assign_standing_places()

                    if self.competition.competition_date == datetime.date.today() and sendsms:
                        create_result_sms.apply_async(args=[result.id, ], countdown=120)


        chip.is_processed = True
        chip.save()

        print(chip)
