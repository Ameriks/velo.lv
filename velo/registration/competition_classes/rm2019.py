import datetime
import os
from io import BytesIO

import pytz
from django.utils import timezone
from django.utils.translation import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.models import Log
from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes import RM2018
from velo.registration.models import Participant, PreNumberAssign, UCICategory
from velo.results.models import ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultRMTautaDistanceTable, \
    ResultRM2016SportsDistanceTable, ResultRMGimeneDistanceTable
from velo.results.tasks import create_result_sms


class RM2019(RM2018):
    SPORTA_DISTANCE_ID = 98
    TAUTAS_DISTANCE_ID = 99
    TAUTAS1_DISTANCE_ID = 88  # OUT
    GIMENU_DISTANCE_ID = 100
    BERNU_DISTANCE_ID = 101

    def _update_year(self, year):
        return year + 0

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3700, 'group': ''}, ],
            self.GIMENU_DISTANCE_ID: [{'start': 7001, 'end': 7900, 'group': ''}, ],
        }

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SPORTA_DISTANCE_ID: ('M-18', 'M', 'M-35', 'M-45', 'M-55', 'M-65', 'W'),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', 'T M-14', 'T W-14', 'T M-16', 'T W-16', 'T M-18', 'T W-18',),
        }

    def assign_group(self, distance_id, gender, birthday, participant=None):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2002) >= year >= self._update_year(2001):
                    return 'M-18'
                elif self._update_year(2000) >= year >= self._update_year(1985):
                    return 'M'
                elif self._update_year(1984) >= year >= self._update_year(1975):
                    return 'M-35'
                elif self._update_year(1974) >= year >= self._update_year(1965):
                    return 'M-45'
                elif self._update_year(1964) >= year >= self._update_year(1955):
                    return 'M-55'
                elif year <= self._update_year(1954):
                    return 'M-65'
            else:
                return 'W'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2006) >= year >= self._update_year(2005):
                    return 'T M-14'
                elif self._update_year(2004) >= year >= self._update_year(2003):
                    return 'T M-16'
                elif self._update_year(2002) >= year >= self._update_year(2001):
                    return 'T M-18'
                elif year <= self._update_year(2000):
                    return 'T M'
            else:
                if self._update_year(2006) >= year >= self._update_year(2005):
                    return 'T W-14'
                elif self._update_year(2004) >= year >= self._update_year(2003):
                    return 'T W-16'
                elif self._update_year(2002) >= year >= self._update_year(2001):
                    return 'T W-18'
                elif year <= self._update_year(2000):
                    return 'T W'

        print('here I shouldnt be...')
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))
