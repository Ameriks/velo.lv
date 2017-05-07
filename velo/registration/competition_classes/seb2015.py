from difflib import get_close_matches
import datetime
from django.db.models import Sum
from velo.core.models import Log
from velo.registration.competition_classes.base_seb import SEBCompetitionBase
from velo.registration.models import Application, ChangedName
from django import forms
from django.utils.translation import ugettext_lazy as _
from velo.registration.tables import ParticipantTableWithPoints, ParticipantTableWithPassage, ParticipantTable
from velo.results.models import SebStandings, HelperResults, ChipScan, Result
from velo.results.tables import ResultDistanceCheckpointTable


class Seb2015(SEBCompetitionBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 36
    TAUTAS_DISTANCE_ID = 37
    VESELIBAS_DISTANCE_ID = 38
    BERNU_DISTANCE_ID = 39

    STAGES_COUNT = 7

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
                (5,  200, 30),
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
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-16', 'T M-18', 'T M', 'T M-35', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
            self.VESELIBAS_DISTANCE_ID: ('M-14', 'W-14', ),
            self.BERNU_DISTANCE_ID: ('B 05-04 M', 'B 05-04 Z', 'B 06', 'B 07', 'B 08', 'B 09', 'B 10', 'B 11-', )
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 350, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 700, 'end': 3300, 'group': ''}, ],
            self.VESELIBAS_DISTANCE_ID: [{'start': 5000, 'end': 5200, 'group': ''}, ],
            self.BERNU_DISTANCE_ID: [{'start': 1, 'end': 100, 'group': group} for group in ('B 05-04', 'B 06', 'B 07', 'B 08', 'B 09', 'B 10', 'B 11-', )],
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
                if year in (self._update_year(1997), self._update_year(1996)):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'M-35'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'M-40'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'M-45'
                elif year <= self._update_year(1964):
                    return 'M-50'
            else:
                return 'W'
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'T M'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'T M-35'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'T M-45'
                elif self._update_year(1964) >= year >= self._update_year(1960):
                    return 'T M-50'
                elif self._update_year(1959) >= year >= self._update_year(1955):
                    return 'T M-55'
                elif self._update_year(1954) >= year >= self._update_year(1950):
                    return 'T M-60'
                elif year <= self._update_year(1949):
                    return 'T M-65'
            else:
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'W-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T W-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'T W'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'T W-35'
                elif year <= self._update_year(1969):
                    return 'T W-45'
        elif distance_id == self.BERNU_DISTANCE_ID:
            # bernu sacensibas
            if year >= 2011:
                return 'B 11-'
            elif year == 2010:
                return 'B 10'
            elif year == 2009:
                return 'B 09'
            elif year == 2008:
                return 'B 08'
            elif year == 2007:
                return 'B 07'
            elif year == 2006:
                return 'B 06'
            elif year in (2005, 2004):
                if gender == 'M':
                    return 'B 05-04 Z'
                else:
                    return 'B 05-04 M'

        elif distance_id == self.VESELIBAS_DISTANCE_ID:
            if year in (2001, 2002, 2003):
                if gender == 'M':
                    return 'M-14'
                else:
                    return 'W-14'
            else:
                return ''

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning.')


    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            return (('sport_approval', forms.BooleanField(label=_("I am informed that participation in Skandi Motors distance requires LRF licence. More info - %s") % "http://lrf.lv/licences/licences-2015.html", required=True)), )

        return ()

    def create_helper_results(self, participants):
        if self.competition.level != 2:
            raise Exception('We allow creating helper results only for stages.')


        # participants = participants.filter(distance_id__in=(self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID))

        current_competition = self.competition.parent
        prev_competition = current_competition.get_previous_sibling()

        # used for matching similar participants (grammar errors)
        prev_slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=prev_competition)]

        def get_prev_standing(participant):
            standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=participant.slug).order_by('-distance_total')

            if not standings:
                # 1. check if participant have changed name
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    standings = SebStandings.objects.filter(competition=prev_competition, participant_slug=changed.slug).order_by('-distance_total')
                except:
                    pass
            if standings:
                return standings[0]
            return None

        def get_current_standing(participant):
            standings = SebStandings.objects.filter(competition=current_competition, participant_slug=participant.slug).order_by('-distance_total')

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

            if participant.distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                continue

            # Calculate stage points only if last stage have finished + 2 days.
            if self.competition_index > 1:
                if self.competition.get_previous_sibling().competition_date  + datetime.timedelta(days=2) > datetime.date.today():
                    continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            current_standing = get_current_standing(participant)

            if self.competition_index == 1 or (self.competition_index == 2 and (not current_standing or current_standing.get('distance_points1') == 0)):
                standing = get_prev_standing(participant)

                helper.matches_slug = ''
                if standing:
                    if standing.distance.kind == 'S':
                        helper.calculated_total = (standing.distance_total or 0.0) / 4.0
                    else:
                        helper.calculated_total = (standing.distance_total or 0.0) / 5.0

                    # If last year participant was riding in Tautas and this year he is riding in Sport distance, then he must be after those who where riding sport distance.
                    # To sort participants correctly we have to give less points to them but still keep order based on last years results.
                    # If we divide by 10, then we will get them at the end of list.
                    if standing.distance.kind == 'T' and participant.distance.kind == 'S':
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
                participated_count = 0
                skipped_count = 0
                total_points = 0

                stages = range(1, self.competition_index)
                for stage in stages:
                    points = current_standing.get('distance_points%i' % stage)

                    if points > 1000:
                        points /= 2  # There shouldn't be such a case, but still, if so, then we divide points by 2

                    if points > 0:
                        participated_count += 1
                        total_points += points
                    else:
                        skipped_count += 1
                if participated_count:
                    helper.calculated_total = float(total_points) / float(participated_count)
                    if skipped_count == 1:
                        helper.calculated_total /= 1.15
                    elif skipped_count == 2:
                        helper.calculated_total /= 1.25
                    elif skipped_count > 2:
                        helper.calculated_total = total_points / (participated_count + (skipped_count - 2))
                else:
                    helper.calculated_total = 0.0
            elif not participant.primary_number:
                matches = get_close_matches(participant.slug, prev_slugs)
                if matches:
                    helper.matches_slug = matches[0]

            if helper.calculated_total is None:
                helper.calculated_total = 0.0

            helper.calculated_total = round(helper.calculated_total, 2)

            helper.save()

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
        if group is None:
            group = super(Seb2015, self).get_group_for_number_search(distance_id, gender, birthday)

        if group in ('B 05-04 M', 'B 05-04 Z'):
            return 'B 05-04'

        return group

    def recalculate_team_result(self, team_id=None, team=None):
        """
        4. stage should have zeros.
        """
        standing = super(Seb2015, self).recalculate_team_result(team_id, team)

        if self.competition_index == 4:
            if standing.team.distance_id == self.SPORTA_DISTANCE_ID:
                standing.points4 = 0
                standing.save()

        return standing

    def process_chip_result(self, chip_id, sendsms=True, recalc=False):
        """
        Function processes chip result and recalculates all standings
        """

        if self.competition_index != 7:
            return super(Seb2015, self).process_chip_result(chip_id, sendsms, recalc)

        chip = ChipScan.objects.get(id=chip_id)

        if chip.is_processed:
            Log.objects.create(content_object=chip, action="Chip process", message="Chip already processed")
            return None


        if chip.url_sync.kind == 'FINISH':
            return super(Seb2015, self).process_chip_result(chip_id, sendsms, recalc)
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
            if lap.time:
                Log.objects.create(content_object=chip, action="Chip process", message="Lap time already set.")
                return None

            lap.time = result_time
            lap.save()

        print(chip)


    def get_result_table_class(self, distance, group=None):
        if distance.id != self.BERNU_DISTANCE_ID and self.competition_index == 7 and not group:
            return ResultDistanceCheckpointTable

        return super(Seb2015, self).get_result_table_class(distance, group)
