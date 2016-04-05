# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function
from builtins import str

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from celery.task import task
from celery import Task
from django.utils import timezone
from premailer import transform
import json

from velo.core.models import User, FailedTask
from velo.marketing.models import MailgunEmail
from velo.marketing.tasks import send_mailgun


class LogErrorsTask(Task):
    def run(self, *args, **kwargs):
        pass

    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.save_failed_task(exc, task_id, args, kwargs, einfo)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :type exc: Exception
        """
        failed_task = FailedTask()
        failed_task.celery_task_id = task_id
        failed_task.full_name = self.name
        failed_task.name = self.name.split('.')[-1]
        failed_task.exception_class = exc.__class__.__name__
        failed_task.exception_msg = str(exc).strip()
        failed_task.traceback = str(traceback).strip()
        failed_task.updated_at = timezone.now()

        if args:
            failed_task.args = json.dumps(list(args))
        if kwargs:
            failed_task.kwargs = json.dumps(kwargs)

        # Find if task with same args, name and exception already exists
        # If it do, update failures count and last updated_at
        #: :type: FailedTask
        existing_task = FailedTask.objects.filter(
            args=failed_task.args,
            kwargs=failed_task.kwargs,
            full_name=failed_task.full_name,
            exception_class=failed_task.exception_class,
            exception_msg=failed_task.exception_msg,
        )

        if len(existing_task):
            existing_task = existing_task[0]
            existing_task.failures += 1
            existing_task.updated_at = task.updated_at
            existing_task.save(force_update=True,
                               update_fields=('updated_at', 'failures'))
        else:
            failed_task.save(force_insert=True)


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
