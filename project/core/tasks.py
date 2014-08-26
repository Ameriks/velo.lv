from celery.task import task
from django.template.loader import render_to_string
from premailer import transform
from django.conf import settings
from core.models import User
from marketing.models import MailgunEmail
from django.utils.translation import ugettext_lazy as _
from marketing.tasks import send_mailgun


@task
def send_email_confirmation(user_id):
    user = User.objects.get(id=user_id)
    context = {
        'object': user,
        'domain': settings.MY_DEFAULT_DOMAIN,
    }

    template = transform(render_to_string('core/email/email_confirmation.html', context))
    template_txt = render_to_string('core/email/email_confirmation.txt', context)

    email_data = {
        'em_to': user.email,
        'subject': _('Verify your velo.lv email address'),
        'html': template,
        'text': template_txt,
        'content_object': user,
    }
    mailgun = MailgunEmail.objects.create(**email_data)
    send_mailgun(email=mailgun)
    return mailgun

@task
def send_change_email_notification(user_id, old_email):
    user = User.objects.get(id=user_id)
    context = {
        'object': user,
        'domain': settings.MY_DEFAULT_DOMAIN,
    }

    template = transform(render_to_string('core/email/email_change.html', context))
    template_txt = render_to_string('core/email/email_change.txt', context)

    email_data = {
        'em_to': old_email,
        'subject': _('Change Email Notification'),
        'html': template,
        'text': template_txt,
        'content_object': user,
    }
    mailgun = MailgunEmail.objects.create(**email_data)
    send_mailgun(email=mailgun)
    return mailgun
