# coding=utf-8
from __future__ import unicode_literals

from celery import task
from premailer import transform

from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from marketing.models import MailgunEmail
from registration.models import Application


@task()
def send_success_email(application_id):
    application = Application.objects.select_related('competition',).get(id=application_id)

    competition = application.competition

    if competition.get_children():
        competitions = competition.get_children()
    else:
        competitions = (competition, )

    context = {
        'application': application,
        'competitions': competitions,
        'url': "{0}{1}".format(settings.MY_DEFAULT_DOMAIN, reverse('application', kwargs={'slug': application.code}))
    }

    template = transform(render_to_string('registration/email/success_email.html', context))
    template_txt = render_to_string('registration/email/success_email.txt', context)

    email_data = {
        'em_to': application.email,
        'subject': u'velo.lv dalībnieku pieteikums nr.%i' % application_id,
        'html': template,
        'text': template_txt,
        'content_object': application,
    }
    mailgun = MailgunEmail.objects.create(**email_data)

    return mailgun