# coding=utf-8
from __future__ import unicode_literals
import datetime
from django.core.cache.utils import make_template_fragment_key
from django.db.models import Count
from django.template.defaultfilters import slugify
import math
import csv
from django.core.cache import cache
from sitetree.utils import item
import StringIO
from core.models import Competition, Choices, Log
from marketing.utils import send_sms_to_participant, send_number_email, send_smses, send_sms_to_family_participant
from registration.competition_classes.base import CompetitionScriptBase, RMCompetitionBase
from registration.models import Number, Participant
from results.models import LegacySEBStandingsResult, ChipScan, Result, DistanceAdmin, SebStandings, TeamResultStandings, \
    LapResult
from results.tables import *
from results.tables import ResultDistanceStandingTable, ResultRMSportsDistanceTable, ResultRMTautaDistanceTable, \
    ResultRMGroupTable
from results.tasks import create_result_sms
from results.helper import time_to_seconds
from team.models import Team, MemberApplication
from marketing.tasks import send_mailgun
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from core.pdf import get_image, getSampleStyleSheet, base_table_style, fill_page_with_image, _baseFontName, \
    _baseFontNameB
from django.conf import settings
from django.db import connection
import os.path


class RM2014(RMCompetitionBase):
    SPORTA_DISTANCE_ID = 28
    TAUTAS_DISTANCE_ID = 29
    GIMENU_DISTANCE_ID = 30


    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SPORTA_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SPORTA_DISTANCE_ID:
            if gender == 'M':
                if 1999 >= year >= 1998:
                    return 'Jaunieši'
                elif 1997 >= year >= 1996:
                    return 'Juniori'
                elif 1995 >= year >= 1980:
                    return 'Vīrieši'
                elif 1979 >= year >= 1975:
                    return 'Seniori I'
                elif 1974 >= year >= 1970:
                    return 'Seniori II'
                elif 1969 >= year >= 1965:
                    return 'Veterāni I'
                elif year <= 1964:
                    return 'Veterāni II'
            else:
                if 1999 >= year >= 1998:
                    return 'Jaunietes'
                elif 1997 >= year >= 1996:
                    return 'Juniores'
                elif 1995 >= year >= 1980:
                    return 'Sievietes'
                elif year <= 1979:
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

        doc = SimpleDocTemplate(output, pagesize=A4, showBoundary=0)
        elements = []
        elements.append(get_image(self.competition.logo.path, width=10*cm))
        elements.append(Paragraph(u"Apsveicam ar sekmīgu reģistrēšanos 31.Rīgas Velomaratonam, kas notiks šo svētdien, 1.jūnijā 11.novembra Krastmalā!", styles['h3']))

        data = [['Vārds, uzvārds:', participant.full_name],
                ['Dzimšanas gads:', participant.birthday.year],
                ['Distance:', participant.distance], ]
        if participant.primary_number:
            data.append(['Starta numurs', participant.primary_number.number])

        table_style = base_table_style[:]
        table_style.append(['FONTSIZE', (0, 0), (-1, -1), 16])
        table_style.append(['BOTTOMPADDING', (0, 0), (-1, -1), 10])


        elements.append(Table(data, style=table_style, hAlign='LEFT'))

        elements.append(Paragraph(u"Šo vēstuli, lūdzam saglabāt un izprintēt un ņemt līdzi uz Rīgas Velomaratona Expo centru, kas darbosies pie tirdzniecības centra „Spice” A ieejas 30. un 31.maijā no pkst.10:00-21:00.", styles['h3']))
        elements.append(Paragraph(u"Uzrādot šo vēstuli, Jūs varēsiet saņemt aploksni ar savu starta numuru. Lūdzam paņemt no reģistrācijas darbiniekiem instrukciju par pareizu numura piestiprināšanu.", styles['h3']))
        elements.append(Paragraph(u"Papildus informāciju meklējiet www.velo.lv", styles['h3']))
        elements.append(Paragraph(u"Vēlreiz apsveicam ar reģistrēšanos Rīgas Velomaratonam un novēlam veiksmīgu startu!", styles['h3']))

        elements.append(Paragraph(u"Rīga ir mūsu!", styles['title']))

        elements.append(Paragraph(u"Rīgas Velomaratona organizatori", styles['h3']))

        elements.append(Paragraph(u"Jautājumi?", styles['h2']))
        elements.append(Paragraph(u"Neskaidrību gadījumā sazinieties ar mums: pieteikumi@velo.lv", styles['h3']))

        doc.build(elements)
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


