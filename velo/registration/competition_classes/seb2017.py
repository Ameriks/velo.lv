from velo.registration.competition_classes import Seb2016
from velo.registration.models import UCICategory


class Seb2017(Seb2016):
    SPORTA_DISTANCE_ID = 60
    TAUTAS_DISTANCE_ID = 61
    VESELIBAS_DISTANCE_ID = 62
    BERNU_DISTANCE_ID = 63

    STAGES_COUNT = 7

    def _update_year(self, year):
        return year + 3

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M', 'M 19-34 CFA', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-16', 'T M-18', 'T M', 'T M-35', 'T M-40', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
            self.VESELIBAS_DISTANCE_ID: ('M-14', 'W-14', ),
            self.BERNU_DISTANCE_ID: ('B 07-06 Z', 'B 07-06 M', 'B 08', 'B 09', 'B 10', 'B 11', 'B 12', 'B 13-', )
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if participant and (self._update_year(1995) >= year >= self._update_year(1980)) and UCICategory.objects.filter(category="CYCLING FOR ALL", slug=participant.slug):
                    return 'M 19-34 CFA'
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
                return 'W'  # ok
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'T M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'T M'
                elif self._update_year(1979) >= year >= self._update_year(1975):
                    return 'T M-35'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'T M-40'
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
            if year >= 2013:
                return 'B 13-'
            elif year == 2012:
                return 'B 12'
            elif year == 2011:
                return 'B 11'
            elif year == 2010:
                return 'B 10'
            elif year == 2009:
                return 'B 09'
            elif year == 2008:
                return 'B 08'
            elif year in (2007, 2006):
                if gender == 'M':
                    return 'B 07-06 Z'
                else:
                    return 'B 07-06 M'

        elif distance_id == self.VESELIBAS_DISTANCE_ID:
            if year in (self._update_year(2000), self._update_year(2001), self._update_year(2002)):
                if gender == 'M':
                    return 'M-14'
                else:
                    return 'W-14'
            else:
                return ''

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning.')
