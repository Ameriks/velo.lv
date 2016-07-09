import csv
import datetime
from velo.core.models import Competition


def recalculate_participant(participant, children=None, commit=True):
    if not children:
        children = participant.competition.get_children()

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
