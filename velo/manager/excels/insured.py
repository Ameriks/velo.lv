from django.template.defaultfilters import slugify
from io import BytesIO
import xlwt

from velo.core.models import Competition
from velo.registration.models import Participant


def create_insured_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    root_competition = competition.get_root()
    output = BytesIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(str(distance))[:30])

        participants = Participant.objects.filter(competition_id__in=competition.get_ids(), is_participating=True,distance=distance).exclude(insurance=None).select_related('competition', 'distance', 'insurance')

        row = 4
        header_row = ('#', 'Sacensības', 'Vārds', 'Uzvārds', 'Dzimšanas diena', 'Personas kods', 'Valsts', 'Pilsēta', 'Telefons', 'E-pasts', 'Summa', 'Nosaukums')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, item in enumerate(participants, start=1):
            insurance_price  = item.insurance.price
            if root_competition.id == 1 and item.competition.level == 1: # SEB complex
                insurance_price = (insurance_price * (100 - item.competition.complex_discount) / 100) * len(item.competition.get_children())

            row_values = (
                index, str(item.competition), item.first_name, item.last_name, str(item.birthday), item.ssn, str(item.country), str(item.city) if item.city else '', item.phone_number, item.email, insurance_price, str(item.insurance),)

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output
