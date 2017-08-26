from velo.registration.competition_classes import VB2016
from velo.registration.models import UCICategory


class VB2017(VB2016):
    SOSEJAS_DISTANCE_ID = 69
    MTB_DISTANCE_ID = 70
    TAUTAS_DISTANCE_ID = 71
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

                if year <= self._update_year(1995) and UCICategory.objects.filter(group="Elite vīrieši", slug=participant.slug):
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
                    return 'M-Elite'

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
