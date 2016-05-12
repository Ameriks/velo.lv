# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.db import connection
from sitetree.utils import item

from velo.core.models import Log
from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Application
from django import forms
from django.utils.translation import ugettext_lazy as _, activate
from velo.registration.tables import ParticipantTable
from velo.results.models import HelperResults, ChipScan, DistanceAdmin, Result
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable
from velo.results.tasks import create_result_sms


class EC2016(CompetitionScriptBase):
    SPORTA_DISTANCE_ID = 48

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M Elite', 'W Elite', ),
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 300, 'group': ''}, ],
        }

    def get_startlist_table_class(self, distance=None):
        return ParticipantTable

    def _update_year(self, year):
        return year + 2

    def assign_group(self, distance_id, gender, birthday):
        if gender == 'M':
            return 'M Elite'
        else:
            return 'W Elite'

    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            return (('sport_approval', forms.BooleanField(label=_("I am informed that participation in UEC MTB Marathon requires licence. More info in Technical Guide."), required=True)), )

        return ()

    def create_helper_results(self, participants):

        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

    def process_chip_result(self, chip_id, sendsms=True):
        """
        Function processes chip result and recalculates all standings
        """
        chip = ChipScan.objects.get(id=chip_id)
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        zero_minus_10secs = (
        datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.timedelta(
            seconds=10)).time()
        if chip.time < zero_minus_10secs:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip scanned before start")
            return False

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0, 0, 0))
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
            Log.objects.create(content_object=chip, action="Chip process",
                               message="Chip ignored. Already have result")
        else:
            participant = Participant.objects.filter(slug=chip.nr.participant_slug,
                                                     competition_id__in=chip.competition.get_ids(),
                                                     distance=chip.nr.distance, is_participating=True)

            if participant:
                result = Result.objects.create(competition=chip.competition, participant=participant[0],
                                               number=chip.nr, time=result_time, )
                result.set_avg_speed()
                result.save()

                self.assign_standing_places()

                if sendsms and participant[
                    0].is_competing and self.competition.competition_date == datetime.date.today():
                    create_result_sms.apply_async(args=[result.id, ], countdown=120)

                chip.is_processed = True
                chip.save()

            else:
                Log.objects.create(content_object=chip, action="Chip error", message="Participant not found")

        print(chip)

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultRMDistanceTable

    def build_menu(self, lang):
        activate(lang)
        current_date = datetime.date.today()
        child_items = [
            item(_('Start List'), 'competition:participant_list %i' % self.competition.id),
            item(_("Maps"), 'competition:maps %i' % self.competition.id),
        ]
        self.build_flat_pages(self.competition, child_items, lang)

        if self.competition.competition_date <= current_date:
            child_items.append(item(_("Results"), 'competition:result_distance_list %i' % self.competition.id))

        return item(str(self.competition), 'competition:competition %i' % self.competition.id, url_as_pattern=True, children=child_items, in_menu=self.competition.is_in_menu)

    def build_manager_menu(self):
        return item(str(self.competition), 'manager:competition %i' % self.competition.id,
                    in_menu=self.competition.is_in_menu, access_loggedin=True)

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
