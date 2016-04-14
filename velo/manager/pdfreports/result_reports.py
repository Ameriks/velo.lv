# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.db import connection

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, PageBreak, Image as pdfImage
from reportlab.lib.units import inch, cm
from PIL import Image
from io import StringIO
import pytz

from velo.core.models import Competition
from velo.core.pdf import getSampleStyleSheet, PageNumCanvas, base_table_style
from velo.results.models import Result, SebStandings, TeamResultStandings
from velo.team.models import MemberApplication
from velo.velo.utils import load_class

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

        self.output = StringIO()
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
             [Paragraph(str(self.title), styles["Heading1"]), Paragraph(title, styles["Heading2"])], ],
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
        return "%s - %s" % (self.competition.parent, self.competition) if self.competition.level == 2 else str(
            self.competition)

    def results_standings(self, top=10000):
        col_width = (
            1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm,
            1 * cm, 1 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(str("Kopvērtējums pa distancēm")))

            self.elements.append(Spacer(10, 10))
            items = SebStandings.objects.filter(distance=distance, competition=self.primary_competition).order_by(
                '-distance_total').select_related('participant', 'competition', 'distance',
                                                  'participant__primary_number')[:top]
            data = [[Paragraph(str(distance), styles["Heading2"]), '', '', '', '', ''], ]
            if items:
                children_count = self.primary_competition.children.count()
                data_line = ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Grupa']
                for index in range(1, children_count + 1):
                    data_line.append('%i.' % index)
                data_line.append('Punkti kopā')
                data.append(data_line)
                for obj in items:
                    data_line = [str(obj.distance_place), str(obj.participant.primary_number),
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

    def results_standings_gender(self, top=10000):
        col_width = (
            1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm,
            1 * cm, 1 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(str("Kopvērtējums pa dzimumiem")))
            for gender, gender_name in [('M', 'Vīrieši'), ('F', 'Sievietes')]:
                self.elements.append(Spacer(10, 10))
                data = [[Paragraph(str(gender_name), styles["Heading2"]), '', '', str(distance), '', ''], ]

                items = SebStandings.objects.filter(distance=distance, participant__gender=gender,
                                                    competition=self.primary_competition).order_by(
                    '-distance_total').select_related('participant', 'competition', 'distance',
                                                      'participant__primary_number')[:top]
                if items:
                    children_count = self.primary_competition.children.count()
                    data_line = ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Grupa']
                    for index in range(1, children_count + 1):
                        data_line.append('%i.' % index)
                    data_line.append('Punkti kopā')
                    data.append(data_line)
                    for obj in items:
                        data_line = [str(obj.distance_place), str(obj.participant.primary_number),
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
            1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 1.5 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm, 1 * cm,
            1 * cm, 1 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))

        children_count = self.primary_competition.children.count()

        for distance in distances:
            self.elements.append(self.header(str("Kopvērtējums pa grupām")))

            for group in self.processing_class.groups.get(distance.id):
                self.elements.append(Spacer(10, 10))
                items = SebStandings.objects.filter(distance=distance, competition=self.primary_competition,
                                                    participant__group=group).order_by('-group_total').select_related(
                    'participant', 'competition', 'distance', 'participant__primary_number')[:top]
                data = [[Paragraph(str(group), styles["Heading2"]), '', '', str(distance), '', ''], ]
                if items:
                    data_line = ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Grupa']
                    for index in range(1, children_count + 1):
                        data_line.append('%i.' % index)
                    data_line.append('Punkti kopā')
                    data.append(data_line)
                    for obj in items:
                        data_line = [str(obj.group_place), str(obj.participant.primary_number),
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
        col_width = (
        1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa distancēm")))

            self.elements.append(Spacer(10, 10))
            items = Result.objects.filter(participant__distance=distance, competition=self.competition,
                                          status='').order_by('time').select_related('participant', 'number',
                                                                                     'participant__distance',
                                                                                     'competition',
                                                                                     'participant__competition')[:top]
            header = [[Paragraph(str(distance), styles["Heading2"]), '', '', '', '', ''], ]
            if items:
                self.elements.append(
                    Table(header + self.result_table_distance(items), style=group_table_style, colWidths=col_width))
            else:
                self.elements.append(Table(header, style=group_table_style))
                self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def results_groups(self, top=10000):
        col_width = (1 * cm, 1 * cm, 3 * cm, 3 * cm, 1.5 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa grupām")))

            for group in self.processing_class.groups.get(distance.id):
                self.elements.append(Spacer(10, 10))
                items = Result.objects.filter(participant__distance=distance, participant__group=group,
                                              competition=self.competition, status='').order_by('time').select_related(
                    'participant', 'number', 'participant__distance', 'competition', 'participant__competition')[:top]
                header = [[Paragraph(str(group), styles["Heading2"]), '', '', str(distance), '', ''], ]
                if items:
                    self.elements.append(
                        Table(header + self.result_table_group(items), style=group_table_style, colWidths=col_width))
                else:
                    self.elements.append(Table(header, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def results_gender(self, top=10):
        col_width = (
        1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 4 * cm, 2 * cm, 1.2 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True).exclude(
            id=getattr(self.processing_class, 'BERNU_DISTANCE_ID', -1))
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa dzimumiem")))
            for gender, gender_name in [('M', 'Vīrieši'), ('F', 'Sievietes')]:
                self.elements.append(Spacer(10, 10))
                items = Result.objects.filter(participant__distance=distance, participant__gender=gender,
                                              competition=self.competition, status='').order_by('time').select_related(
                    'participant', 'number', 'participant__distance', 'competition', 'participant__competition')[:top]
                header = [[Paragraph(str(gender_name), styles["Heading2"]), '', '', str(distance), '', ''], ]
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
                        'team__member__memberapplication__participant__result__time', )
            self.elements.append(self.header(str("%s komandu rezultāti" % distance)))
            team_members = []
            team_place = 0
            for index, item in enumerate(items):
                if index == 0 or item.get('team__id') != items[index - 1].get('team__id'):
                    team_place += 1
                    team_members = [[Paragraph(str(team_place), styles["Heading2"]),
                                     Paragraph(item.get('team__title'), styles["Heading2"]), '', '', '', '', '',
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
            items = TeamResultStandings.objects.filter(team__distance=distance).order_by('-points_total',
                                                                                         '-team__is_featured',
                                                                                         'team__title').select_related(
                'team')
            self.elements.append(self.header(str("%s komandu rezultāti" % distance)))
            data = []
            data_line = ['Vieta', 'Nosaukums', ]
            for i in range(1, children_count + 1):
                data_line.append('%i.' % i)
            data_line.append('Kopā')
            data.append(data_line)

            for index, item in enumerate(items, start=1):
                data_line = [str(index), item.team.title, ]
                for i in range(1, children_count + 1):
                    data_line.append(str(getattr(item, 'points%i' % i, '') or ''))
                data_line.append(str(item.points_total))
                data.append(data_line)

            self.elements.append(Table(data, style=base_table_style))
            self.elements.append(PageBreak())

    def RM_result_table_distance(self, items):
        top = [
            ['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Komanda', 'Apļi', 'Laiks', 'Vid.ātr.', 'Grupa', 'Vieta grupā']]
        data = []
        for obj in items:
            laps = []
            if obj.l1:
                laps.append('%s: %s' % (1, obj.l1.strftime("%H:%M:%S")))
            if obj.l2:
                laps.append('%s: %s' % (2, obj.l2.strftime("%H:%M:%S")))
            if obj.l3:
                laps.append('%s: %s' % (3, obj.l3.strftime("%H:%M:%S")))
            if obj.l4:
                laps.append('%s: %s' % (4, obj.l4.strftime("%H:%M:%S")))
            if obj.l5:
                laps.append('%s: %s' % (5, obj.l5.strftime("%H:%M:%S")))

            if obj.time and laps:
                laps.pop()

            data.append(
                [obj.result_distance, obj.number, Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                 Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                 Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                 Paragraph(obj.participant.team_name, styles["SmallNormal"]),
                 Paragraph(str("<br />\n".join(laps)), styles["XSmallNormal"]),
                 Paragraph(obj.time.strftime("%H:%M:%S") if obj.time else "", styles["SmallNormal"]),
                 Paragraph(str(obj.avg_speed), styles["SmallNormal"]),
                 Paragraph(obj.participant.group, styles["SmallNormal"]),
                 Paragraph(str(obj.result_group) if obj.result_group else "", styles["SmallNormal"]), ])
        return top + data

    def RM_results_distance(self, top=10000):
        col_width = (
        1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 3.5 * cm, 1.5 * cm, 1.8 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True)
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa distancēm")))

            self.elements.append(Spacer(10, 10))
            items = Result.objects.filter(participant__distance=distance, competition=self.competition,
                                          status='').extra(
                select={
                    'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                    'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                    'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                    'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
                    'l5': 'SELECT time FROM results_lapresult l5 WHERE l5.result_id = results_result.id and l5.index=5',
                },
            ).order_by('time', 'l4', 'l3', 'l2', 'l1').select_related('participant', 'number',
                                                                      'participant__distance',
                                                                      'competition',
                                                                      'participant__competition')[:top]
            header = [[Paragraph(str(distance), styles["Heading2"]), '', '', '', '', ''], ]
            if items:
                self.elements.append(
                    Table(header + self.RM_result_table_distance(items), style=group_table_style, colWidths=col_width))
            else:
                self.elements.append(Table(header, style=group_table_style))
                self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def RM_results_gender(self, top=10):
        col_width = (
        1 * cm, 1 * cm, 2.5 * cm, 2.5 * cm, 1.5 * cm, 3.5 * cm, 1.5 * cm, 1.8 * cm, 1.2 * cm, 1.4 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True)
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa dzimumiem")))
            for gender, gender_name in [('M', 'Vīrieši'), ('F', 'Sievietes')]:
                self.elements.append(Spacer(10, 10))
                items = Result.objects.filter(participant__distance=distance, participant__gender=gender,
                                              competition=self.competition,
                                              status='').extra(
                    select={
                        'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                        'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                        'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                        'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
                        'l5': 'SELECT time FROM results_lapresult l5 WHERE l5.result_id = results_result.id and l5.index=5',
                    },
                ).order_by('time', 'l4', 'l3', 'l2', 'l1').select_related('participant', 'number',
                                                                          'participant__distance',
                                                                          'competition',
                                                                          'participant__competition')[:top]

                header = [[Paragraph(str(gender_name), styles["Heading2"]), '', '', str(distance), '', ''], ]
                if items:
                    self.elements.append(
                        Table(header + self.RM_result_table_distance(items), style=group_table_style,
                              colWidths=col_width))
                else:
                    self.elements.append(Table(header, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def RM_result_table_group(self, items, point_attr='points_group'):
        top = [['', '#', 'Vārds', 'Uzvārds', 'Gads', 'Komanda', 'Apļi', 'Laiks', 'Vid.ātr.']]
        data = []
        for obj in items:

            laps = []
            if obj.l1:
                laps.append('%s: %s' % (1, obj.l1.strftime("%H:%M:%S")))
            if obj.l2:
                laps.append('%s: %s' % (2, obj.l2.strftime("%H:%M:%S")))
            if obj.l3:
                laps.append('%s: %s' % (3, obj.l3.strftime("%H:%M:%S")))
            if obj.l4:
                laps.append('%s: %s' % (4, obj.l4.strftime("%H:%M:%S")))
            if obj.l5:
                laps.append('%s: %s' % (5, obj.l5.strftime("%H:%M:%S")))

            if obj.time and laps:
                laps.pop()

            data.append([obj.result_group, obj.number, Paragraph(obj.participant.first_name, styles["SmallNormal"]),
                         Paragraph(obj.participant.last_name, styles["SmallNormal"]),
                         Paragraph(str(obj.participant.birthday.year), styles["SmallNormal"]),
                         Paragraph(obj.participant.team_name, styles["SmallNormal"]),
                         Paragraph(str("<br />\n".join(laps)), styles["XSmallNormal"]),
                         Paragraph(obj.time.strftime("%H:%M:%S") if obj.time else "", styles["SmallNormal"]),
                         Paragraph(str(obj.avg_speed), styles["SmallNormal"]), ])
        return top + data

    def RM_results_groups(self, top=10000):
        col_width = (1 * cm, 1 * cm, 3 * cm, 3 * cm, 1.5 * cm, 4 * cm, 1.5 * cm, 1.8 * cm, 1.2 * cm)
        distances = self.competition.get_distances().filter(have_results=True)
        for distance in distances:
            self.elements.append(self.header(str("Rezultāti pa grupām")))

            for group in self.processing_class.groups.get(distance.id):
                self.elements.append(Spacer(10, 10))

                items = Result.objects.filter(participant__distance=distance, competition=self.competition,
                                              participant__group=group,
                                              status='').extra(
                    select={
                        'l1': 'SELECT time FROM results_lapresult l1 WHERE l1.result_id = results_result.id and l1.index=1',
                        'l2': 'SELECT time FROM results_lapresult l2 WHERE l2.result_id = results_result.id and l2.index=2',
                        'l3': 'SELECT time FROM results_lapresult l3 WHERE l3.result_id = results_result.id and l3.index=3',
                        'l4': 'SELECT time FROM results_lapresult l4 WHERE l4.result_id = results_result.id and l4.index=4',
                        'l5': 'SELECT time FROM results_lapresult l5 WHERE l5.result_id = results_result.id and l5.index=5',
                    },
                ).order_by('time', 'l5', 'l4', 'l3', 'l2', 'l1').select_related('participant', 'number',
                                                                                'participant__distance',
                                                                                'competition',
                                                                                'participant__competition')[:top]

                header = [[Paragraph(str(group), styles["Heading2"]), '', '', str(distance), '', ''], ]
                if items:
                    self.elements.append(
                        Table(header + self.RM_result_table_group(items), style=group_table_style, colWidths=col_width))
                else:
                    self.elements.append(Table(header, style=group_table_style))
                    self.elements.append(Paragraph("Nav rezultātu", styles['Normal']))
            self.elements.append(PageBreak())

    def RM_results_team(self):
        col_width = (2 * cm, 1.5 * cm, 3 * cm, 3 * cm, 1 * cm, 2 * cm, 1 * cm, 3 * cm)
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

            cursor = connection.cursor()
            cursor.execute("""
    Select *, DATE_TRUNC('second', total) from (
    Select kopa.team_name_slug, count(*) counter, sum(kopa.time) total
    from (
    Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) kopa group by kopa.team_name_slug
    having count(*)>1
    order by total
    ) team
    left outer join
    (
    Select p.team_name, p.team_name_slug, p.time,p.first_name,p.last_name,p.birthday,p.team_name,p.number from (
    SELECT
        a.*,
        r.time,
        nr.number,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        left outer join registration_number nr on nr.id = a.primary_number_id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) participant on team.team_name_slug = participant.team_name_slug
    order by counter desc, total, team.team_name_slug, time
    """, [distance.id, distance.id])
            object_list = cursor.fetchall()

            self.elements.append(self.header(str("%s komandu rezultāti" % distance)))
            team_members = []
            team_place = 0

            current_team_name = ""
            current_team_index = 0
            current_team_member_index = 0

            for index, item in enumerate(object_list):
                if item[0] != current_team_name:
                    current_team_name = item[0]
                    current_team_index += 1
                    current_team_member_index = 1

                    team_members = [
                        [Paragraph(str(current_team_index), styles["Heading2"]), Paragraph(item[3], styles["Heading2"]),
                         '', '', '', '', '',
                         Paragraph(str(item[11]),
                                   styles["Heading2"])],
                        ['', 'Numurs', 'Vārds', 'Uzvārds', 'Gads', 'Laiks', '', '']]

                else:
                    current_team_member_index += 1

                team_members.append(
                    ['', item[10],
                     item[6], item[7],
                     str(item[8].year),
                     item[5].replace(microsecond=0),
                     '', '']
                )
                if len(object_list) == index + 1 or item[0] != object_list[index + 1][0]:
                    self.elements.append(Table(team_members, style=team_table_style, colWidths=col_width))
            self.elements.append(PageBreak())

    def build(self):
        self.doc.build(self.elements, canvasmaker=PageNumCanvas)
        self.output.seek(0)
        return self.output
