# coding=utf-8
from __future__ import unicode_literals
from difflib import get_close_matches
import pytz
import xlwt
import StringIO
from reportlab.lib import colors
from core.models import Competition
from core.pdf import getSampleStyleSheet, ParagraphStyle, PageNumCanvas, base_table_style
from registration.models import Participant
from results.models import Result, SebStandings, TeamResultStandings
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak, Image as pdfImage
from reportlab.lib.units import inch, cm
from team.models import MemberApplication
from velo.utils import load_class
from PIL import Image

riga_tz = pytz.timezone("Europe/Riga")

PAGE_HEIGHT = A4[1]
PAGE_WIDTH = A4[0]
styles = getSampleStyleSheet()

group_table_style = base_table_style[:] + [
    ('LINEABOVE', (0, 1), (-1, 1), 0.25, colors.black),
    ('LINEBELOW', (0, 1), (-1, 1), 0.25, colors.black),
    ('SPAN', (0, 0), (3, 0)),
    ('SPAN', (3, 0), (-1, 0)),
    ('ALIGNMENT', (3, 0), (-1, 0), 'RIGHT'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
]


class PDFReports(object):
    competition = None
    primary_competition = None
    output = None
    doc = None
    elements = None
    processing_class = None

    def __init__(self, competition=None, competition_id=None):
        if not competition and not competition_id:
            raise Exception('Expected at least one variable')
        if not competition:
            self.competition = Competition.objects.get(id=competition_id)
        else:
            self.competition = competition
        if self.competition.level == 2:
            self.primary_competition = self.competition.parent
        else:
            self.primary_competition = self.competition

        self.output = StringIO.StringIO()
        self.doc = SimpleDocTemplate(self.output, pagesize=A4, topMargin=0.2 * inch, bottomMargin=0.8 * inch,
                                     leftMargin=0.2 * inch, rightMargin=0.2 * inch, showBoundary=0)

        class_ = load_class(self.competition.processing_class)
        self.processing_class = class_(self.competition.id)

        self.elements = []

    def header(self, title):
        image = Image.open(self.primary_competition.logo.path)
        image_width, image_height = image.size
        new_image_height = 100
        new_image_width = (new_image_height * image_width) / image_height
        data = [
            [pdfImage(self.primary_competition.logo.path, width=new_image_width, height=new_image_height),
             [Paragraph(unicode(self.title), styles["Heading1"]), Paragraph(title, styles["Heading2"])], ],
        ]
        return Table(data, style=base_table_style)


    def result_table_group(self, items, point_attr='points_group'):
        try:
            top = [['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Komanda', 'Laiks', 'Vid.ātr.', 'Punkti']]
            data = []
            for obj in items:
                data.append([obj.result_group, obj.number, Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                             Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                             Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                             Paragraph(obj.participant.team_name, styles["SmallNormal"]),
                             Paragraph(obj.time.strftime("%H:%M:%S"), styles["SmallNormal"]),
                             Paragraph(str(obj.avg_speed), styles["SmallNormal"]),
                             Paragraph(str(obj.points_group), styles["SmallNormal"])])
        except Exception as e:
            import pdb;

            pdb.set_trace()
        return top + data

    def result_table_distance(self, items, point_attr='points_group'):
        try:
            top = [
                ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Komanda', 'Laiks', 'Vid.ātr.', 'Punkti', 'Grupa', 'Vieta grupā']]
            data = []
            for obj in items:
                data.append(
                    [obj.result_distance, obj.number, Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                     Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                     Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                     Paragraph(obj.participant.team_name, styles["SmallNormal"]),
                     Paragraph(obj.time.strftime("%H:%M:%S"), styles["SmallNormal"]),
                     Paragraph(str(obj.avg_speed), styles["SmallNormal"]),
                     Paragraph(str(obj.points_distance), styles["SmallNormal"]),
                     Paragraph(str(obj.participant.group), styles["SmallNormal"]),
                     Paragraph(str(obj.result_group), styles["SmallNormal"]), ])
        except Exception as e:
            import pdb;

            pdb.set_trace()
        return top + data


    @property
    def title(self):
        return "%s - %s" % (self.competition.parent, self.competition) if self.competition.level == 2 else unicode(
            self.competition)

    def results_standings(self, top=10000):
        col_width = (
            1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(unicode("Kopvērtējums pa distancēm")))

            self.elements.append(Spacer(10, 10))
            items = SebStandings.objects.filter(distance=distance, competition=self.primary_competition).order_by(
                '-distance_total').select_related('participant', 'competition', 'distance',
                                                 'participant__primary_number')[:top]
            data = [[Paragraph(unicode(distance), styles["Heading2"]), '', '', '', '', ''], ]
            if items:
                children_count = self.primary_competition.children.count()
                data_line = ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Grupa']
                for index in range(1, children_count + 1):
                    data_line.append('%i.' % index)
                data_line.append('Punkti kopā')
                data.append(data_line)
                for obj in items:
                    data_line = [str(obj.distance_place), unicode(obj.participant.primary_number),
                                 Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                                 Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                                 Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                                 Paragraph(str(obj.participant.group), styles["SmallNormal"])]
                    for index in range(1, children_count + 1):
                        data_line.append(str(getattr(obj, 'distance_points%i' % index)))

                    data_line.append(str(obj.distance_total))
                    data.append(data_line)
                self.elements.append(Table(data, style=group_table_style, colWidths=col_width))
            else:
                self.elements.append(Table(data, style=group_table_style))
                self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())


    def results_standings_groups(self, top=10000):
        col_width = (
            1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))

        children_count = self.primary_competition.children.count()

        for distance in distances:
            self.elements.append(self.header(unicode("Kopvērtējums pa grupām")))

            for group in self.processing_class.groups.get(distance.id):
                self.elements.append(Spacer(10, 10))
                items = SebStandings.objects.filter(distance=distance, competition=self.primary_competition,
                                                    participant__group=group).order_by('-group_total').select_related(
                    'participant', 'competition', 'distance', 'participant__primary_number')[:top]
                data = [[Paragraph(unicode(group), styles["Heading2"]), '', '', unicode(distance), '', ''], ]
                if items:
                    data_line = ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Grupa']
                    for index in range(1, children_count + 1):
                        data_line.append('%i.' % index)
                    data_line.append('Punkti kopā')
                    data.append(data_line)
                    for obj in items:
                        data_line = [str(obj.group_place), unicode(obj.participant.primary_number),
                                     Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                                     Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                                     Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                                     Paragraph(str(obj.participant.group), styles["SmallNormal"]), ]
                        for index in range(1, children_count + 1):
                            data_line.append(str(getattr(obj, 'group_points%i' % index)))

                        data_line.append(str(obj.group_total))
                        data.append(data_line)
                    self.elements.append(Table(data, style=group_table_style, colWidths=col_width))
                else:
                    self.elements.append(Table(data, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())


    def results_distance(self, top=10000):
        col_width = (1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 2 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(unicode("Rezultāti pa distancēm")))

            self.elements.append(Spacer(10, 10))
            items = Result.objects.filter(participant__distance=distance, competition=self.competition,
                                          status='').order_by('time').select_related('participant', 'number',
                                                                                     'participant__distance',
                                                                                     'competition',
                                                                                     'participant__competition')[:top]
            header = [[Paragraph(unicode(distance), styles["Heading2"]), '', '', '', '', ''], ]
            if items:
                self.elements.append(
                    Table(header + self.result_table_distance(items), style=group_table_style, colWidths=col_width))
            else:
                self.elements.append(Table(header, style=group_table_style))
                self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())


    def results_groups(self, top=10000):
        col_width = (1 * cm, 1 * cm, 3 * cm, 3 * cm, 2 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(unicode("Rezultāti pa grupām")))

            for group in self.processing_class.groups.get(distance.id):
                self.elements.append(Spacer(10, 10))
                items = Result.objects.filter(participant__distance=distance, participant__group=group,
                                              competition=self.competition, status='').order_by('time').select_related(
                    'participant', 'number', 'participant__distance', 'competition', 'participant__competition')[:top]
                header = [[Paragraph(unicode(group), styles["Heading2"]), '', '', unicode(distance), '', ''], ]
                if items:
                    self.elements.append(
                        Table(header + self.result_table_group(items), style=group_table_style, colWidths=col_width))
                else:
                    self.elements.append(Table(header, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def results_gender(self, top=10):
        col_width = (1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 2 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(unicode("Rezultāti pa dzimumiem")))
            for gender, gender_name in [('M', 'Vīrieši'), ('F', 'Sievietes')]:
                self.elements.append(Spacer(10, 10))
                items = Result.objects.filter(participant__distance=distance, participant__gender=gender,
                                              competition=self.competition, status='').order_by('time').select_related(
                    'participant', 'number', 'participant__distance', 'competition', 'participant__competition')[:top]
                header = [[Paragraph(unicode(gender_name), styles["Heading2"]), '', '', unicode(distance), '', ''], ]
                if items:
                    self.elements.append(
                        Table(header + self.result_table_distance(items), style=group_table_style, colWidths=col_width))
                else:
                    self.elements.append(Table(header, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())


    def results_team(self):
        col_width = (2 * cm, 1.5 * cm, 3 * cm, 3 * cm, 1 * cm, 2 * cm, 1 * cm, 2 * cm)
        distances = self.competition.get_distances().filter(can_have_teams=True)
        competition_index = self.processing_class.competition_index  # Get stage index

        team_table_style = base_table_style[:] + [
            ('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black),
            ('LINEBELOW', (1, 1), (-1, 1), 0.25, colors.black),
            ('SPAN', (1, 0), (5, 0)),
            ('ALIGNMENT', (3, 0), (-1, 0), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]


        for distance in distances:
            items = TeamResultStandings.objects.filter(team__distance=distance).filter(
                team__member__memberapplication__competition=self.competition,
                team__member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT,
                team__member__memberapplication__participant__result__competition=self.competition) \
                .order_by('-points%i' % competition_index, '-team__is_featured', 'team__title',
                          '-team__member__memberapplication__participant__result__points_distance',
                          'team__member__memberapplication__participant__primary_number__number', ) \
                .values('team__id',
                        'team__title',
                        'team__is_featured',
                        'team__teamresultstandings__points%i' % competition_index,
                        'team__member__first_name',
                        'team__member__last_name',
                        'team__member__birthday',
                        'team__member__memberapplication__participant__primary_number__number',
                        'team__member__memberapplication__participant__result__points_distance',
                        'team__member__memberapplication__participant__result__result_distance',
                        'team__member__memberapplication__participant__result__time',)
            self.elements.append(self.header(unicode("%s komandu rezultāti" % distance)))
            team_members = []
            team_place = 0
            for index, item in enumerate(items):
                if index == 0 or item.get('team__id') != items[index - 1].get('team__id'):
                    team_place += 1
                    team_members = [[Paragraph(str(team_place), styles["Heading2"]), Paragraph(item.get('team__title'), styles["Heading2"]), '', '', '', '','',
                                     Paragraph(str(item.get('team__teamresultstandings__points%i' % competition_index)),
                                               styles["Heading2"])],
                                    ['', 'Numurs', 'Vārds', 'Uzvārds', 'Gads', 'Laiks', 'Vieta', 'Punkti']]

                team_members.append(
                    ['', item.get('team__member__memberapplication__participant__primary_number__number'),
                     item.get('team__member__first_name'), item.get('team__member__last_name'),
                     str(item.get('team__member__birthday').year),
                     item.get('team__member__memberapplication__participant__result__time').replace(microsecond=0),
                     item.get('team__member__memberapplication__participant__result__result_distance'),
                     item.get('team__member__memberapplication__participant__result__points_distance')]
                )
                if len(items) == index + 1 or item.get('team__id') != items[index + 1].get('team__id'):
                    self.elements.append(Table(team_members, style=team_table_style, colWidths=col_width))
            self.elements.append(PageBreak())

    def results_team_standings(self):
        distances = self.competition.get_distances().filter(can_have_teams=True)
        children_count = self.primary_competition.children.count()
        for distance in distances:
            items = TeamResultStandings.objects.filter(team__distance=distance).order_by('-points_total', '-team__is_featured', 'team__title').select_related('team')
            self.elements.append(self.header(unicode("%s komandu rezultāti" % distance)))
            data = []
            data_line = ['Vieta', 'Nosaukums', ]
            for i in range(1, children_count+1):
                data_line.append('%i.' % i)
            data_line.append('Kopā')
            data.append(data_line)

            for index, item in enumerate(items, start=1):
                data_line = [str(index), item.team.title, ]
                for i in range(1, children_count+1):
                    data_line.append(str(getattr(item, 'points%i' % i, '') or ''))
                data_line.append(str(item.points_total))
                data.append(data_line)

            self.elements.append(Table(data, style=base_table_style))
            self.elements.append(PageBreak())



    def build(self):
        self.doc.build(self.elements, canvasmaker=PageNumCanvas)
        self.output.seek(0)
        return self.output