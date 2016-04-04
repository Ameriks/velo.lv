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

    if settings.DEBUG:
        msg = EmailMultiAlternatives(email.subject, email.text, email.em_from, to=[email.em_to, ], cc=[email.em_cc, ])
        msg.attach_alternative(email.html, "text/html")
        msg.send()
        return True
    try:
        data = {
            "from": email.em_from,
            "to": email.em_to.split(';'),
            "subject": email.subject,
            "text": email.text,
            "html": email.html,
            "v:email_code": email.code,
        }
        if email.em_cc:
            data.update({"cc": email.em_cc.split(';')})
        if email.em_replyto:
            data.update({'h:Reply-To': email.em_replyto})

        ret = requests.post(
            "%s/mans.velo.lv/messages" % settings.MAILGUN_URL,
            auth=("api", settings.MAILGUN_ACCESS_KEY),
            data=data)
        if ret.status_code == 200:
            email.is_sent = True
            email.email_id = ret.json().get('id')
            email.save()
        else:
            raise Exception
    except Exception as exc:
        raise send_mailgun.retry(exc=exc, countdown=120)