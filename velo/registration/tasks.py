# -*- coding: utf-8 -*-
import datetime
import hashlib
import hmac
import base64

from celery.schedules import crontab
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils import timezone

from celery.task import periodic_task, task
from django.utils.translation import activate, ugettext_lazy as _
from premailer import transform

from velo.registration.models import Application, Participant


@task()
def send_success_email(application_id):
    application = Application.objects.select_related('competition',).get(id=application_id)

    competition = application.competition

    if competition.get_children():
        competitions = competition.get_children()
    else:
        competitions = (competition, )

    if competition.level == 2:
        primary_competition = competition.parent
    else:
        primary_competition = competition


    context = {
        'domain': settings.MY_DEFAULT_DOMAIN,
        'application': application,
        'competitions': competitions,
        'competition': primary_competition,
        'url': "{0}{1}".format(settings.MY_DEFAULT_DOMAIN, reverse('application', kwargs={'slug': application.code}))
    }

    activate(application.language)
    template = transform(render_to_string('registration/email/success_email_%s.html' % application.language, context))
    template_txt = render_to_string('registration/email/success_email_%s.txt' % application.language, context)

    email_data = {
        'subject': _('VELO.LV application #%i') % application_id,
        'message': template_txt,
        'from_email': settings.SERVER_EMAIL,
        'recipient_list': [application.email, ],
        'html_message': template,
    }
    send_mail(**email_data)


@periodic_task(run_every=crontab(day_of_month=1, hour=4, minute=23))
def hash_old_ssns():
    """Function converts all SSNs in previous year competitions to hashed SSNs.
    Hashed SSNs are stored for reference in case we need to connect/find same person in previous years.

    If there will be no good use cases, hashed SSNs could be removed in future.

    Executed as celery task once per month.
    """
    participants = Participant.objects.filter(created__lt=timezone.now() - datetime.timedelta(days=365)).exclude(ssn="")
    for participant in participants:
        Participant.objects.filter(id=participant.id).update(ssn="hashed", ssn_hashed=base64.b64encode(hmac.new(str.encode(settings.SECRET_KEY), str.encode(participant.ssn), digestmod=hashlib.sha256).digest()))
