import logging
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _, activate

import datetime

from premailer import transform

from velo.core.models import Insurance, Log
from velo.core.utils import get_client_ip
from velo.payment.models import Payment, Invoice, Transaction
from velo.payment.pdf import InvoiceGenerator
from velo.registration.models import Application

from velo.registration.tasks import send_success_email

logger = logging.getLogger('velo.payment')


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


def generate_pdf_invoice(instance, invoice_data, active_payment_type):
    content_type = ContentType.objects.get_for_model(instance)

    payment, created = Payment.objects.get_or_create(
        content_type=content_type,
        object_id=instance.id,
        total=instance.final_price,
        donation=instance.donation if hasattr(instance, "donation") else 0.0,
        defaults={"status": Payment.STATUSES.pending}
    )
    if not created and payment.status != Payment.STATUSES.ok:
        payment.status = Payment.STATUSES.new
        payment.save()

    invoice_object = Invoice(
        competition=instance.competition,
        company_name=instance.company_name,
        company_vat=instance.company_vat,
        company_regnr=instance.company_regnr,
        company_address=instance.company_address,
        company_juridical_address=instance.company_juridical_address,
        email=instance.email,
        series=invoice_data.get('bill_series'),
        channel=active_payment_type.payment_channel,
        payment=payment,
    )
    invoice_object.set_number()

    invoice_data.update({'name': invoice_object.invoice_nr})
    invoice = InvoiceGenerator(invoice_data)
    invoice_pdf = invoice.build()
    invoice_object.file = ContentFile(invoice_pdf.read(), str("%s-%03d.pdf" % (invoice_object.series, invoice_object.number)))
    invoice_object.save()

    instance.invoice = invoice_object
    instance.save(update_fields=['invoice'])

    total_price = 0
    for item in invoice_data.get('items'):
        total_price += item.get('price')
    invoice_data.update({'total_price': total_price})

    if instance.competition.level == 2:
        primary_competition = instance.competition.parent
    else:
        primary_competition = instance.competition

    context = {
        'application': instance,
        'competitions': instance.competition,
        'competition': primary_competition,
        'domain': settings.MY_DEFAULT_DOMAIN,
        'invoice': invoice_data,
        'url': "{0}/payment/invoice/{1}/".format(settings.MY_DEFAULT_DOMAIN, invoice_object.slug)
    }

    try:
        language = instance.language
    except:
        language = 'lv'
    activate(language)
    template = transform(render_to_string('payment/email/invoice_email_lv.html', context))
    template_txt = render_to_string('payment/email/invoice_email_lv.txt', context)

    email_data = {
        'subject': _('VELO.LV application #%i') % instance.id,
        'message': template_txt,
        'from_email': settings.SERVER_EMAIL,
        'recipient_list': [instance.email, ],
        'html_message': template,
    }

    send_mail(**email_data)

    return invoice_object

def create_team_invoice(team, active_payment_type, action="send"):
    due_date = datetime.datetime.now() + datetime.timedelta(days=7)
    invoice_data = {
        "bill_series": team.distance.competition.bill_series,
        "client_data": {
            'name': team.company_name,
            'number': team.company_regnr,
            'vat': team.company_vat,
            'office_address': team.company_address,
            'country': 'Latvia',
            'juridical_address': team.company_juridical_address,
            'name_short': team.company_name,
            'integration_code': "team_%s" % str(team.id),
            'form': 1,  # Juridical
        },
        "organiser_data": {
            "name": active_payment_type.payment_channel.params.get("name"),
            "juridical_address": active_payment_type.payment_channel.params.get("juridical_address"),
            "number": active_payment_type.payment_channel.params.get("number"),
            "vat": active_payment_type.payment_channel.params.get("vat"),
            "account_name": active_payment_type.payment_channel.params.get("account_name"),
            "account_code": active_payment_type.payment_channel.params.get("account_code"),
            "account_number": active_payment_type.payment_channel.params.get("account_number")
        },
        "invoice_date": datetime.datetime.now(),
        "due_date": due_date,
        "currency": "EUR",
        "language": "LV",
        "payment_type": "Pārskaitījums",
        "kind": "2",
        "items": [{
            "description": "Komandas %s profila apmaksa" % str(team),
            "units": "gab.",
            "amount": "1",
            "price": float(team.final_price)
        }],
        "status": "10",
        "activity": 'Pakalpojumu sniegšana',
        "ad_integration_code": "team_%i" % team.id,
        'email': team.email,
        "comments": "Nesaņemot apmaksu līdz norādītajam termiņam, rēķins zaudē spēku un dalībnieki starta sarakstā neparādās, kā arī netiek pielaisti pie starta.",
        "action": action
    }
    invoice_pdf = generate_pdf_invoice(team, invoice_data, active_payment_type)

    return invoice_pdf


def create_application_invoice(application, active_payment_type, action="send"):
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
                "vat": getattr(settings, "EREKINS_%s_DEFAULT_VAT" % active_payment_type.payment_channel.payment_channel),
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
        "bill_series": application.competition.bill_series,
        "client_data": {
            'name': application.company_name,
            'number': application.company_regnr,
            'vat': application.company_vat,
            'office_address': application.company_address,
            'country': 'Latvia',
            'juridical_address': application.company_juridical_address,
        },
        "organiser_data": {
            "name": active_payment_type.payment_channel.params.get("name"),
            "juridical_address": active_payment_type.payment_channel.params.get("juridical_address"),
            "number": active_payment_type.payment_channel.params.get("number"),
            "vat": active_payment_type.payment_channel.params.get("vat"),
            "account_name": active_payment_type.payment_channel.params.get("account_name"),
            "account_code": active_payment_type.payment_channel.params.get("account_code"),
            "account_number": active_payment_type.payment_channel.params.get("account_number")
        },
        "invoice_date": now,
        "due_date": due_date,
        "currency": "EUR",
        "language": "LV",
        "payment_channel": active_payment_type.payment_channel.payment_channel,
        "payment_type": "Pārskaitījums",
        "kind": "2",
        "items": items,
        "status": "10",
        "activity": 'Pakalpojumu sniegšana',
        "ad_integration_code": application.id,
        'email': application.email,
        "comments": "Nesaņemot apmaksu līdz norādītajam termiņam, rēķins zaudē spēku un dalībnieki starta sarakstā neparādās, kā arī netiek pielaisti pie starta.",
        "action": action
    }
    invoice_object = generate_pdf_invoice(application, invoice_data, active_payment_type)

    return invoice_object


def create_bank_transaction(instance, active_payment_type, request):
    instance_name = instance.__class__.__name__
    if instance_name == 'Application':
        information = "Pieteikums nr.%i" % instance.id if not instance.invoice else "Rekins nr.%s" % instance.invoice.invoice_nr
        if instance.donation > 0:
            information += (" + %s" % instance.competition.params_dict.get("donation", {}).get("bank_code", "Ziedojums - %s")) % instance.donation
    elif instance_name == 'Team':
        information = "Komandas %s profila apmaksa %s" % (str(instance), instance.distance.competition.get_full_name) \
            if not instance.invoice else "Rekins nr.%s" % instance.invoice.invoice_nr
    else:
        raise Exception()

    # For testing purposes. To test successful SEB and Swedbank transactions.
    if request.user.is_authenticated() and request.user.id == 6:
        instance.final_price = 0.01

    content_type = ContentType.objects.get_for_model(instance)
    payment, created = Payment.objects.get_or_create(
                content_type=content_type,
                object_id=instance.id,
                total=instance.final_price,
                donation=instance.donation if hasattr(instance, "donation") else 0.0,
                defaults={"status": Payment.STATUSES.pending}
            )

    if not created:
        if payment.status == Payment.STATUSES.ok:
            raise Exception("Already payed")
        payment.status = Payment.STATUSES.pending
        payment.save()

    transaction = Transaction.objects.create(
        channel=active_payment_type.payment_channel,
        payment=payment,
        language=request.LANGUAGE_CODE,
        status=Transaction.STATUSES.new,
        amount=instance.final_price,
        created_ip=get_client_ip(request),
        information=information,
    )

    return reverse('payment:transaction', kwargs=({'slug': transaction.code}))


def approve_payment(payment, user=False, request=None):
    payment.status = Payment.STATUSES.ok
    payment.save(update_fields=['status'])

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
