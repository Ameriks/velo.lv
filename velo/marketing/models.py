from django.db import models
from django.contrib.contenttypes.models import ContentType


class SMS(models.Model):
    phone_number = models.CharField(max_length=20)
    text = models.CharField(max_length=160)
    is_processed = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    discount_code = models.ForeignKey('payment.DiscountCode', blank=True, null=True)
    send_out_at = models.DateTimeField()
    status = models.CharField(max_length=50, blank=True)

    class Meta:
        permissions = (
            ('can_update_marketing', 'Can update marketing'),
        )
