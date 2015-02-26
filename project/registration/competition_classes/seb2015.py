# coding=utf-8
from __future__ import unicode_literals
from registration.competition_classes.base import SEBCompetitionBase
from registration.models import Application
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _


class Seb2015(SEBCompetitionBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 36
    TAUTAS_DISTANCE_ID = 37
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
            self.BERNU_DISTANCE_ID: ('B 03-02', 'B 05-04', 'B 06', 'B 07', 'B 08', 'B 09', 'B 10-', )
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

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.BERNU_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if year in (self._update_year(1997), self._update_year(1996)):
                return 'M-18'

            if gender == 'M':
                if self._update_year(1995) >= year >= self._update_year(1980):
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
            if year >= self._update_year(2010):
                return 'B 10-'
            elif year == self._update_year(2009):
                return 'B 09'
            elif year == self._update_year(2008):
                return 'B 08'
            elif year == self._update_year(2007):
                return 'B 07'
            elif year == self._update_year(2006):
                return 'B 06'
            elif year in (self._update_year(2005), self._update_year(2004)):
                return 'B 05-04'
            elif year in (self._update_year(2003), self._update_year(2002)):
                return 'B 03-02'

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning.')


    def payment_additional_checkboxes(self, application_id=None, application=None):
        if not application:
            application = Application.objects.get(id=application_id)

        if application.participant_set.filter(distance_id=self.SPORTA_DISTANCE_ID):
            return (('sport_approval', forms.BooleanField(label=_("I am informed that participation in Skandi Motors distance requires LRF licence. More info - %s") % "http://lrf.lv/licences/licences-2015.html", required=True)), )

        return ()