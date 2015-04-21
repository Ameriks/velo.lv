# coding=utf-8
from __future__ import unicode_literals
from difflib import get_close_matches
from registration.competition_classes.base import SEBCompetitionBase
from registration.models import Application, ChangedName
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from registration.tables import ParticipantTableWithResult, ParticipantTable, ParticipantTableBase
from results.models import SebStandings, HelperResults


class Seb2015(SEBCompetitionBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 36
    TAUTAS_DISTANCE_ID = 37
    VESELIBAS_DISTANCE_ID = 38
    BERNU_DISTANCE_ID = 39

    STAGES_COUNT = 7

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-16', 'T M-18', 'T M', 'T M-35', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
            self.BERNU_DISTANCE_ID: ('B 05-04', 'B 06', 'B 07', 'B 08', 'B 09', 'B 10', 'B 11-', )
        }

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 350, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 500, 'end': 3500, 'group': ''}, ],
            self.BERNU_DISTANCE_ID: [{'start': 1, 'end': 100, 'group': group} for group in self.groups.get(self.BERNU_DISTANCE_ID)],
        }

    def get_startlist_table_class(self, distance=None):
        if distance.id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ParticipantTableWithResult
        elif distance.id == self.VESELIBAS_DISTANCE_ID:
             return ParticipantTableBase
        else:
            return ParticipantTable

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.BERNU_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
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
                return 'B 05-04'


        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning.')


    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            return (('sport_approval', forms.BooleanField(label=_("I am informed that participation in Skandi Motors distance requires LRF licence. More info - %s") % "http://lrf.lv/licences/licences-2015.html", required=True)), )

        return ()

    def create_helper_results(self, participants):
        if self.competition.level != 2:
            return Exception('We allow creating helper results only for stages.')

        participants = participants.filter(distance_id__in=(self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID))

        current_competition = self.competition.parent
        prev_competition = current_competition.get_previous_sibling()

        # used for matching similar participants (grammar errors)
        prev_slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=prev_competition)]
        current_slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=current_competition)]


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
            if standings:
                return standings[0]
            return None

        for participant in participants:
            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant, defaults={'calculated_total': 0})

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            current_standing = get_current_standing(participant)

            if self.competition_index == 1 or (self.competition_index == 2 and (not current_standing or current_standing.distance_points1 == 0)):
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
                    matches = get_close_matches(participant.slug, prev_slugs)
                    if matches:
                        helper.matches_slug = matches[0]
            else:
                participated_count = 0
                skipped_count = 0
                total_points = 0

                stages = range(1, self.competition_index)
                for stage in stages:
                    points = getattr(current_standing, 'distance_points%i' % stage)
                    if points > 0:
                        participated_count += 1
                        total_points += points
                    else:
                        skipped_count += 1

                helper.calculated_total = total_points / participated_count
                if skipped_count == 1:
                    helper.calculated_total /= 1.15
                elif skipped_count == 2:
                    helper.calculated_total /= 1.25
                elif skipped_count > 2:
                    helper.calculated_total = total_points / (participated_count + (skipped_count - 2))


            helper.save()
