from celery.task import task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import requests
from marketing.models import MailgunEmail


@task(max_retries=5)
def send_mailgun(_id=None, email=None):
    if not email:
        email = MailgunEmail.objects.get(id=_id)

    if email.is_sent:
        print 'Already sent'
        return False

    msg = EmailMultiAlternatives(email.subject, email.text, email.em_from, to=[email.em_to, ], cc=[email.em_cc, ])
    msg.attach_alternative(email.html, "text/html")
    msg.send()

    email.is_sent = True
    email.save()

    return True