# coding=utf-8
from __future__ import unicode_literals
from velo.registration.competition_classes.base_seb import SEBCompetitionBase


class Seb2014(SEBCompetitionBase):
    competition_index = None

    SPORTA_DISTANCE_ID = 24
    TAUTAS_DISTANCE_ID = 25
    VESELIBAS_DISTANCE_ID = 26
    BERNU_DISTANCE_ID = 27

    STAGES_COUNT = 7

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'W', 'M-35', 'M-40', 'M-45', 'M-50'),
            self.TAUTAS_DISTANCE_ID: ('M-14', 'M-16', 'T M-18', 'T M', 'T M-35', 'T M-45', 'T M-50', 'T M-55', 'T M-60', 'T M-65', 'W-16', 'T W-18', 'T W', 'T W-35', 'T W-45'),
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


    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID, self.BERNU_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if year in (1997, 1996):
                return 'M-18'

            if gender == 'M':
                if 1995 >= year >= 1980:
                    return 'M'
                elif 1979 >= year >= 1975:
                    return 'M-35'
                elif 1974 >= year >= 1970:
                    return 'M-40'
                elif 1969 >= year >= 1965:
                    return 'M-45'
                elif year <= 1964:
                    return 'M-50'
            else:
                return 'W'
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if 2002 >= year >= 2000:
                    return 'M-14'
                elif 1999 >= year >= 1998:
                    return 'M-16'
                elif 1997 >= year >= 1996:
                    return 'T M-18'
                elif 1995 >= year >= 1980:
                    return 'T M'
                elif 1979 >= year >= 1970:
                    return 'T M-35'
                elif 1969 >= year >= 1965:
                    return 'T M-45'
                elif 1964 >= year >= 1960:
                    return 'T M-50'
                elif 1959 >= year >= 1955:
                    return 'T M-55'
                elif 1954 >= year >= 1950:
                    return 'T M-60'
                elif year <= 1949:
                    return 'T M-65'
            else:
                if 2002 >= year >= 1998:
                    return 'W-16'
                elif 1997 >= year >= 1996:
                    return 'T W-18'
                elif 1995 >= year >= 1980:
                    return 'T W'
                elif 1979 >= year >= 1970:
                    return 'T W-35'
                elif year <= 1969:
                    return 'T W-45'
        elif distance_id == self.BERNU_DISTANCE_ID:
            # bernu sacensibas
            if year >= 2010:
                return 'B 10-'
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
            elif year in (2003, 2002):
                return 'B 03-02'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning.')

    def _participant_standings_points(self, standing, distance=False):
        """
        This is private function that calculates points for participant based on distance.
        """
        stages = range(1, self.STAGES_COUNT+1)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            stages.remove(4)  # 4.stage is not taken because it is UCI category
        if distance:
            points = sorted((getattr(standing, 'distance_points%i' % stage) for stage in stages), reverse=True)
        else:
            points = sorted((getattr(standing, 'group_points%i' % stage) for stage in stages), reverse=True)

        if standing.distance_id == self.SPORTA_DISTANCE_ID:
            return sum(points[0:4])
        elif standing.distance_id == self.TAUTAS_DISTANCE_ID:
            return sum(points[0:5])
        elif standing.distance_id == self.BERNU_DISTANCE_ID:
            return sum(points[0:5])

