import datetime
import os
from io import BytesIO

import pytz
from django.utils import timezone
from django.utils.translation import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from slugify import slugify

from velo.core.models import Log
from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes import RM2019, RM2017
from velo.registration.models import Participant, PreNumberAssign, UCICategory
from velo.results.models import ChipScan, DistanceAdmin, Result, LapResult
from velo.results.tables import ResultRMGroupTable, ResultRMDistanceTable, ResultRMTautaDistanceTable, \
    ResultRM2016SportsDistanceTable, ResultRMGimeneDistanceTable
from velo.results.tasks import create_result_sms


class RM2020(RM2019):
    SPORTA_DISTANCE_ID = 98
    TAUTAS_DISTANCE_ID = 99
    TAUTAS1_DISTANCE_ID = 88  # OUT
    GIMENU_DISTANCE_ID = 100
    BERNU_DISTANCE_ID = 101

    def _update_year(self, year):
        return year + 1

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 1, 'end': 200, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3600, 'group': ''}, ],
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

    def passages(self):
        return {
            self.SPORTA_DISTANCE_ID: [(1, 1, 500, 0), ],
            self.TAUTAS_DISTANCE_ID: [
                                    (1, 2001, 2200, 15),
                                    (2, 2201, 2400, 20),
                                    (3, 2401, 2600, 20),
                                    (4, 2601, 2800, 10),
                                    (5, 2801, 3000, 10),
                                    (6, 3001, 3200, 10),
                                    (7, 3201, 3400, 5),
                                    (8, 3401, 3700, 0),
                                    ],
            self.GIMENU_DISTANCE_ID: [
                (1, 7001, 7901, 0),
            ],
        }
