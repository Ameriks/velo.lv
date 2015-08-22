# coding=utf-8
from __future__ import unicode_literals
import StringIO
from difflib import get_close_matches
from registration.competition_classes.base_vb import VBCompetitionBase
from registration.models import Participant, ChangedName
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from core.pdf import get_image, getSampleStyleSheet, base_table_style, fill_page_with_image, _baseFontName, \
    _baseFontNameB
import os.path
from results.models import Result, HelperResults


class VB2015(VBCompetitionBase):
    SOSEJAS_DISTANCE_ID = 45
    MTB_DISTANCE_ID = 46
    TAUTAS_DISTANCE_ID = 47
    competition_index = 1

    @property
    def groups(self):
        """
        Returns defined groups for each competition type.
        """
        return {
            self.SOSEJAS_DISTANCE_ID: ('W-18', 'M-16', 'M-18', 'M-Elite', 'W', 'M-35', 'M-45', 'M-55', 'M-60'),
            self.MTB_DISTANCE_ID: ('MTB M-14', 'MTB W-18', 'MTB M-16', 'MTB M-18', 'MTB M-Elite', 'MTB W', 'MTB M-35', 'MTB M-45', 'MTB M-55', 'MTB M-65', ),
            self.TAUTAS_DISTANCE_ID: ('T M', 'T W', )
        }

    def _update_year(self, year):
        return year + 1

    def assign_group(self, distance_id, gender, birthday):
        year = birthday.year
        if distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
            return ''
        elif distance_id == self.SOSEJAS_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(1999) >= year >= self._update_year(1998):
                    return 'M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'M-Elite'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'M-55'
                elif year <= self._update_year(1949):
                    return 'M-60'
            else:
                if self._update_year(1999) >= year >= self._update_year(1996):
                    return 'W-18'
                elif year <= self._update_year(1995):
                    return 'W'
        elif distance_id == self.MTB_DISTANCE_ID:
            if gender == 'M':
                if self._update_year(2002) >= year >= self._update_year(2000):
                    return 'MTB M-14'
                elif self._update_year(1999) >= year >= self._update_year(1998):
                    return 'MTB M-16'
                elif self._update_year(1997) >= year >= self._update_year(1996):
                    return 'MTB M-18'
                elif self._update_year(1995) >= year >= self._update_year(1980):
                    return 'MTB M-Elite'
                elif self._update_year(1979) >= year >= self._update_year(1970):
                    return 'MTB M-35'
                elif self._update_year(1969) >= year >= self._update_year(1960):
                    return 'MTB M-45'
                elif self._update_year(1959) >= year >= self._update_year(1950):
                    return 'MTB M-55'
                elif year <= self._update_year(1949):
                    return 'MTB M-65'
            else:
                if self._update_year(2002) >= year >= self._update_year(1996):
                    return 'MTB W-18'
                elif year <= self._update_year(1995):
                    return 'MTB W'
        elif distance_id == self.TAUTAS_DISTANCE_ID:
            if gender == 'M':
                return 'T M'
            else:
                return 'T W'

        print 'here I shouldnt be...'
        raise Exception('Invalid group assigning. {0} {1} {2}'.format(gender, distance_id, birthday))


    def number_pdf(self, participant_id):
        raise NotImplementedError
        participant = Participant.objects.get(id=participant_id)
        styles = getSampleStyleSheet()
        output = StringIO.StringIO()

        doc = SimpleDocTemplate(output, pagesize=A4, showBoundary=0)
        elements = []

        if self.competition.logo:
            elements.append(get_image(self.competition.logo.path, width=10*cm))
        elements.append(Paragraph(u"Apsveicam ar sekmīgu reģistrēšanos 24.Latvijas riteņbraucēju Vienības braucienam, kas notiks šo svētdien, 7.septembrī Siguldā!", styles['h3']))

        data = [['Vārds, uzvārds:', participant.full_name],
                ['Dzimšanas gads:', participant.birthday.year],
                ['Distance:', participant.distance], ]
        if participant.primary_number:
            data.append(['Starta numurs', participant.primary_number.number])

        table_style = base_table_style[:]
        table_style.append(['FONTSIZE', (0, 0), (-1, -1), 16])
        table_style.append(['BOTTOMPADDING', (0, 0), (-1, -1), 10])

        elements.append(Spacer(10, 10))
        elements.append(Table(data, style=table_style, hAlign='LEFT'))
        elements.append(Spacer(10, 10))
        elements.append(Paragraph(u"Šo vēstuli lūdzam saglabāt, izprintēt un uzrādīt saņemot starta numuru.", styles['h3']))
        elements.append(Paragraph(u"Starta numurus iespējams saņemt 5. un 6.septembrī pie u/v Elkor Plaza (Brīvības gatve 201, Rīga) laikā no 10:00 līdz 20:00 vai arī 7.septembrī Siguldā, reģistrācijas teltī no 09:00.", styles['h3']))

        elements.append(Paragraph(u"Lūdzam paņemt no reģistrācijas darbiniekiem instrukciju par pareizu numura piestiprināšanu.", styles['h3']))
        elements.append(Paragraph(u"Papildus informāciju meklējiet www.velo.lv", styles['h3']))

        elements.append(Paragraph(u"Vēlreiz apsveicam ar reģistrēšanos Vienības braucienam un novēlam veiksmīgu startu!", styles['h3']))

        elements.append(Paragraph(u"Sajūti kopīgo spēku!", styles['title']))

        elements.append(Paragraph(u"Sacensību organizatori", styles['h3']))

        elements.append(Paragraph(u"Jautājumi?", styles['h2']))
        elements.append(Paragraph(u"Neskaidrību gadījumā sazinieties ar mums: pieteikumi@velo.lv", styles['h3']))

        doc.build(elements)
        return output

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
        prev_competition = self.competition.get_previous_sibling()

        prev_slugs_road = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='V').select_related('participant')]
        prev_slugs_mtb = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='S').select_related('participant')]
        prev_slugs_tauta = [obj.participant.slug for obj in Result.objects.filter(competition=prev_competition, participant__distance__kind='T').select_related('participant')]

        for participant in participants:
            results = Result.objects.filter(competition=prev_competition, participant__slug=participant.slug, participant__distance__kind=participant.distance.kind).order_by('time')

            if not results:
                try:
                    changed = ChangedName.objects.get(new_slug=participant.slug)
                    results = Result.objects.filter(competition=prev_competition, participant__slug=changed.slug, participant__distance__kind=participant.distance.kind).order_by('time')
                except:
                    pass


            helper, created = HelperResults.objects.get_or_create(competition=self.competition, participant=participant)

            if participant.distance_id not in (self.SOSEJAS_DISTANCE_ID, self.MTB_DISTANCE_ID, self.TAUTAS_DISTANCE_ID):
                continue

            if helper.is_manual:
                continue # We do not want to overwrite manually created records

            if results:
                result = results[0]
                helper.calculated_total = result.result_distance
                helper.result_used = result
            else:
                helper.calculated_total = None
                matches = None
                if participant.distance_id == self.SOSEJAS_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_road, 1, 0.8)
                elif participant.distance_id == self.MTB_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_mtb, 1, 0.8)
                elif participant.distance_id == self.TAUTAS_DISTANCE_ID:
                    matches = get_close_matches(participant.slug, prev_slugs_tauta, 1, 0.8)

                if matches:
                    helper.matches_slug = matches[0]

            helper.save()
