from celery.task import task
from celery import Task
from django.template.loader import render_to_string
from django.utils import timezone
from premailer import transform
from django.conf import settings
from core.models import User, FailedTask
from marketing.models import MailgunEmail
from django.utils.translation import ugettext_lazy as _
from marketing.tasks import send_mailgun
import json


class LogErrorsTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.save_failed_task(exc, task_id, args, kwargs, einfo)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :type exc: Exception
        """
        task = FailedTask()
        task.celery_task_id = task_id
        task.full_name = self.name
        task.name = self.name.split('.')[-1]
        task.exception_class = exc.__class__.__name__
        task.exception_msg = unicode(exc).strip()
        task.traceback = unicode(traceback).strip()
        task.updated_at = timezone.now()

        if args:
            task.args = json.dumps(list(args))
        if kwargs:
            task.kwargs = json.dumps(kwargs)

        # Find if task with same args, name and exception already exists
        # If it do, update failures count and last updated_at
        #: :type: FailedTask
        existing_task = FailedTask.objects.filter(
            args=task.args,
            kwargs=task.kwargs,
            full_name=task.full_name,
            exception_class=task.exception_class,
            exception_msg=task.exception_msg,
        )

        if len(existing_task):
            existing_task = existing_task[0]
            existing_task.failures += 1
            existing_task.updated_at = task.updated_at
            existing_task.save(force_update=True,
                               update_fields=('updated_at', 'failures'))
        else:
            task.save(force_insert=True)




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
