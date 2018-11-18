import os
from difflib import get_close_matches
from io import BytesIO

from django.utils.translation import activate
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.pdf import fill_page_with_image, _baseFontNameB, _baseFontName
from velo.registration.competition_classes import VB2018
from velo.registration.models import Participant, ChangedName, UCICategory, PreNumberAssign
from velo.results.models import Result, HelperResults
from velo.team.models import Team, Member


class VB2019(VB2018):
    SOSEJAS_DISTANCE_ID = 102
    MTB_DISTANCE_ID = 103
    TAUTAS_DISTANCE_ID = 104
    RETRO_DISTANCE_ID = 105
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
        return year + 5
