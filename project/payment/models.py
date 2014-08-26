from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

# Create your models here.
from django.contrib.contenttypes.models import ContentType
from velo.mixins.models import TimestampMixin


class Price(TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    from_year = models.IntegerField(default=0)
    till_year = models.IntegerField(default=2050)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    start_registering = models.DateTimeField(blank=True, null=True)
    end_registering = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ('distance', 'start_registering')
        permissions = (
            ('can_see_totals', 'Can see income totals')
        )
    def __unicode__(self):
        return str(self.price)


class DiscountCampaign(models.Model):
    title = models.CharField(max_length=50)
    competition = models.ForeignKey('core.Competition')


class DiscountCode(TimestampMixin, models.Model):
    campaign = models.ForeignKey('payment.DiscountCampaign')
    code = models.CharField(max_length=20, unique=True)
    usage_times = models.IntegerField(default=1)
    usage_times_left = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)


class PaymentChannel(models.Model):
    payment_channel = models.CharField(max_length=20, default='LKDF')
    title = models.CharField(max_length=50)
    image_slug = models.CharField(max_length=50, blank=True)
    erekins_url_prefix = models.CharField(max_length=50, blank=True)
    erekins_auth_key = models.CharField(max_length=100, blank=True)
    erekins_link = models.CharField(max_length=50, blank=True)
    is_bill = models.BooleanField(default=False)

    def translations(self): # This is just place holder for translation strings for unicode function
        ugettext("Receive Bill")

    def __unicode__(self):
        return ugettext(self.title)

class ActivePaymentChannel(models.Model):
    payment_channel = models.ForeignKey('payment.PaymentChannel')
    competition = models.ForeignKey('core.Competition')
    from_date = models.DateTimeField()
    till_date = models.DateTimeField()

    def __unicode__(self):
        return self.payment_channel


class Payment(TimestampMixin, models.Model):
    STATUS_ID_NOT_FOUND = -70
    STATUS_ERROR = -60
    STATUS_FAILED = -50
    STATUS_DECLINED = -40
    STATUS_TIMEOUT = -30
    STATUS_CANCELLED = -20
    STATUS_REVERSED = -10
    STATUS_NEW = 10
    STATUS_PENDING = 20
    STATUS_OK = 30
    STATUSES = (
        (STATUS_ID_NOT_FOUND, _('ID not found')),
        (STATUS_ERROR, _('Error')),
        (STATUS_FAILED, _('Failed')),
        (STATUS_DECLINED, _('Declined')),
        (STATUS_TIMEOUT, _('Timeout')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_REVERSED, _('Reversed')),
        (STATUS_NEW, _('New')),
        (STATUS_PENDING, _('Pending')),
        (STATUS_OK, _('OK')),
    )

    # This model can have relation to either Application or Team
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    channel = models.ForeignKey('payment.ActivePaymentChannel')
    erekins_code = models.CharField(max_length=100, blank=True)  # Erekins code

    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_NEW)
