import pytz
import xlwt
from io import BytesIO

from slugify import slugify

from velo.core.models import Competition
from velo.payment.models import Payment
from velo.registration.models import Participant, Number, Application
from velo.results.models import Result, SebStandings, HelperResults

riga_tz = pytz.timezone("Europe/Riga")


def create_standing_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)
    output = BytesIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()


    for distance in distances:
        sheet = wbk.add_sheet(str(distance))
        slugs = []

        items = SebStandings.objects.filter(competition_id__in=competition.get_ids(),distance=distance).select_related('participant', 'participant__competition', 'participant__distance', 'participant__price', 'participant__primary_number').order_by('participant__distance', 'participant__primary_number__group', 'participant__primary_number__number', 'participant__registration_dt')

        row = 4
        header_row = (
            '#', 'St.ID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums',
            'Grupa', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Rezultāts', 'Punkti', 'VISI piešķirtie numuri')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, item in enumerate(items, start=1):
            row_values = (
                index, item.id, str(item.participant.primary_number), item.participant_slug, str(item.participant.competition), str(item.participant.distance), item.participant.last_name,
                item.participant.first_name, item.participant.birthday.strftime("%Y-%m-%d"), item.participant.gender, item.participant.group,
                item.participant.email, item.participant.phone_number, str(item.participant.country), item.participant.team_name, str(item.participant.bike_brand2) if item.participant.bike_brand2 else '',
                item.distance_place, item.distance_total, ','.join([str(obj.number) for obj in item.participant.numbers()]))

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output


def payment_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)
    output = BytesIO()

    wbk = xlwt.Workbook()

    applications = Application.objects.filter(competition_id__in=competition.get_ids(),
                                              payment_status=Application.PAY_STATUS.payed)

    sheet = wbk.add_sheet('Applications')
    row = 4
    header_row = (
        'ID', 'Izveidots', 'Labots', 'Sacensības', 'Statuss', 'www.velo.lv ID', 'Uzņēmums', 'Rēķina numurs', 'Fināla cena',
        'Ebill kods', 'Ebill Statuss', 'Ebill summa', 'Ebill Kanāls')
    for col, value in enumerate(header_row):
        sheet.write(row, col, value)
    row += 1
    for application in applications:
        payments = application.payment_set.filter(status=Payment.STATUSES.ok)
        row_values = (
            application.id, application.created.date(), application.modified.date(), str(application.competition), application.get_payment_status_display(),
            application.legacy_id, application.company_name, application.invoice.invoice_nr if application.invoice else "",  application.final_price
        )
        for payment in payments:
            row_values += (
                payment.erekins_code, payment.get_status_display(), payment.total, str(payment.channel),
            )
        for col, value in enumerate(row_values):
            sheet.write(row, col, value)
        row += 1

    wbk.save(output)
    return output


def create_start_list(competition=None, competition_id=None):
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

        helperresults = HelperResults.objects.filter(competition=competition, participant__distance=distance, participant__is_participating=True).select_related('participant', 'participant__competition', 'participant__distance', 'participant__application',
                                                                                      'participant__price', 'participant__primary_number').order_by('participant__distance', 'participant__primary_number__group', 'participant__primary_number__number', 'participant__registration_dt')

        row = 4
        header_row = (
            '#', 'UID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums', 'Pilsēta', 'Sacenšas?',
            'Grupa', 'Pieteikuma ziedojums', 'Dalības maksa', 'Apdrošināšanas maksa', 'Kopā samaksāts', 'Atlaižu kods', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Izveidots', 'Punkti', 'Koridors', 'T-krekls')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, res in enumerate(helperresults, start=1):
            item = res.participant
            total_entry_fee = item.total_entry_fee
            total_insurance_fee = item.total_insurance_fee
            final_price = item.final_price

            if root_competition.id == 1 and item.competition.level == 1:
                child_count = item.competition.get_children().filter(is_individual=False).count()
                total_entry_fee = total_entry_fee / child_count
                total_insurance_fee = total_insurance_fee / child_count
                final_price = final_price / child_count

            donation = 0.0
            if item.application:
                donation = item.application.donation

            row_values = (
                index, item.id, str(item.primary_number), item.slug, str(item.competition), str(item.distance), item.last_name,
                item.first_name, item.birthday.strftime("%Y-%m-%d"), item.gender, str(item.city) if item.city else "", str(item.is_competing), item.group, donation, total_entry_fee, total_insurance_fee, final_price,
                str(item.application.discount_code or '') if item.application else '', item.email, item.phone_number, str(item.country), item.team_name, str(item.bike_brand2) if item.bike_brand2 else '',
                item.registration_dt.astimezone(riga_tz).strftime("%Y-%m-%d %H:%M"), res.calculated_total, res.passage_assigned if res.passage_assigned else "", item.t_shirt_size if item.t_shirt_size else '')

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output


def start_list_have_participated_this_year(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    root_competition = competition.get_root()
    child_competitions = competition.get_siblings()

    output = BytesIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()

    for distance in distances:
        slugs_participates = [obj.slug for obj in distance.participant_set.filter(is_participating=True, competition=competition)]
        sheet = wbk.add_sheet(slugify(str(distance))[:30])

        row = 4
        header_row = (
            '#', 'UID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums', 'Pilsēta',
            'Grupa', 'Pieteikuma ziedojums', 'Dalības maksa', 'Apdrošināšanas maksa', 'Kopā samaksāts', 'Atlaižu kods', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Izveidots', 'Rezultāts - Punkti')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        participants = distance.participant_set.filter(is_participating=True).filter(competition__in=child_competitions).exclude(slug__in=slugs_participates).order_by('distance', 'last_name', 'first_name', '-competition')

        row = 5
        for index, item in enumerate(participants, start=1):
            res = item.result_set.order_by('-points_distance')
            res_points = None
            if res:
                res_points = res[0].points_distance


            total_entry_fee = item.total_entry_fee
            total_insurance_fee = item.total_insurance_fee
            final_price = item.final_price

            if root_competition.id == 1 and item.competition.level == 1:
                child_count = item.competition.get_children().filter(is_individual=False).count()
                total_entry_fee = total_entry_fee / child_count
                total_insurance_fee = total_insurance_fee / child_count
                final_price = final_price / child_count

            donation = 0.0
            if item.application:
                donation = item.application.donation

            row_values = (
                index, item.id, str(item.primary_number), item.slug, str(item.competition), str(item.distance), item.last_name,
                item.first_name, item.birthday.strftime("%Y-%m-%d"), item.gender, str(item.city), item.group, donation, total_entry_fee, total_insurance_fee, final_price,
                str(item.application.discount_code or '') if item.application else '', item.email, item.phone_number, str(item.country), item.team_name, str(item.bike_brand2) if item.bike_brand2 else '',
                item.registration_dt.astimezone(riga_tz).strftime("%Y-%m-%d %H:%M"), res_points)

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output







def create_donations_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    root_competition = competition.get_root()

    output = BytesIO()

    wbk = xlwt.Workbook()

    sheet = wbk.add_sheet('donations')

    applications = Application.objects.filter(competition_id__in=competition.get_ids(), payment_status=Application.PAY_STATUS.payed).exclude(donation=0.0).prefetch_related('participant_set').select_related('competition')

    row = 1
    header_row = (
        '#', 'Pieteikuma ID', 'Sacensības', 'Uzvārds', 'Vārds', 'Personas kods', 'E-pasts', 'Pieteikuma ziedojums', 'Veiksmīgo maksājumu skaits', 'Veiksmiga maksajuma ziedojuma summa (check)', 'Rekina NR')
    for col, value in enumerate(header_row):
        sheet.write(row, col, value)

    row = 2
    for index, application in enumerate(applications, start=1):
        participant = application.participant_set.all()[0]
        total_payed = 0.0
        total_count = 0
        payments = application.payment_set.filter(status=Payment.STATUSES.ok)

        if payments:
            total_count = payments.count()
            total_payed = payments[0].donation

        row_values = (
            index, application.id, str(application.competition), participant.last_name,
            participant.first_name, participant.ssn, application.email, application.donation, total_count, total_payed, application.invoice.invoice_nr if application.invoice else "")

        for col, value in enumerate(row_values):
            sheet.write(row, col, value)
        row += 1

    wbk.save(output)
    return output




def team_member_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)
    output = BytesIO()
    distances = competition.get_distances().filter(can_have_teams=True)

    notpayed_pattern = xlwt.Pattern()
    notpayed_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    notpayed_pattern.pattern_fore_colour = 2

    not_payed_style = xlwt.XFStyle()
    not_payed_style.pattern = notpayed_pattern

    payed_style = xlwt.XFStyle()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(str(distance))[:30])

        row=0
        sheet.write(row, 0, "Team ID")
        sheet.write(row, 1, "Team Name")
        sheet.write(row, 2, "First Name")
        sheet.write(row, 3, "Last Name")
        sheet.write(row, 4, "Year")
        sheet.write(row, 5, "Kind")
        sheet.write(row, 6, "Found participant")
        sheet.write(row, 7, "Bike brand")
        sheet.write(row, 8, "Found unpaid")
        sheet.write(row, 9, "Found potential")
        sheet.write(row, 10, "NR")
        sheet.write(row, 11, "Papildus numuri")

        row += 1
        for team in distance.team_set.all():
            for member in competition.memberapplication_set.filter(member__team=team).order_by('kind').select_related('member', 'participant', 'participant_unpaid', 'participant_potential', 'participant__primary_number',):
                is_payed = True if member.participant_id else False
                sheet.write(row, 0, str(team.id), payed_style if is_payed else not_payed_style)
                sheet.write(row, 1, str(team), payed_style if is_payed else not_payed_style)
                sheet.write(row, 2, str(member.member.first_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 3, str(member.member.last_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 4, str(member.member.birthday.year), payed_style if is_payed else not_payed_style)
                sheet.write(row, 5, str(member.get_kind_display()), payed_style if is_payed else not_payed_style)
                sheet.write(row, 6, str(member.participant.slug) if member.participant else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 7, str(member.participant.bike_brand2) if member.participant and member.participant.bike_brand2 else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 8, str(member.participant_unpaid.slug) if member.participant_unpaid else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 9, str(member.participant_potential.slug) if member.participant_potential else '', payed_style if is_payed else not_payed_style)
                number = Number.objects.filter(participant_slug=member.member.slug, competition_id__in=competition.get_ids(), distance=team.distance).order_by('-number')
                if number:
                    sheet.write(row, 10, str(number[0]), payed_style if is_payed else not_payed_style)
                    if number.count()>1:
                        sheet.write(row, 11, str(','.join([str(obj.number) for obj in number[1:]])), payed_style if is_payed else not_payed_style)
                row += 1

    wbk.save(output)
    return output



def create_team_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    distances = competition.get_distances().filter(can_have_teams=True)

    output = BytesIO()

    notpayed_pattern = xlwt.Pattern()
    notpayed_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    notpayed_pattern.pattern_fore_colour = 0x16

    not_payed_style = xlwt.XFStyle()
    not_payed_style.pattern = notpayed_pattern

    payed_style = xlwt.XFStyle()



    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(str(distance))[:30])

        sheet.col(0).width = 256 * 4
        sheet.col(1).width = 256 * 4
        sheet.col(2).width = 256 * 5
        sheet.col(3).width = 256 * 20
        sheet.col(4).width = 256 * 5

        sheet.col(5).width = 256 * 4

        sheet.col(6).width = 256 * 4
        sheet.col(7).width = 256 * 4
        sheet.col(8).width = 256 * 5
        sheet.col(9).width = 256 * 20
        sheet.col(10).width = 256 * 5


        row = 5
        for index, team in enumerate(distance.team_set.filter(member__memberapplication__competition=competition, status__gte=0).defer('member__memberapplication__competition__params').distinct(), start=1):
            col_add = 0 if index % 2 == 1 else 6
            sheet.write(row, 0 + col_add, str(index))
            sheet.write(row, 1 + col_add, str(team))
            row += 1
            next_line = row
            for member in competition.memberapplication_set.filter(member__team=team).order_by('kind'):
                is_payed = True if member.participant_id else False



                sheet.write(row, 1 + col_add, str(member.get_kind_display())[0], payed_style if is_payed else not_payed_style)
                sheet.write(row, 2 + col_add, str(member.participant.primary_number) if member.participant else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 3 + col_add, str(member.member.full_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 4 + col_add, str(member.member.birthday.year), payed_style if is_payed else not_payed_style)


                row += 1
            if index % 2 == 0:
                row = next_line + 12
            else:
                row = next_line - 1

    wbk.save(output)
    return output


def create_temporary_participant_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    output = BytesIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(str(distance))[:30])

        participants = Participant.objects.filter(competition__in=competition.get_ids(), distance=distance, is_participating=True, is_temporary=True).select_related('competition', 'distance', 'application',
                                                                                      'price', 'primary_number').order_by('distance', 'primary_number__group', 'primary_number__number', 'registration_dt')
        row = 4
        header_row = (
            '#', 'UID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums', 'Pilsēta', 'Sacenšas?',
            'Grupa', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Izveidots')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, participant in enumerate(participants, start=1):

            row_values = (
                index, participant.id, str(participant.primary_number), participant.slug, str(participant.competition), str(participant.distance), participant.last_name,
                participant.first_name, participant.birthday.strftime("%Y-%m-%d"), participant.gender, str(participant.city) if participant.city else "", str(participant.is_competing), participant.group,
                participant.email, participant.phone_number, str(participant.country), participant.team_name, str(participant.bike_brand2) if participant.bike_brand2 else '',
                participant.created.astimezone(riga_tz).strftime("%Y-%m-%d %H:%M"))

            for col, value in enumerate(row_values):
                sheet.write(row, col, value)
            row += 1

    wbk.save(output)
    return output
