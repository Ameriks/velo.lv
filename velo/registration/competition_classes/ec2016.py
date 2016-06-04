# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.db import connection
from sitetree.utils import item

from velo.core.models import Log
from velo.registration.competition_classes.base import CompetitionScriptBase
from velo.registration.models import Application, Participant
from django import forms
from django.utils.translation import ugettext_lazy as _, activate
from velo.registration.tables import ParticipantTable, ParticipantTableWCountry
from velo.results.models import HelperResults, ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultXCODistanceCheckpointTable, \
    ResultGroupTable
from velo.results.tasks import create_result_sms


class EC2016(CompetitionScriptBase):
    SPORTA_DISTANCE_ID = 48
    competition_index = 1

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
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 351, 'group': ''}, ],
        }

    def get_startlist_table_class(self, distance=None):
        return ParticipantTableWCountry

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

        if chip.nr.number > 350:  # Skip all results that have number > 300 those are from public ride.
            return False

        Log.objects.create(content_object=chip, action="Chip process", message="Started")

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(
            datetime.date.today(), datetime.time(0, 0, 0, 0))
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

        participant = Participant.objects.get(slug=chip.nr.participant_slug, competition_id__in=chip.competition.get_ids(), distance=chip.nr.distance, is_participating=True)

        participant_in_seb = Participant.objects.filter(slug=chip.nr.participant_slug, competition_id__in=(54, 51), distance_id=49, is_participating=True)

        result, created = Result.objects.get_or_create(competition=chip.competition, number=chip.nr, participant=participant)

        result_seb = None
        if participant_in_seb:
            result_seb, created = Result.objects.get_or_create(competition_id=54, number=chip.nr, participant=participant_in_seb[0])

        already_exists_result = LapResult.objects.filter(result=result, time__gte=result_time_5back,
                                                         time__lte=result_time_5forw)

        if already_exists_result:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip double scanned.")
        elif result.time:
            Log.objects.create(content_object=chip, action="Chip process", message="Result already set.")
        else:
            if participant.gender == 'M':
                if chip.url_sync.kind == 'FINISH':
                    split1 = result.lapresult_set.filter(index=2)
                    split2 = result.lapresult_set.filter(index=4)
                    split3 = result.lapresult_set.filter(index=5)

                    if not split1:
                        result.lapresult_set.create(index=2, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=2, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=4, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=4, time=result_time)
                    elif not split3:
                        result.lapresult_set.create(index=5, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=5, time=result_time)
                else:
                    split1 = result.lapresult_set.filter(index=1)
                    split2 = result.lapresult_set.filter(index=3)

                    if not split1:
                        result.lapresult_set.create(index=1, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=1, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=3, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=3, time=result_time)
            else:
                # WOMEN
                if chip.url_sync.kind == 'FINISH':
                    split1 = result.lapresult_set.filter(index=2)
                    split2 = result.lapresult_set.filter(index=3)

                    if not split1:
                        result.lapresult_set.create(index=2, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=2, time=result_time)
                    elif not split2:
                        result.lapresult_set.create(index=3, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=3, time=result_time)

                else:
                    split1 = result.lapresult_set.filter(index=1)

                    if not split1:
                        result.lapresult_set.create(index=1, time=result_time)
                        if result_seb:
                            result_seb.lapresult_set.create(index=1, time=result_time)

            # FINAL RESULT CALC:
            if participant.gender == 'M':
                final_result = result.lapresult_set.filter(index=5)
            else:
                final_result = result.lapresult_set.filter(index=3)

            if final_result:
                final_result = final_result[0]
                Log.objects.create(content_object=chip, action="Chip process",
                                   message="DONE. Lets assign avg speed.")
                result.time = final_result.time
                result.set_avg_speed()
                result.save()

                result_seb.time = final_result.time
                result_seb.set_avg_speed()
                result_seb.save()

                self.assign_standing_places()

                # Recalculate standing places in SEB also.
                from .seb2016 import Seb2016
                _class = Seb2016(competition_id=54)
                _class.assign_standing_places()

                if participant.is_competing and self.competition.competition_date == datetime.date.today() and sendsms:
                    create_result_sms.apply_async(args=[result.id, ], countdown=240)

        chip.is_processed = True
        chip.save()

        print(chip)

    def assign_standing_places(self):
        self.assign_result_place()
        self.reset_cache_results()

    def get_result_table_class(self, distance, group=None):
        if group:
            return ResultRMGroupTable
        else:
            return ResultXCODistanceCheckpointTable

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
