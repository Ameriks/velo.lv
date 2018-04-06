from velo.registration.competition_classes import RM2017


class RM2018(RM2017):
    SPORTA_DISTANCE_ID = 84
    TAUTAS_DISTANCE_ID = 85
    TAUTAS1_DISTANCE_ID = 88
    GIMENU_DISTANCE_ID = 87
    BERNU_DISTANCE_ID = 86

    def _update_year(self, year):
        return year + 4

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'M-35', 'M-45', 'M-55', 'M-65', 'W'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', 'T M-14', 'T W-14', 'T M-16', 'T W-16', 'T M-18', 'T W-18', ),
            # self.TAUTAS1_DISTANCE_ID: ('T1 M', 'T1 W',)
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
