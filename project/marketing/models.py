from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
import uuid


class SMS(models.Model):
    phone_number = models.CharField(max_length=20)
    text = models.CharField(max_length=160)
    is_processed = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    discount_code = models.ForeignKey('payment.DiscountCode', blank=True, null=True)
    send_out_at = models.DateTimeField()
    status = models.CharField(max_length=50, blank=True)


class MailgunEmail(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    code = models.CharField(max_length=50, default=lambda: str(uuid.uuid4()), unique=True)

    em_from = models.CharField(max_length=85, default=settings.MAILGUN_FROM)
    em_to = models.CharField(max_length=255)
    em_cc = models.CharField(max_length=255)
    em_replyto = models.CharField(max_length=255, default='pieteikumi@velo.lv')
    subject = models.TextField()
    html = models.TextField()
    text = models.TextField()

    is_sent = models.BooleanField(default=False)
    mailgun_id = models.CharField(max_length=80, blank=True)

    def save(self, *args, **kwargs):
        is_created = False if self.id else True
        super(MailgunEmail, self).save(*args, **kwargs)
        if is_created:
            from marketing.tasks import send_mailgun
            send_mailgun.delay(self.id)