from io import BytesIO

from django.utils.translation import activate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from velo.core.pdf import fill_page_with_image, _baseFontNameB
from velo.registration.competition_classes import VB2017
from velo.registration.models import Participant


class VB2018(VB2017):
    SOSEJAS_DISTANCE_ID = 89
    MTB_DISTANCE_ID = 90
    TAUTAS_DISTANCE_ID = 91
    RETRO_DISTANCE_ID = 92
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
        return year + 4


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        activate(participant.application.language if participant.application else 'lv')
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/VB2018.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(9.0*cm, 21.85*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(6.4*cm, 19.6*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(16.5*cm, 20.6*cm, str(participant.primary_number))
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(16.5*cm, 20.6*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output
