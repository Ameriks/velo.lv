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

    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        activate(participant.application.language if participant.application else 'lv')
        output = BytesIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("velo/media/competition/vestule/VB2019.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(8.0*cm, 21.85*cm, "%s %s" % (participant.full_name.upper(), participant.birthday.year))
        c.drawString(8.0*cm, 19.6*cm, str(participant.distance))

        if participant.primary_number:
            c.setFont(_baseFontNameB, 35)
            c.drawString(8.0*cm, 20.6*cm, str(participant.primary_number))
        else:
            c.setFont(_baseFontNameB, 25)
            c.drawString(8.0*cm, 20.6*cm, "-")

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def pre_competition_run(self):
        t = Team.objects.filter(distance__competition=self.competition)
        members = Member.objects.filter(team__in=t)
        for member in members:
            try:
                p = Participant.objects.get(slug=member.slug, is_participating=True, distance=member.team.distance)
                if p.team_name != member.team.title:
                    print("%i %s %s %s" % (p.id, p.slug, p.team_name, member.team.title))
                    p.team_name = member.team.title
                    p.save()
            except:
                print('Not %s' % member.slug)

    def generate_diploma(self, result):
        output = BytesIO()
        path = 'velo/results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            raise Exception

        total_participants = result.competition.result_set.filter(participant__distance=result.participant.distance).count()
        total_group_participants = result.competition.result_set.filter(participant__distance=result.participant.distance, participant__group=result.participant.group).count()

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 28)
        c.setFillColor(HexColor(0x9F2B36))
        c.drawString(8 * cm, 12.2 * cm, str(result.participant.primary_number))

        c.setFont(_baseFontNameB, 25)
        c.setFillColor(HexColor(0x46445c))
        c.drawCentredString(c._pagesize[0]/2, 14.1*cm, result.participant.full_name)
        print(c._pagesize[0])
        c.setFont(_baseFontName, 25)
        c.drawCentredString(176, 9.2 * cm, str(result.time.replace(microsecond=0)))

        c.drawCentredString(128, 5.8*cm, str(result.result_group))
        c.drawCentredString(230, 5.8*cm, str(total_group_participants))

        c.drawCentredString(430, 5.8*cm, "%s km/h" % result.avg_speed)

        c.drawCentredString(380, 9.2*cm, str(result.result_distance))
        c.drawCentredString(482, 9.2*cm, str(total_participants))

        c.setFont(_baseFontName, 16)
        c.setFillColor(HexColor(0x9F2B36))
        c.drawRightString(523, 10.7 * cm, str(result.participant.group))

        c.showPage()
        c.save()
        output.seek(0)
        return output
