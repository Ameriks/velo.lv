# coding=utf-8
from __future__ import unicode_literals
from difflib import get_close_matches
from django.template.defaultfilters import slugify
import pytz
import xlwt
import StringIO
from core.models import Competition
from registration.models import Participant, Number
from results.models import Result, SebStandings

riga_tz = pytz.timezone("Europe/Riga")


def create_standing_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)
    output = StringIO.StringIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()


    for distance in distances:
        sheet = wbk.add_sheet(distance.__unicode__())
        slugs = []

        items = SebStandings.objects.filter(competition_id__in=competition.get_ids(),distance=distance).select_related('participant', 'participant__competition', 'participant__distance', 'participant__price', 'participant__bike_brand', 'participant__primary_number').order_by('participant__distance', 'participant__primary_number__group', 'participant__primary_number__number', 'participant__registration_dt')

        row = 4
        header_row = (
            '#', 'St.ID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums',
            'Grupa', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Rezultāts', 'Punkti', 'VISI piešķirtie numuri')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, item in enumerate(items, start=1):
            row_values = (
                index, item.id, unicode(item.participant.primary_number), item.participant_slug, unicode(item.participant.competition), unicode(item.participant.distance), item.participant.last_name,
                item.participant.first_name, item.participant.birthday.strftime("%Y-%m-%d"), item.participant.gender, item.participant.group,
                item.participant.email, item.participant.phone_number, unicode(item.participant.country), item.participant.team_name, unicode(item.participant.bike_brand) if item.participant.bike_brand else '',
                item.distance_place, item.distance_total, ','.join([str(obj.number) for obj in item.participant.numbers()]))

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
    output = StringIO.StringIO()
    distances = competition.get_distances()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(distance.__unicode__())[:30])
        slugs = []
        items = distance.participant_set.filter(competition_id__in=competition.get_ids(),
                                                is_participating=True).select_related('competition', 'distance',
                                                                                      'price', 'bike_brand', 'primary_number').order_by('distance', 'primary_number__group', 'primary_number__number', 'registration_dt')

        if competition.tree_id == 1 or competition.tree_id == 2: # SEB
            prev = competition.get_previous_sibling()
            if prev:
                slugs = [obj.participant_slug for obj in SebStandings.objects.filter(competition=competition.parent.id, distance=distance)]

                if distance.id == 27:
                    select = 'group_place'
                else:
                    select = 'distance_place'

                items = items.extra(
                    select={
                        'last_result_distance': "SELECT r."+select+" FROM results_sebstandings r WHERE r.competition_id=%s and r.participant_slug=registration_participant.slug and r.distance_id=registration_participant.distance_id",
                    },
                    select_params=(competition.parent.id, ),
                )

                items = items.extra(
                    select={
                        'comp_count': "Select count(*) from registration_participant p_count left outer join core_competition cc_count on p_count.competition_id = cc_count.id WHERE p_count.slug = registration_participant.slug and p_count.is_participating is True and (cc_count.id = %s or cc_count.parent_id = %s) AND cc_count.id <> %s"
                    },
                    select_params=(competition.parent.id, competition.parent.id, competition.id),
                )
        elif competition.id == 35:
            items = items.extra(
                select={
                    'last_result_distance': "SELECT r.result_distance FROM results_legacyresult r WHERE r.participant_2014_id=registration_participant.id and r.distance_id = registration_participant.distance_id order by r.result_distance LIMIT 1",
                },
            )

        row = 4
        header_row = (
            '#', 'UID', 'Numurs', 'Alias', 'Sacensības', 'Distance', 'Uzvārds', 'Vārds', 'Dzimšanas diena', 'Dzimums',
            'Grupa', 'Cena', 'E-pasts', 'Telefons', 'Valsts', 'Komanda', 'Velo', 'Izveidots', 'Rezultāts', 'Pieteicies citām sacensibas')
        for col, value in enumerate(header_row):
            sheet.write(row, col, value)

        row = 5
        for index, item in enumerate(items, start=1):
            row_values = (
                index, item.id, unicode(item.primary_number), item.slug, unicode(item.competition), unicode(item.distance), item.last_name,
                item.first_name, item.birthday.strftime("%Y-%m-%d"), item.gender, item.group, unicode(item.price),
                item.email, item.phone_number, unicode(item.country), item.team_name, unicode(item.bike_brand) if item.bike_brand else '',
                item.registration_dt.astimezone(riga_tz).strftime("%Y-%m-%d %H:%M"))

            if competition.tree_id == 1 or competition.tree_id == 2:
                if hasattr(item, 'last_result_distance') and getattr(item, 'last_result_distance', None):
                    row_values += (item.last_result_distance, )
                else:
                    row_values += ('', )

                if hasattr(item, 'comp_count'):
                    row_values += (item.comp_count, )
            elif competition.id == 35:
                if hasattr(item, 'last_result_distance') and getattr(item, 'last_result_distance', None):
                    row_values += (item.last_result_distance, )
                else:
                    row_values += ('', )

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
    output = StringIO.StringIO()
    distances = competition.get_distances().filter(can_have_teams=True)

    notpayed_pattern = xlwt.Pattern()
    notpayed_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    notpayed_pattern.pattern_fore_colour = 2

    not_payed_style = xlwt.XFStyle()
    not_payed_style.pattern = notpayed_pattern

    payed_style = xlwt.XFStyle()

    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(distance.__unicode__())

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
            for member in competition.memberapplication_set.filter(member__team=team).order_by('kind').select_related('member', 'participant', 'participant_unpaid', 'participant_potential', 'participant__primary_number', 'participant__bike_brand'):
                is_payed = True if member.participant_id else False
                sheet.write(row, 0, unicode(team.id), payed_style if is_payed else not_payed_style)
                sheet.write(row, 1, unicode(team), payed_style if is_payed else not_payed_style)
                sheet.write(row, 2, unicode(member.member.first_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 3, unicode(member.member.last_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 4, unicode(member.member.birthday.year), payed_style if is_payed else not_payed_style)
                sheet.write(row, 5, unicode(member.get_kind_display()), payed_style if is_payed else not_payed_style)
                sheet.write(row, 6, unicode(member.participant.slug) if member.participant else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 7, unicode(member.participant.bike_brand) if member.participant and member.participant.bike_brand else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 8, unicode(member.participant_unpaid.slug) if member.participant_unpaid else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 9, unicode(member.participant_potential.slug) if member.participant_potential else '', payed_style if is_payed else not_payed_style)
                number = Number.objects.filter(participant_slug=member.member.slug, competition_id__in=competition.get_ids(), distance=team.distance).order_by('-number')
                if number:
                    sheet.write(row, 10, unicode(number[0]), payed_style if is_payed else not_payed_style)
                    if number.count()>1:
                        sheet.write(row, 11, unicode(','.join([str(obj.number) for obj in number[1:]])), payed_style if is_payed else not_payed_style)
                row += 1

    wbk.save(output)
    return output



def create_team_list(competition=None, competition_id=None):
    if not competition and not competition_id:
        raise Exception('Expected at least one variable')
    if not competition:
        competition = Competition.objects.get(id=competition_id)

    distances = competition.get_distances().filter(can_have_teams=True)

    output = StringIO.StringIO()

    notpayed_pattern = xlwt.Pattern()
    notpayed_pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    notpayed_pattern.pattern_fore_colour = 0x16

    not_payed_style = xlwt.XFStyle()
    not_payed_style.pattern = notpayed_pattern

    payed_style = xlwt.XFStyle()



    wbk = xlwt.Workbook()

    for distance in distances:
        sheet = wbk.add_sheet(slugify(distance.__unicode__()))

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
        for index, team in enumerate(distance.team_set.filter(member__memberapplication__competition=competition).distinct(), start=1):
            col_add = 0 if index % 2 == 1 else 6
            sheet.write(row, 0 + col_add, str(index))
            sheet.write(row, 1 + col_add, unicode(team))
            row += 1
            next_line = row
            for member in competition.memberapplication_set.filter(member__team=team).order_by('kind'):
                is_payed = True if member.participant_id else False



                sheet.write(row, 1 + col_add, unicode(member.get_kind_display())[0], payed_style if is_payed else not_payed_style)
                sheet.write(row, 2 + col_add, unicode(member.participant.primary_number) if member.participant else '', payed_style if is_payed else not_payed_style)
                sheet.write(row, 3 + col_add, unicode(member.member.full_name), payed_style if is_payed else not_payed_style)
                sheet.write(row, 4 + col_add, unicode(member.member.birthday.year), payed_style if is_payed else not_payed_style)


                row += 1
            if index % 2 == 0:
                row = next_line + 12
            else:
                row = next_line - 1

    wbk.save(output)
    return output