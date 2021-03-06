import csv
import datetime
import requests
import re
from bs4 import BeautifulSoup
from velo.core.models import Competition
from velo.payment.models import DiscountCode
from velo.velo.utils import load_class


def recalculate_participant(participant, children=None, commit=True):
    from velo.registration.models import ChangedName
    from velo.registration.models import Participant
    from velo.results.models import HelperResults
    if not children:
        children = participant.competition.get_children().filter(is_individual=False)

    pre_final_price = participant.final_price
    if (not participant.price and not participant.insurance_id) or not participant.is_paying:
        participant.final_price = participant.total_entry_fee = participant.total_insurance_fee = 0.0
    else:
        insurance = float(participant.insurance.price) if participant.insurance else 0.0
        entry_fee = float(participant.price.price) if participant.price else 0.0
        if participant.competition_id == 99:
            if participant.distance_id in (106, 107):
                slugs = list(ChangedName.objects.filter(new_slug=participant.slug).values_list('slug')) + [participant.slug, ]
                was_paticipant = Participant.objects.filter(competition_id=89, distance_id__in=(93, 94), is_participating=True, slug__in=slugs).exists()
                discount_until = datetime.date(2020, 1, 1)

                if was_paticipant:
                    entry_fee = 100

                if 2002 <= participant.birthday.year <= 2005:
                    entry_fee = 70
                elif datetime.datetime.now().date() <= discount_until:
                    if was_paticipant:
                        entry_fee = 100     # Sporta and Tautas distance pirms 01.01 un bija iepriekšējā gada abonements
                    else:
                        entry_fee = 115
                else:
                    entry_fee = 125     # Tautas distance after 05.01.2019

            if participant.distance_id == 108:       # Mammadaba Veselibas distance
                entry_fee = 70
            if participant.distance_id == 110:       # Mammadaba Zeni un Meitenes distance
                entry_fee = 50
            if participant.distance_id == 109:  # Bernu distance
                if participant.birthday.year in (2009, 2010, 2011, 2012, 2013):
                    entry_fee = 15
                else:
                    entry_fee = 10
        else:
            entry_fee = float(participant.price.price) if participant.price else 0.0

        if children:
            insurance = insurance * len(children) * (100 - participant.competition.complex_discount) / 100
            if not participant.competition_id == 99:
                entry_fee = entry_fee * len(children) * (100 - participant.competition.complex_discount) / 100

        if participant.application:
            dc = participant.application.discount_code
            if dc and dc.usage_times_left:
                discount_code = DiscountCode.objects.get(code=dc.code, campaign__competition_id=participant.competition_id)
                _class = load_class(discount_code.campaign.discount_kind)
                discount = _class(application=participant.application)
                entry_fee = discount.get_entry_fee_for_participant(participant=participant)
                if participant.insurance:
                    insurance = discount.get_insurance_fee_for_participant(participant=participant)

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


def import_lrf_licences_2017():
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
            elif col[idx] == 'Grupa':
                row_dict.update({"group": value})
            elif col[idx] == 'Licence derīga':
                try:
                    row_dict.update({"valid_until": datetime.datetime.strptime(value, '%d.%m.%Y')})
                except ValueError:
                    print(value, row_dict)
                    row_dict.update({"valid_until": datetime.datetime.strptime("31.12.2017", '%d.%m.%Y')})
            else:
                continue
        UCICategory.objects.update_or_create(**row_dict)


def import_lrf_licences_2018():
    from velo.registration.models import UCICategory
    get_params = {'limit': 100}

    for index in [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]:
        get_params.update({'startat': index})
        lrf_licence_html = requests.get('http://lrf.lv/index.php/licences/2019-gada-licencu-saraksts', params=get_params)
        beautiful_lrf_licence = BeautifulSoup(lrf_licence_html.text, 'html.parser')
        table = beautiful_lrf_licence.find('table', {'class': 'ui table'})
        columns = table.find('thead').find_all('th')
        col = []
        for column in columns:
            col.append(column.get_text().strip())
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            row_dict = {}
            for idx, cell in enumerate(row.find_all('td')):
                value = "" if cell.string is None else cell.string.strip()
                if col[idx] == "UCI kods":
                    if value.isnumeric():
                        row_dict.update({"code": "LAT" + value})
                    else:
                        # UCI ID column contains not only numeric values!
                        print(value)
                        row_dict.update({"code": "LAT" + ''.join(re.findall(r'\b\d+\b', value))})
                elif col[idx] == 'Uzvārds':
                    row_dict.update({"last_name": value})
                elif col[idx] == 'Vārds':
                    row_dict.update({"first_name": value})
                elif col[idx] == 'UCI kategorija':
                    row_dict.update({"category": value})
                elif col[idx] == 'Kategorija':
                    row_dict.update({"group": value})
                elif col[idx] == 'Lic.derīga':
                    if not value:
                        value = '31.12.2018'
                    row_dict.update({"valid_until": datetime.datetime.strptime(value, '%d.%m.%Y')})
                else:
                    continue
            UCICategory.objects.update_or_create(**row_dict)

