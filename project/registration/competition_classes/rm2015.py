# coding=utf-8
from __future__ import unicode_literals
import StringIO
from marketing.utils import send_sms_to_participant, send_number_email, send_smses, send_sms_to_family_participant
from registration.competition_classes.base import RMCompetitionBase
from registration.models import Number, Participant

from marketing.tasks import send_mailgun
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from core.pdf import get_image, getSampleStyleSheet, base_table_style, fill_page_with_image, _baseFontName, _baseFontNameB
import os.path


class RM2015(RMCompetitionBase):
    SPORTA_DISTANCE_ID = 40
    TAUTAS_DISTANCE_ID = 41
    GIMENU_DISTANCE_ID = 42

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'Jaunieši'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'Juniori'
                elif self._update_year(1995) >= year >= self._update_year(1983):
                    return 'Vīrieši'
                elif self._update_year(1984) >= year >= self._update_year(1975):
                    return 'Seniori I'
                elif self._update_year(1974) >= year >= self._update_year(1970):
                    return 'Seniori II'
                elif self._update_year(1969) >= year >= self._update_year(1965):
                    return 'Veterāni I'
                elif year <= self._update_year(1964):
                    return 'Veterāni II'
            else:
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'Jaunietes'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'Juniores'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'Sievietes'
                elif year <= self._update_year(1979):
                    return 'Sievietes II'

        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T M'
            else:
                return 'T W'

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))


    def number_pdf(self, participant_id):
        participant = Participant.objects.get(id=participant_id)
        styles = getSampleStyleSheet()
        output = StringIO.StringIO()

        c = canvas.Canvas(output, pagesize=A4)
        fill_page_with_image("media/competition/vestule/RVm_2015_vestule_ar_tekstu.jpg", c)

        c.setFont(_baseFontNameB, 18)
        c.drawString(5*cm, 20*cm, participant.full_name.upper())
        c.drawString(5*cm, 18*cm, unicode(participant.distance))

        try:
            c.setFont(_baseFontNameB, 35)
            c.drawString(15*cm, 19*cm, unicode(participant.primary_number))
        except:
            pass

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def assign_numbers_continuously(self):
        for distance_id in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            last_number = Participant.objects.filter(distance_id=distance_id, is_participating=True).exclude(primary_number=None).order_by('-primary_number__number')[0].primary_number.number
            if distance_id == self.TAUTAS_DISTANCE_ID:
                last_number = 3590
            participants = Participant.objects.filter(distance_id=distance_id, is_participating=True, primary_number=None).order_by('created')

            for participant in participants:
                next_number = Number.objects.filter(distance_id=distance_id, number__gt=last_number, participant_slug='')[0]
                next_number.participant_slug = participant.slug
                next_number.save()
                participant.primary_number = next_number
                participant.save()
                send_sms_to_participant(participant)
                mailgun = send_number_email(participant)
                if mailgun:
                    send_mailgun(mailgun.id)

        participants = Participant.objects.filter(competition_id=self.competition_id, is_participating=True, is_sent_number_sms=False, distance_id=self.GIMENU_DISTANCE_ID).order_by('created')
        for participant in participants:
            send_sms_to_family_participant(participant)

        participants = Participant.objects.filter(competition_id=self.competition_id, distance_id=self.GIMENU_DISTANCE_ID, is_participating=True, is_sent_number_email=False).order_by('created')
        for participant in participants:
            mailgun = send_number_email(participant)
            if mailgun:
                send_mailgun(mailgun.id)

        send_smses()


    def generate_diploma(self, result):
        raise NotImplementedError
        output = StringIO.StringIO()
        path = 'results/files/diplomas/%i/%i.jpg' % (self.competition_id, result.participant.distance_id)

        if not os.path.isfile(path):
            return Exception

        c = canvas.Canvas(output, pagesize=A4)

        fill_page_with_image(path, c)

        c.setFont(_baseFontNameB, 35)
        c.drawCentredString(c._pagesize[0] / 2, 16.3*cm, result.participant.full_name)
        c.setFont(_baseFontName, 25)
        c.drawCentredString(c._pagesize[0] / 2, 15*cm, "%i.vieta" % result.result_distance)
        c.setFont(_baseFontName, 18)
        c.drawCentredString(c._pagesize[0] / 2, 14*cm, "Laiks: %s" % result.time.replace(microsecond=0))
        c.drawCentredString(c._pagesize[0] / 2, 13*cm, "Vidējais ātrums: %s km/h" % result.avg_speed)

        # if result.zero_time:
        #     zero_time = datetime.datetime.combine(datetime.date.today(), result.zero_time)
        #     delta = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0, 0)) - zero_time
        #     zero_time = (datetime.datetime.combine(datetime.date.today(), result.time) + delta).time().replace(microsecond=0)
        #     c.drawCentredString(c._pagesize[0] / 2, 12*cm, "Čipa laiks: %s" % zero_time)

        c.showPage()
        c.save()
        output.seek(0)
        return output

    def create_helper_results(self, participants):
        return True
