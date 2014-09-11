# coding=utf-8
from __future__ import unicode_literals
from django.template.defaultfilters import slugify
import xlwt
import StringIO
from core.models import Competition
from registration.models import Participant


def create_insured_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)
    output = StringIO.StringIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(distance.__unicode__())[:30])

        participants = Participant.objects.filter(competition_id__in=competition.get_ids(), is_participating=True,distance=distance).exclude(insurance=None).select_related('competition', 'distance', 'insurance')

        row = 4
        header_row = ('#', 'Sacensības', 'Vārds', 'Uzvārds', 'Dzimšanas diena', 'Personas kods', 'Valsts', 'Telefons', 'E-pasts', 'Summa', 'Nosaukums')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, item in enumerate(participants, start=1):
            row_values = (
                index, unicode(item.competition), item.first_name, item.last_name, unicode(item.birthday), item.ssn, item.country, item.phone_number, item.email, item.insurance.price, unicode(item.insurance),)

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output
