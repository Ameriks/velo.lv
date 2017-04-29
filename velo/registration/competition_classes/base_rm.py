import datetime


from django.db import connection

from sitetree.utils import item
from velo.core.models import Log
from velo.marketing.utils import send_sms_to_participant
from velo.marketing.utils import send_number_email
from velo.marketing.utils import send_sms_to_family_participant
from velo.marketing.utils import send_smses
from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Number, Participant, PreNumberAssign, Application
from django.core.cache import cache
from velo.registration.tables import ParticipantTable, ParticipantTableWithLastYearPlace
from velo.results.models import Result, DistanceAdmin, ChipScan, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMSportsDistanceTable, ResultRMTautaDistanceTable
from velo.results.tasks import create_result_sms

from django.utils.translation import ugettext_lazy as _


class RMCompetitionBase(CompetitionScriptBase):
    competition_index = 1
    TAUTAS1_DISTANCE_ID = None

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('Jaunieši', 'Jaunietes', 'Juniori', 'Juniores', 'Vīrieši', 'Sievietes', 'Sievietes II', 'Seniori I', 'Seniori II', 'Veterāni I', 'Veterāni II'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def result_select_extra(self, distance_id):
        if distance_id == self.SPORTA_DISTANCE_ID:
            return {
                'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
                'l5': 'SELECT time FROM results_lapresult l5 WHERE l5.result_id = results_result.id and l5.index=5',
            }
        else:
            return {
                'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
            }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        return NotImplementedError

    def build_manager_menu(self):
        return item(str(self.competition), 'manager:competition %i' % self.competition.id, in_menu=self.competition.is_in_menu, access_loggedin=True)

    def build_menu(self, lang):
        current_date = datetime.date.today() + datetime.timedelta(days=1)
        child_items = [
            # item('Atbalstītāji', 'competition:supporters %i' % self.competition.id),
            item(_("Teams"), 'competition:team %i' % self.competition.id, children=[
                item('{{ object }}', 'competition:team %i object.id' % self.competition.id, in_menu=False),
            ]),
            item(_('Start List'), 'competition:participant_list %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items, lang)
        if self.competition.map_set.count():
            child_items.append(item(_("Maps"), 'competition:maps %i' % self.competition.id))

        if self.competition.competition_date <= current_date:
            child_items.append(item(_("Results"), 'competition:result_distance_list %i' % self.competition.id))
            child_items.append(item(_("Team Results"), 'competition:result_team_by_name %i' % self.competition.id))
        return item(str(self.competition), 'competition:competition %i' % self.competition.id, url_as_pattern=True, children=child_items, in_menu=self.competition.is_in_menu)

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 500, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 4100, 'group': ''}, ],
        }

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 201, 400, 0), (2, 401, 500, 0)],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 10),
                                    (2, 2201, 2400, 30),
                                    (3, 2401, 2600, 30),
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
        if distance.id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            are_numbers_assigned = Participant.objects.filter(is_participating=True, distance=distance).exclude(primary_number=None).count()
            if not are_numbers_assigned:
                return ParticipantTableWithLastYearPlace
            else:
                return ParticipantTable
        else:
            return ParticipantTable


    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
            return ''


    def process_chip_result(self, chip_id, sendsms=True):
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


        participants = chip.nr.participant_set.all()

        if not participants:
            Log.objects.create(content_object=chip, action="Chip process", message="Number not assigned to anybody. Ignoring.")
            return None
        else:
            participant = participants[0]

        result, created = Result.objects.get_or_create(competition=chip.competition, participant=participant, number=chip.nr)

        already_exists_result = LapResult.objects.filter(result=result, time__gte=result_time_5back, time__lte=result_time_5forw)
        if already_exists_result:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip double scanned.")
        else:
            laps_done = result.lapresult_set.count()
            result.lapresult_set.create(index=(laps_done+1), time=result_time)
            if (chip.nr.distance_id == self.SPORTA_DISTANCE_ID and laps_done == 5) or (chip.nr.distance_id == self.TAUTAS_DISTANCE_ID and laps_done == 1):
                Log.objects.create(content_object=chip, action="Chip process", message="DONE. Lets assign avg speed.")
                result.time = result_time
                result.set_avg_speed()
                result.save()

                self.assign_standing_places()

                if participant.is_competing and self.competition.competition_date == datetime.date.today() and sendsms:
                    create_result_sms.apply_async(args=[result.id, ], countdown=120)


        chip.is_processed = True
        chip.save()

        print(chip)


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


    def assign_standing_places(self):
        self.assign_result_place()
        self.reset_cache_results()

    def reset_cache(self):
        cache.clear()  # This cleans all cache.
        return True
        # Reset team results.
        self.reset_cache_results()

        super(RM2014, self).reset_cache()

    def process_unprocessed_chips(self, send_sms=False):
        for chip in self.competition.chipscan_set.filter(is_processed=False).order_by('time'):
            self.process_chip_result(chip.id, send_sms)

    def generate_diploma(self, result):
        raise NotImplementedError


    def assign_numbers(self, reassign=False, assign_special=False):
        # TODO: There is not "group_together" made.
        if reassign:
            Number.objects.filter(competition=self.competition).update(participant_slug='', number_text='')
            Participant.objects.filter(competition=self.competition, is_participating=True).update(primary_number=None)

        if assign_special:
            # first assign special numbers
            numbers = PreNumberAssign.objects.filter(competition=self.competition).exclude(number=None)
            for pre in numbers:
                number = Number.objects.get(number=pre.number, competition=self.competition)
                print("%s - %s" % (number, pre.participant_slug))
                number.participant_slug = pre.participant_slug
                number.save()

                participant = Participant.objects.filter(slug=number.participant_slug, competition=self.competition, distance=number.distance, is_participating=True)
                if participant:
                    participant = participant[0]
                    participant.primary_number = number
                    participant.save()

        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.TAUTAS1_DISTANCE_ID):


            for passage_nr, passage_start, passage_end, passage_extra in self.passages().get(distance_id):
                special_in_passage = PreNumberAssign.objects.filter(competition=self.competition, number__gte=passage_start, number__lte=passage_end).count()
                places = passage_end - passage_start - passage_extra + 1 - special_in_passage

                final_slugs_in_passage = []
                participants_in_passage = PreNumberAssign.objects.filter(competition=self.competition, segment=passage_nr, distance_id=distance_id)
                for pre in participants_in_passage:
                    if not Participant.objects.filter(competition=self.competition, is_participating=True, distance_id=distance_id, slug=pre.participant_slug).exclude(primary_number=None):
                        final_slugs_in_passage.append(pre.participant_slug)


                participants = Participant.objects.filter(competition_id__in=self.competition.get_ids(), is_participating=True, distance_id=distance_id, primary_number=None).order_by('helperresults__calculated_total', 'registration_dt')[:places]
                participant_slugs = [obj.slug for obj in participants]

                extra_count = 0
                slugs_in_passage = final_slugs_in_passage[:]
                for slug in slugs_in_passage:
                    if slug in participant_slugs:
                        print('FOUND %s' % slug)
                        final_slugs_in_passage.remove(slug)
                    else:
                        print('not in')
                        extra_count += 1


                final_slugs = [obj.slug for obj in participants[:places-extra_count]] + final_slugs_in_passage

                final_numbers = [nr for nr in range(passage_start, passage_end+1) if Number.objects.filter(number=nr, competition=self.competition, participant_slug='')]


                for nr, slug in zip(final_numbers, final_slugs):
                    print('%i - %s' % (nr, slug))
                    number = Number.objects.get(number=nr, competition=self.competition, participant_slug='')
                    number.participant_slug = slug
                    number.save()
                    participant = Participant.objects.filter(slug=slug, competition=self.competition, distance=number.distance, is_participating=True)
                    if participant:
                        participant = participant[0]
                        participant.primary_number = number
                        participant.save()

    def assign_numbers_continuously(self):
        application_ids = []
        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            last_number = Participant.objects.filter(distance_id=distance_id, is_participating=True).exclude(primary_number=None).order_by('-primary_number__number')[0].primary_number.number
            participants = Participant.objects.filter(distance_id=distance_id, is_participating=True, primary_number=None).order_by('registration_dt')

            for participant in participants:
                if participant.application_id and participant.application_id not in application_ids:
                    application_ids.append(participant.application_id)
                next_number = Number.objects.filter(distance_id=distance_id, number__gt=last_number, participant_slug='')[0]
                next_number.participant_slug = participant.slug
                next_number.save()
                participant.primary_number = next_number
                participant.save()
                if participant.phone_number:
                    send_sms_to_participant(participant)
                if participant.email:
                    send_number_email(self.competition, [participant, ])

        participants = Participant.objects.filter(competition_id=self.competition_id, is_participating=True, is_sent_number_sms=False, distance_id=self.GIMENU_DISTANCE_ID).order_by('created')
        for participant in participants:
            if participant.phone_number:
                send_sms_to_family_participant(participant)

        participants = Participant.objects.filter(competition_id=self.competition_id, distance_id=self.GIMENU_DISTANCE_ID, is_participating=True, is_sent_number_email=False).order_by('-created')
        for participant in participants:
            if participant.application_id and participant.application_id not in application_ids:
                application_ids.append(participant.application_id)
            if participant.email:
                send_number_email(self.competition, [participant, ])

        applications = Application.objects.filter(id__in=application_ids)
        for application in applications:
            send_number_email(self.competition, application.participant_set.filter(is_participating=True), application)


        send_smses()

    def recalculate_all_standings(self):
        # Here are no standings.
        pass

    def recalculate_all_points(self):
        """
        MAIN FUNCTION FROM MANAGER
        This function is called from manager view to manually recalculate points.
        This function is called in case there are errors in given points.
        """
        distances = [self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.TAUTAS1_DISTANCE_ID]
        recalculate_places = False
        results = Result.objects.filter(competition=self.competition, participant__distance_id__in=distances)
        for result in results:
            print(result.id)
            if result.set_all():
                recalculate_places = True
                result.save()

        if recalculate_places:
            self.assign_standing_places()
