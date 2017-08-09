import csv
import datetime
import requests
import re
from bs4 import BeautifulSoup
from velo.core.models import Competition


def recalculate_participant(participant, children=None, commit=True):
    if not children:
        children = participant.competition.get_children().filter(is_individual=False)

    pre_final_price = participant.final_price
    if (not participant.price and not participant.insurance_id) or not participant.is_participating or not participant.is_paying:
        participant.final_price = participant.total_entry_fee = participant.total_insurance_fee = 0.0
    else:
        insurance = float(participant.insurance.price) if participant.insurance else 0.0
        entry_fee = float(participant.price.price) if participant.price else 0.0

        if children:
            insurance = insurance * len(children) * (100 - participant.competition.complex_discount) / 100
            entry_fee = entry_fee * len(children) * (100 - participant.competition.complex_discount) / 100

        if participant.application:
            dc = participant.application.discount_code
            if dc:
                insurance = dc.calculate_insurance(insurance)
                entry_fee = dc.calculate_entry_fee(entry_fee)

        participant.total_entry_fee = entry_fee
        participant.total_insurance_fee = insurance

    participant.final_price = participant.total_insurance_fee + participant.total_entry_fee

    if pre_final_price != participant.final_price and commit:
        print('saved %s' % participant.id)
        participant.save()


def recalculate_participant_final_payment(competition_id):
    competition = Competition.objects.get(id=competition_id)
    children = competition.get_children()

    for participant in competition.participant_set.all().select_related('competition', ):
        recalculate_participant(participant, children)


def update_uci_category(filename):
    from velo.registration.models import UCICategory
    with open(filename, 'r') as csvfile:
        participants = csv.reader(csvfile)
        next(participants)  # skip header
        for row in participants:
            if not row[2] or not row[3]:  # if not first name or last name then skip
                continue

            category = row[0].upper()
            if category == 'CYCLING FOR ALL':
                birthday = datetime.datetime.strptime(row[10], "%m/%d/%Y")
                issued = datetime.datetime.strptime(row[7], "%m/%d/%Y")
                UCICategory.objects.get_or_create(category=category,
                                                  first_name=row[3].upper(),
                                                  last_name=row[2].upper(),
                                                  code=row[8].upper(),
                                                  birthday=birthday,
                                                  issued=issued)


def import_lrf_licences():
    from velo.registration.models import UCICategory
    lrf_licence_html = requests.get('http://lrf.lv/index.php/licences/2017-gada-licencu-saraksts?limit=false&start=0')
    beautiful_lrf_licence = BeautifulSoup(lrf_licence_html.text, 'html.parser')
    table = beautiful_lrf_licence.find('table', id="licences")
    columns = table.find('thead').find_all('th')
    col = []
    for column in columns:
        col.append(column.string)
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        row_dict = {}
        for idx, cell in enumerate(row):
            value = "" if cell.string is None else cell.string
            if col[idx] == "UCI ID":
                if value.isnumeric():
                    row_dict.update({"code": "LAT" + value})
                else:
                    # UCI ID column contains not only numeric values!
                    print(value)
                    row_dict.update({"code": "LAT" + ''.join(re.findall(r'\b\d+\b', value))})
            elif col[idx] == 'Dzimšanas dati':
                if not value == "00.00.":
                    if value == '24.11.92':
                        value = '24.11.1992'
                    value = value.rstrip('.')
                    row_dict.update({"birthday": datetime.datetime.strptime(value, '%d.%m.%Y')})
            elif col[idx] == 'Uzvārds':
                row_dict.update({"last_name": value})
            elif col[idx] == 'Vārds':
                row_dict.update({"first_name": value})
            elif col[idx] == 'Veids':
                row_dict.update({"category": value})
            elif col[idx] == 'Licence derīga':
                try:
                    row_dict.update({"valid_until": datetime.datetime.strptime(value, '%d.%m.%Y')})
                except ValueError:
                    print(value, row_dict)
                    row_dict.update({"valid_until": datetime.datetime.strptime("31.12.2017", '%d.%m.%Y')})
            else:
                continue
        UCICategory.objects.update_or_create(**row_dict)

