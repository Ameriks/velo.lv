# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, activate

import json
import datetime
from urllib.parse import quote

from velo.core.models import Insurance, Log
from velo.payment.models import Payment
from velo.registration.models import Application
from velo.velo.utils import SessionWHeaders
from velo.registration.tasks import send_success_email


def get_price(competition, distance_id, year):
    now = timezone.now()
    prices = competition.price_set.filter(start_registering__lt=now, end_registering__gte=now, till_year__gte=year,
                                          from_year__lte=year, distance_id=distance_id).order_by('price')
    if prices:
        return prices[0]
    return None


def get_participant_fee(competition, distance_id, year):
    parent_competition = None
    if competition.complex_payment_enddate and competition.complex_payment_enddate > timezone.now():
        parent_competition = competition
        child_count = competition.get_children().count()
        competition = competition.get_children()[0]

    price_obj = get_price(competition, distance_id, year)
    if not price_obj:
        return None
    if parent_competition:  # Means that complex.
        entry_fee = round(
            float(price_obj.price) * child_count * ((100.0 - parent_competition.complex_discount) / 100.0), 2)
    else:
        entry_fee = float(price_obj.price)

    return {
        'price_obj': price_obj,
        'entry_fee': entry_fee,
    }


def get_participant_fee_from_price(competition, price_obj):
    parent_competition = None
    if competition.complex_payment_enddate and competition.complex_payment_enddate > timezone.now():
        parent_competition = competition
        child_count = competition.get_children().count()
        competition = competition.get_children()[0]

    if not price_obj:
        return None
    if parent_competition:  # Means that complex.
        entry_fee = round(
            float(price_obj.price) * child_count * ((100.0 - parent_competition.complex_discount) / 100.0), 2)
    else:
        entry_fee = float(price_obj.price)

    return entry_fee


def get_insurance_fee(competition, insurance_id):
    if not insurance_id:
        return None
    try:
        insurance = competition.get_insurances().get(id=insurance_id)
        if competition.complex_payment_enddate and competition.complex_payment_enddate > timezone.now():
            child_count = competition.get_children().count()
            insurance_fee = round(float(insurance.price) * child_count * ((100.0 - insurance.complex_discount) / 100.0),
                                  2)
        else:
            insurance_fee = float(insurance.price)
    except Insurance.DoesNotExist:
        return None

    return {
        'insurance_obj': insurance,
        'insurance_fee': insurance_fee,
    }


def get_insurance_fee_from_insurance(competition, insurance):
    if not insurance:
        return 0.0
    try:
        if competition.complex_payment_enddate and competition.complex_payment_enddate > timezone.now():
            child_count = competition.get_children().count()
            insurance_fee = round(float(insurance.price) * child_count * ((100.0 - insurance.complex_discount) / 100.0),
                                  2)
        else:
            insurance_fee = float(insurance.price)
    except Insurance.DoesNotExist:
        return 0.0

    return insurance_fee


def get_total(competition, distance_id, year, insurance_id=None):
    participant_fee = get_participant_fee(competition, distance_id, year)
    if not participant_fee:
        return None
    if insurance_id:
        insurance_fee = get_insurance_fee(competition, insurance_id)
        ret = dict(participant_fee)
        ret.update(insurance_fee)
        ret.update({'total': participant_fee.get('entry_fee') + insurance_fee.get('insurance_fee')})
        return ret
    else:
        participant_fee.update({'total': participant_fee.get('entry_fee')})
        return participant_fee


def get_form_message(competition, distance_id, year, insurance_id=None):
    totals = get_total(competition, distance_id, year, insurance_id)
    if totals:
        messages = [_("<div class='fs12 fw700 c-white--70 uppercase text-align--right bottom-margin--10'>Entry fee - <span>%(entry_fee)s€</span></div>") % totals, ]
        if insurance_id:
            messages.append(_("<div class='fs12 fw700 c-white--70 uppercase text-align--right bottom-margin--10'>Insurance fee - <span>%(insurance_fee)s€</span></div>") % totals)
        messages.append(_("<div class='fs14 fw700 c-white uppercase text-align--right'>Total - <span class='c-yellow'>%(total)s€</span></div>") % totals)
    else:
        messages = [_("<div class='fs14 fw700 c-white uppercase text-align--right'>This distance isn't available for birth year %(year)s.</div>") % {'year': year}, ]
    return messages


def create_team_invoice(team, active_payment_type, action="send"):
    bill_series = team.distance.competition.bill_series
    prefix = active_payment_type.payment_channel.erekins_url_prefix

    # Create new requests session with Auth keys and prepended url
    session = SessionWHeaders({'Authorization': 'ApiKey %s' % active_payment_type.payment_channel.erekins_auth_key},
                              url="https://%s.e-rekins.lv" % prefix)

    # Find series resource_uri from e-rekins
    series_obj = session.get("/api/v1/series/?prefix=%s" % bill_series)
    if series_obj.json().get('meta').get('total_count') == 0:
        series_obj = session.post("/api/v1/series/", data=json.dumps({
            'title': bill_series,
            'reset_period': 4,
            'prefix': bill_series,
            'formatting': '- #'
        }))
        series_obj.raise_for_status()
        series_resource_uri = series_obj.headers.get('Location')
    else:
        series_resource_uri = series_obj.json().get('objects')[0].get('resource_uri')

    client_data = {
        'name': team.company_name,
        'name_short': team.company_name,
        'integration_code': "team_%s" % str(team.id),
        'number': team.company_regnr,
        'vat': team.company_vat,
        'email': team.email,
        'office_address': {
            'address': team.company_address,
            'country': '/api/v1/country/124/',  # Always default is Latvia
        },
        'juridical_address': {
            'address': team.company_juridical_address,
            'country': '/api/v1/country/124/',  # Always default is Latvia
        },
        'form': 1,  # Juridical
    }

    # Find or Create customer
    client_obj = session.get("/api/v1/client/?number=%s" % team.company_regnr)
    if client_obj.json().get('meta').get('total_count') == 0:
        client_obj = session.post("/api/v1/client/", data=json.dumps(client_data))
        client_obj.raise_for_status()
        client_obj = session.get(client_obj.headers.get('Location'))
        client_obj.raise_for_status()
        client_resource_uri = client_obj.json().get('resource_uri')
    else:
        client_resource_uri = client_obj.json().get('objects')[0].get('resource_uri')
        client_obj = session.put(client_resource_uri, data=json.dumps(client_data))
        client_obj.raise_for_status()

    items = [{
        "description": "Komandas %s profila apmaksa" % str(team),
        "vat": getattr(settings, "EREKINS_%s_DEFAULT_VAT" % active_payment_type.payment_channel.payment_channel),
        "units": "gab.",
        "amount": "1",
        "price": float(team.final_price)
    }, ]

    due_date = datetime.datetime.now() + datetime.timedelta(days=7)
    invoice_data = {
        "due_date": due_date.strftime('%Y-%m-%d'),
        "client": client_resource_uri,
        "currency": "/api/v1/currency/1/",
        "invoice_creator": getattr(settings,
                                   "EREKINS_%s_DEFAULT_CREATOR" % active_payment_type.payment_channel.payment_channel),
        "series": series_resource_uri,
        "language": getattr(settings,
                            "EREKINS_%s_DEFAULT_LANGUAGE" % active_payment_type.payment_channel.payment_channel),
        "payment_type": "Pārskaitījums",
        "kind": "2",
        "items": items,
        "status": "10",
        "activity": 'Pakalpojumu sniegšana',
        "ad_integration_code": "team_%i" % team.id,
        "action": action,
    }

    # Create invoice
    invoice_obj = session.post("/api/v1/invoice/", data=json.dumps(invoice_data))
    invoice_obj.raise_for_status()
    invoice_obj = session.get(invoice_obj.headers.get('Location'))
    invoice_obj.raise_for_status()
    invoice = invoice_obj.json()
    return invoice.get('code'), invoice.get('invoice_nr')


def create_application_invoice(application, active_payment_type, action="send"):
    bill_series = application.competition.bill_series
    prefix = active_payment_type.payment_channel.erekins_url_prefix

    # Create new requests session with Auth keys and prepended url
    session = SessionWHeaders({'Authorization': 'ApiKey %s' % active_payment_type.payment_channel.erekins_auth_key},
                              url="https://%s.e-rekins.lv" % prefix)

    # Find series resource_uri from e-rekins
    series_obj = session.get("/api/v1/series/?prefix=%s" % bill_series)
    if series_obj.json().get('meta').get('total_count') == 0:
        series_obj = session.post("/api/v1/series/", data=json.dumps({
            'title': bill_series,
            'reset_period': 4,
            'prefix': bill_series,
            'formatting': '- #'
        }))
        series_obj.raise_for_status()
        series_resource_uri = series_obj.headers.get('Location')
    else:
        series_resource_uri = series_obj.json().get('objects')[0].get('resource_uri')

    client_data = {
        'name': application.company_name,
        'name_short': application.company_name,
        'integration_code': str(application.id),
        'number': application.company_regnr,
        'vat': application.company_vat,
        'email': application.email,
        'office_address': {
            'address': application.company_address,
            'country': '/api/v1/country/124/',  # Always default is Latvia
        },
        'juridical_address': {
            'address': application.company_juridical_address,
            'country': '/api/v1/country/124/',  # Always default is Latvia
        },
        'form': 1,  # Juridical
    }

    # Find or Create customer
    client_obj = session.get("/api/v1/client/?number=%s" % application.company_regnr)
    if client_obj.json().get('meta').get('total_count') == 0:
        client_obj = session.post("/api/v1/client/", data=json.dumps(client_data))
        client_obj.raise_for_status()
        client_obj = session.get(client_obj.headers.get('Location'))
        client_obj.raise_for_status()
        client_resource_uri = client_obj.json().get('resource_uri')
    else:
        client_resource_uri = client_obj.json().get('objects')[0].get('resource_uri')
        client_obj = session.put(client_resource_uri, data=json.dumps(client_data))
        client_obj.raise_for_status()

    items = []
    for participant in application.participant_set.all():
        activate(application.language)
        if application.invoice_show_names:
            description = "Dalības maksa %(competition)s - %(distance)s - %(full_name)s (%(year)i)" % {
                "competition": application.competition.get_full_name,
                "distance": str(participant.distance),
                "full_name": participant.full_name,
                "year": participant.birthday.year
            }
        else:
            description = "Dalības maksa %(competition)s " % {
                "competition": application.competition.get_full_name,
            }

        items.append({
            "description": description,
            "vat": getattr(settings, "EREKINS_%s_DEFAULT_VAT" % active_payment_type.payment_channel.payment_channel),
            "units": "gab.",
            "amount": "1",
            "price": get_participant_fee_from_price(participant.competition, participant.price)
        })
        if participant.insurance:
            items.append({
                "description": "&nbsp;-&nbsp;Apdrošināšana %(insurance)s" % {
                    "insurance": participant.insurance,
                },
                "vat": getattr(settings,
                               "EREKINS_%s_DEFAULT_VAT" % active_payment_type.payment_channel.payment_channel),
                "units": "gab.",
                "amount": "1",
                "price": get_insurance_fee_from_insurance(participant.competition, participant.insurance)
            })
    if application.donation > 0:
        information = application.competition.params_dict.get('donation', {}).get('bank_code',
                                                                             'Ziedojums - %s') % application.donation
        items.append({
            "description": information,
            "vat": getattr(settings, "EREKINS_%s_DEFAULT_VAT" % active_payment_type.payment_channel.payment_channel),
            "units": "gab.",
            "amount": "1",
            "price": float(application.donation)
        })
    if not application.competition.complex_payment_enddate:
        competition_date = application.competition.competition_date
    else:
        competition_date = application.competition.get_children()[0].competition_date
    competition_datetime = datetime.datetime.combine(competition_date, datetime.time())
    now = datetime.datetime.now()
    if now + datetime.timedelta(days=7) > competition_datetime:
        due_date = now
    elif now + datetime.timedelta(days=14) > competition_datetime:
        due_date = competition_datetime - datetime.timedelta(days=6)
    else:
        due_date = now + datetime.timedelta(days=7)

    invoice_data = {
        "due_date": due_date.strftime('%Y-%m-%d'),
        "client": client_resource_uri,
        "currency": "/api/v1/currency/1/",
        "invoice_creator": getattr(settings,
                                   "EREKINS_%s_DEFAULT_CREATOR" % active_payment_type.payment_channel.payment_channel),
        "series": series_resource_uri,
        "language": getattr(settings,
                            "EREKINS_%s_DEFAULT_LANGUAGE" % active_payment_type.payment_channel.payment_channel),
        "payment_type": "Pārskaitījums",
        "kind": "2",
        "items": items,
        "status": "10",
        "activity": 'Pakalpojumu sniegšana',
        "ad_integration_code": application.id,
        "comments": "Nesaņemot apmaksu līdz norādītajam termiņam, rēķins zaudē spēku un dalībnieki starta sarakstā neparādās, kā arī netiek pielaisti pie starta.",
        "action": action,
        "invoice_external_edit_url": ("%s%s" % (settings.MY_DEFAULT_DOMAIN, reverse('manager:application_pay', kwargs={
            'pk': application.competition_id, 'pk2': application.id}))).replace('http://', 'https://'),
    }

    # Create invoice
    invoice_obj = session.post("/api/v1/invoice/", data=json.dumps(invoice_data))
    invoice_obj.raise_for_status()
    invoice_obj = session.get(invoice_obj.headers.get('Location'))
    invoice_obj.raise_for_status()
    invoice = invoice_obj.json()
    return invoice.get('code'), invoice.get('invoice_nr')


def create_team_bank_transaction(team, active_payment_type):
    prefix = active_payment_type.payment_channel.erekins_url_prefix

    # Create new requests session with Auth keys and prepended url
    session = SessionWHeaders({'Authorization': 'ApiKey %s' % active_payment_type.payment_channel.erekins_auth_key},
                              url="https://%s.e-rekins.lv" % prefix)

    information = "Komandas %s profila apmaksa %s" % (str(team),
                                                      team.distance.competition.get_full_name) if not team.external_invoice_code else "Rekins nr.%s" % team.external_invoice_nr

    bank_data = {
        "information": information,
        "integration_id": team.id,
        "amount": float(team.final_price),
        "link": active_payment_type.payment_channel.erekins_link,
    }

    transaction_obj = session.post("/api/v1/transaction/", data=json.dumps(bank_data))
    transaction_obj.raise_for_status()
    transaction = transaction_obj.json()

    Payment.objects.create(content_object=team,
                           channel=active_payment_type,
                           erekins_code=transaction.get('code'),
                           total=team.final_price,
                           status=Payment.STATUSES.pending, )

    return "https://%s.e-rekins.lv/bank/%s/" % (prefix, transaction.get('code'))


def create_application_bank_transaction(application, active_payment_type):
    prefix = active_payment_type.payment_channel.erekins_url_prefix

    # Create new requests session with Auth keys and prepended url
    session = SessionWHeaders({'Authorization': 'ApiKey %s' % active_payment_type.payment_channel.erekins_auth_key},
                              url="https://%s.e-rekins.lv" % prefix)

    information = "Pieteikums nr.%i" % application.id if not application.external_invoice_code else "Rekins nr.%s" % application.external_invoice_nr
    if application.donation > 0:
        information += (" + %s" % application.competition.params_dict.get('donation', {}).get('bank_code',
                                                                                         'Ziedojums - %s')) % application.donation

    bank_data = {
        "information": information,
        "integration_id": application.id,
        "amount": float(application.final_price),
        "link": active_payment_type.payment_channel.erekins_link,
    }

    transaction_obj = session.post("/api/v1/transaction/", data=json.dumps(bank_data))
    transaction_obj.raise_for_status()
    transaction = transaction_obj.json()

    Payment.objects.create(content_object=application,
                           channel=active_payment_type,
                           erekins_code=transaction.get('code'),
                           total=application.final_price,
                           status=Payment.STATUSES.pending,
                           donation=application.donation)

    return "https://%s.e-rekins.lv/bank/%s/" % (prefix, transaction.get('code'))


def approve_payment(payment, user=False, request=None):
    if payment.content_type.model == 'application':
        application = payment.content_object
        application.payment_status = Application.PAY_STATUS.payed
        application.save()
        for participant in application.participant_set.all():
            participant.is_participating = True
            participant.save()
            if participant.company_participant_id:
                participant.company_participant.is_participating = True
                participant.company_participant.save()

        send_success_email.delay(application.id)

        if user:
            return HttpResponseRedirect(reverse('application_ok', kwargs={'slug': payment.content_object.code}))
        else:
            return True

    elif payment.content_type.model == 'team':
        team = payment.content_object
        team.is_featured = True
        team.save()

        if user:
            messages.success(request, _('Team profile successfully paid.'))
            return HttpResponseRedirect(reverse('account:team', kwargs={'pk2': payment.content_object.id}))
        else:
            return True


def validate_payment(payment, user=False, request=None):
    prefix = payment.channel.payment_channel.erekins_url_prefix
    # Create new requests session with Auth keys and prepended url
    session = SessionWHeaders({'Authorization': 'ApiKey %s' % payment.channel.payment_channel.erekins_auth_key},
                              url="https://%s.e-rekins.lv" % prefix)

    transaction_obj = session.get('/api/v1/transaction/?code=%s' % quote(payment.erekins_code))

    transactions = transaction_obj.json()
    if transactions.get('meta').get('total_count') == 0:
        if payment.status != payment.STATUSES.ok:
            payment.status = payment.STATUSES.id_not_found
            payment.save()
            Log.objects.create(content_object=payment, action="TRANSACTION_VALIDATE",
                               message="Not found transaction id in e-rekins.lv", params={'code': payment.erekins_code})
        if user:
            raise Http404
        else:
            return False

    transaction = transactions.get('objects')[0]
    status = transaction.get('status')

    payment.status = status
    payment.save()

    if status == 30:
        # Transaction is successful.
        return approve_payment(payment, user, request)
    elif status < 0:

        other_active_payments = Payment.objects.filter(content_type=payment.content_type, object_id=payment.object_id,
                                                       status__gte=0).exclude(id=payment.id)
        if payment.content_type.model == 'application':
            application = payment.content_object
            # If there are no other active payments and user haven't taken invoice, then lets reset application payment status.
            if not other_active_payments and not application.external_invoice_code:
                application.payment_status = application.PAY_STATUS.not_payed
                application.save()

        Log.objects.create(content_object=payment, action="TRANSACTION_VALIDATE",
                           message="Transaction unsuccessful. Redirecting to payment view.", params={'user': user})

        if user:
            messages.error(request, _('Transaction unsuccessful. Try again.'))
            if payment.content_type.model == 'application':
                return HttpResponseRedirect(reverse('application_pay', kwargs={'slug': payment.content_object.code}))
            elif payment.content_type.model == 'team':
                return HttpResponseRedirect(reverse('account:team_pay', kwargs={'pk2': payment.content_object.id}))
        else:
            return False
    else:
        Log.objects.create(content_object=payment, action="TRANSACTION_VALIDATE",
                           message="UNKNOWN STATUS. This must be fixed.", params={'user': user})

        if user:
            messages.info(request, _(
                'Transaction status unknown. If you paid, then wait a while until status is updated - you will receive email.'))
            if payment.content_type.model == 'application':
                return HttpResponseRedirect(reverse('application_pay', kwargs={'slug': payment.content_object.code}))
            elif payment.content_type.model == 'team':
                return HttpResponseRedirect(reverse('account:team_pay', kwargs={'pk2': payment.content_object.id}))
        else:
            return False
