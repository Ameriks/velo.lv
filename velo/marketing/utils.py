from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import requests
import unicodedata
from urllib.parse import urlencode
import uuid

from django.utils.translation import activate
from requests import RequestException

from velo.core.models import Competition
from velo.marketing.models import SMS
from velo.registration.models import Participant, Application
from premailer import transform
import logging

logger = logging.getLogger('marketing')


# TODO: Rebuild this all

def send_number_email(competition, participants=None, application=None):
    activate('lv')
    if application:
        email = application.email
        participants = application.participant_set.filter(is_participating=True)
    else:
        email = participants[0].email

    if not participants:
        return False
    if not email:
        return False

    context = {
        'participants': participants,
        'domain': settings.MY_DEFAULT_DOMAIN,
        'competition': competition,
        'application': True,
    }
    template = transform(render_to_string('registration/email/%s/number_email.html' % competition.skin, context))
    template_txt = render_to_string('registration/email/%s/number_email.txt' % competition.skin, context)

    activate('lv')
    if len(participants) == 1:
        subject = u'Reģistrācijas apliecinājums - %s - %s' % (competition.get_full_name, participants[0].full_name)
    else:
        subject = u'Reģistrācijas apliecinājums - %s' % competition.get_full_name

    email_data = {
        'subject': subject,
        'message': template_txt,
        'from_email': settings.SERVER_EMAIL,
        'recipient_list': [email, ],
        'html_message': template,
    }
    send_mail(**email_data)

    return True

def send_sms_to_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print('Not sending to %s' % number)
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print('TOO SHORT NUMBER')
        return False

    print('Sending to %s' % number)

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')

#    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=u"{0}, Jusu starta numurs ir {1} Vienibas brauciena. Iznemiet to EXPO centra 31.08.-1.09. Domina Shopping, Ieriku 3, uzradot so SMS".format(full_name, str(participant.primary_number)))
    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=u"{0}, Jusu starta numurs ir {1} Toyota Rigas velomaratona. Iznemiet to EXPO centra 31.05.-1.06. Riga Plaza 10.00–20.00, uzradot so SMS ".format(full_name, str(participant.primary_number)))

    Participant.objects.filter(id=participant.id).update(is_sent_number_sms=True)

    return True

def send_sms_to_family_participant(participant):
    send_out = timezone.now()
    number = participant.phone_number.strip().replace('+371', '').replace(' ', '').replace('00371', '').replace('+', '')
    if len(number) == 0:
        return False
    if number[0:3] == '371':
        number = number[3:]
    if len(number) == 8 and number[0] != '2':
        print('Not sending to %s' % number)
        return False
    elif len(number) == 8:
        number = '371%s' % number

    if len(number) < 8:
        print('TOO SHORT NUMBER')
        return False

    print('Sending to %s' % number)

    full_name = unicodedata.normalize('NFKD', participant.full_name).encode('ascii', 'ignore').decode('ascii')
    sms_txt = u"Sveiki, {0}! Jums ir pieskirts starta numurs Gimenes brauciena. Iznemiet to EXPO centra 2.-3.06 Doma laukuma, uzradot so SMS".format(full_name)[:160]
    sms = SMS.objects.create(send_out_at=send_out, phone_number=number, text=sms_txt)

    Participant.objects.filter(id=participant.id).update(is_sent_number_sms=True)



def initial_send_numbers_to_all_participants():
    # TODO: Filter. If participant is only one in application, then send only one email.
    competition = Competition.objects.get(id=97)
    print(competition)
    applications = Application.objects.filter(competition_id=97).filter(participant__is_participating=True).order_by('id')
    applications = applications.distinct()

    for application in applications:
        print(application.id)
        send_number_email(competition, application=application)
        application.participant_set.all().update(is_sent_number_email=True)

    participants = Participant.objects.filter(competition_id=97, is_participating=True, is_sent_number_email=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        print(participant.id)
        if participant.application:
            if participant.application.participant_set.filter(is_participating=True).count() == 1:
                continue
            if participant.email == participant.application.email:
                continue

        if participant.email:
            send_number_email(competition, [participant, ])
            participant.is_sent_number_email = True
            participant.save()


def send_numbers_to_all_participants_sms():
    participants = Participant.objects.filter(competition_id=97, is_participating=True, is_sent_number_sms=False).exclude(primary_number=None).order_by('primary_number__number')
    for participant in participants:
        send_sms_to_participant(participant)

    # participants = Participant.objects.filter(competition_id=61, is_participating=True, is_sent_number_sms=False, distance_id=56).order_by('created')
    # for participant in participants:
    #     send_sms_to_family_participant(participant)


def send_sms_text2reach(number, msg):
    text2reach_api_key = getattr(settings, 'TEXT2REACH_BULK_API_KEY')

    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')

    # Remove + from number as Text2Reach phone number can not start with +
    if str(number).startswith('+'):
        number = number[1:]

    if len(str(number)) == 8:
        number = "371%s" % number

    if settings.ENVIRONMENT_NAME in ('INT', 'DEV'):
        msg = number + ': ' + msg
        number = settings.TEXT2REACH_DEV_NUMBER

    url_params = {
        "api_key": text2reach_api_key,
        "phone": number,
        "from": "velo.lv",
        "message": msg,
        "unicode": 'false',

    }
    sms_url = 'https://api.text2reach.com/sms/send?%s' % urlencode(url_params)

    if settings.DEBUG:
        logger.info('Sent SMS %s to %s' % (msg, number))
        return '0001'

    try:
        r = requests.get(sms_url)
    except RequestException as e:
        # Log error
        logger.error('Error sending SMS to {0} using Text2Reach with error msg {1}'.format(
            number, str(e)
        ))
        return ''

    # If the message cannot be sent, the return value for msg_id
    # will contain a negative integer. Response code is also 200 in case of error
    if r.status_code != 200 or not r.text.isnumeric() or int(r.text) < 0:
        # Log error
        logger.error('Error sending SMS to {0} using Text2Reach with error code {1}'.format(
            number, r.text
        ))
        return ''
    return r.content


def send_smses():
    smses = SMS.objects.filter(is_processed=False)[:100]
    for sms in smses:
        sms.response = send_sms_text2reach(sms.phone_number, sms.text)
        sms.is_processed = True
        sms.save()
