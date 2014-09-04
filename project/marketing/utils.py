# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
import datetime
from django.conf import settings
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import timezone
import requests
import unicodedata
import urllib
from legacy.models import Ev68RVeloParticipations
from marketing.models import SMS, MailgunEmail
from payment.models import DiscountCode
from registration.models import Participant, Application
from results.models import LegacyResult
from premailer import transform


# TODO: Create view, where it is possible to filter participants and send information. This is tmp solution.
def send_email_to_all_seb():
    applications = Application.objects.filter(payment_status=20, competition_id__in=[25, 26, 27, 28, 29, 30, 31, 32]).exclude(email='').exclude(email=' ')
    emails = set()
    for application in applications:
        emails.add(application.email.strip())

    participants = Participant.objects.filter(competition_id__in=[25,26,27,28,29,30,31,32], is_participating=True).exclude(email='').exclude(email=' ')
    for participant in participants:
        emails.add(participant.email.strip())

    template = transform(render_to_string('marketing/email/info_email.html', {}))
    template_txt = render_to_string('marketing/email/info_email.txt', {})


    for email in emails:
        email_data = {
            'em_to': email,
            'subject': u'SEB MTB maratona Cēsu posmam mainīti starta laiki',
            'html': template,
            'text': template_txt,
        }
        mailgun = MailgunEmail.objects.create(**email_data)


def legacy_prepare_all_seb():
    participants = Participant.objects.filter(competition_id__in=[25,26,27,28,29,30,31,32], is_participating=True).exclude(phone_number='').exclude(phone_number=' ')

    sms_txt = "Sveiki! Sakara ar silto laiku,nolemts mainit startalaikus 10.08 Cesu SEB MTB maratonam! Sporta brauciens-11:00. Tauta-12:00. Berniem-12:15. http://ej.uz/cesis6"

    send_out = timezone.now().replace(hour=9, minute=0) + datetime.timedelta(days=1)

    numbers = set()
    for participant in participants:
        numbers.add(participant.phone_number)

    for number in numbers:
        number = number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
        if len(number) == 0:
            continue
        if number[0:3] == '371':
            number = number[3:]
        if len(number) == 8 and number[0] != '2':
            print 'Not sending to %s' % number
            continue
        elif len(number) == 8:
            number = '371%s' % number

        if len(number) < 8:
            print 'TOO SHORT NUMBER'
            continue

        print 'Sending to %s' % number
        sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=sms_txt, )





def send_number_email(participant):
    context = {
        'object': participant,
        'number': participant.primary_number,
        'domain': settings.MY_DEFAULT_DOMAIN,
    }

    template = transform(render_to_string('marketing/email/number_email_vb.html', context))
    template_txt = render_to_string('marketing/email/number_email_vb.txt', context)

    email = participant.email
    if not email and participant.application:
        participants = Participant.objects.filter(application=participant.application).exclude(email='')
        if participants:
            email = participants[0].email

    if not email and participant.registrant:
        email = participant.registrant.email

    if not email:
        print 'PARTICIPANT %i doesnt have email' % participant.id
        return False

    email_data = {
        'em_to': email,
        'subject': u'Reģistrācijas apliecinājums - Rīgas velomaratons 2014',
        'html': template,
        'text': template_txt,
        'content_object': participant,
    }
    mailgun = MailgunEmail.objects.create(**email_data)

    participant.is_sent_number_email = True
    participant.save()

    return mailgun

def send_numbers_to_all_participants():
    participants = Participant.objects.filter(competition_id=34, is_participating=True, is_sent_number_email=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        send_number_email(participant)

    participants = Participant.objects.filter(competition_id=34, distance_id=30, is_participating=True, is_sent_number_email=False).order_by('created')
    for participant in participants:
        send_number_email(participant)




def send_sms_to_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print 'Not sending to %s' % number
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print 'TOO SHORT NUMBER'
        return False

    print 'Sending to %s' % number

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')
    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=u"{0}, Jusu numurs Vienibas brauciena ir {1}. Iznemiet numuru 5.-6.09 Riga vai 7.09 Sigulda, uzradot so SMS! Jusu, velo.lv".format(full_name, participant.primary_number.number))

    participant.is_sent_number_sms = True
    participant.save()

    return True


def send_sms_to_family_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print 'Not sending to %s' % number
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print 'TOO SHORT NUMBER'
        return False

    print 'Sending to %s' % number

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')

    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=u"Sveiki, {0}! Jums ir pieskirts starta numurs Spice Gimenu braucienam! Iznemiet numuru registracijas telti 1.junija,uzradot so sms.".format(full_name))

    participant.is_sent_number_sms = True
    participant.save()

    return True


def send_numbers_to_all_participants_sms():
    participants = Participant.objects.filter(competition_id=34, is_participating=True, is_sent_number_sms=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        send_sms_to_participant(participant)

    participants = Participant.objects.filter(competition_id=34, is_participating=True, is_sent_number_sms=False, distance_id=30).order_by('created')
    for participant in participants:
        send_sms_to_family_participant(participant)


def legacy_prepare():
    results = LegacyResult.objects.exclude(phone_number='').filter(participant_2014=None).values('phone_number').annotate(n=Count('phone_number'))

    send_out = timezone.now().replace(hour=5, minute=0) + datetime.timedelta(days=1)


    for result in results:
        code = DiscountCode.objects.order_by('id').filter(sms=None)[0]
        number = result.get('phone_number').strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
        if len(number) == 0:
            continue
        if number[0:3] == '371':
            number = number[3:]
        if len(number) == 8 and number[0] != '2':
            print 'Not sending to %s' % number
            continue
        elif len(number) == 8:
            number = '371%s' % number

        if len(number) < 8:
            print 'TOO SHORT NUMBER'
            continue

        print 'Sending to %s' % number
        sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text="Pedeja diena, lai pieteiktos Rigas Velomaratonam un saglabatu savu koridoru! Tikai Tev 10% atlaide - {0}. Riga ir musu! Vairak info: http://ej.uz/velo10".format(code.code), discount_code=code)


def legacy4_prepare():
    slugs = [p.slug for p in Participant.objects.filter(competition_id=34)]
    pp = Ev68RVeloParticipations.objects.exclude(alias__in=slugs).exclude(participant_phone_number='').values('participant_phone_number').annotate(n=Count('participant_phone_number'))

    numbers = []
    send_out = timezone.now()

    for p in pp:
        code = DiscountCode.objects.order_by('id').filter(sms=None, campaign_id=2)[0]
        number = p.get('participant_phone_number', '').strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
        if len(number) == 0:
            continue
        if number[0:3] == '371':
            number = number[3:]
        if len(number) == 8 and number[0] != '2':
            print 'Not sending to %s' % number
            continue
        elif len(number) == 8:
            number = '371%s' % number

        if len(number) < 8:
            print 'TOO SHORT NUMBER'
            continue

        if len(number) != 11 or number[0:3] != '371':
            print 'NON LV NUMBER'
            continue

        last_check = SMS.objects.filter(phone_number=number)
        if not last_check:
            numbers.append(number)
            sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text="Rigas Velomaratons jau so svetdien! Tikai Tev pieskiram 20% atlaidi - {0}. Riga ir musu! Vairak info: http://ej.uz/velo20".format(code.code), discount_code=code)

    print 'Kopejais skaits: %i' % len(numbers)

    return numbers




def send_test():
    sms = SMS.objects.filter(is_processed=False)[0]

    sms_obj = {
        'page': 'message/send',
        'username': settings.SMS_USERNAME,
        'password': settings.SMS_PASSWORD,
        'destinationAddress': '37126461101',
        'text': sms.text,
    }
    resp = requests.get('%s/?%s' % (settings.SMS_GATEWAY, urllib.urlencode(sms_obj)))
    sms.response = resp.content
    sms.is_processed = True
    sms.save()

def send_smses():
    smses = SMS.objects.filter(is_processed=False)[:1000]
    for sms in smses:
        # text = unicodedata.normalize('NFKD', sms.text).encode('ascii', 'ignore').decode('ascii')
        # print text
        sms_obj = {
            'page': 'message/send',
            'username': settings.SMS_USERNAME,
            'password': settings.SMS_PASSWORD,
            'destinationAddress': sms.phone_number,
            'text': sms.text,
        }
        resp = requests.get('%s/?%s' % (settings.SMS_GATEWAY, urllib.urlencode(sms_obj)))
        sms.response = resp.content
        sms.is_processed = True
        sms.save()
