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
        return year + 5

    def number_ranges(self):
        """
        Returns number ranges for each distance.
        """
        return {
            self.SPORTA_DISTANCE_ID: [{'start': 201, 'end': 400, 'group': ''}, ],
            self.TAUTAS_DISTANCE_ID: [{'start': 2001, 'end': 3700, 'group': ''}, ],
            self.GIMENU_DISTANCE_ID: [{'start': 7001, 'end': 7900, 'group': ''}, ],
        }
