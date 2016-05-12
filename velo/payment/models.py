# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function
from builtins import str

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from model_utils import Choices

from velo.velo.mixins.models import TimestampMixin


class ActivePriceManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(start_registering__lte=timezone.now(), end_registering__gte=timezone.now())


@python_2_unicode_compatible
class Price(TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    from_year = models.IntegerField(default=0)
    till_year = models.IntegerField(default=2050)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    start_registering = models.DateTimeField(blank=True, null=True)
    end_registering = models.DateTimeField(blank=True, null=True)

    objects = ActivePriceManager()

    class Meta:
        ordering = ('distance', 'start_registering')
        permissions = (
            ('can_see_totals', 'Can see income totals'),
        )

    def __str__(self):
        return str(self.price)


@python_2_unicode_compatible
class DiscountCampaign(models.Model):
    title = models.CharField(max_length=50)
    competition = models.ForeignKey('core.Competition')
    discount_entry_fee_percent = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_entry_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_insurance_percent = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_insurance = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    def __str__(self):
        name = ''
        if self.discount_entry_fee:
            name = '{0}€ '.format(self.discount_entry_fee)
        elif self.discount_entry_fee_percent:
            name = '{0}% '.format(self.discount_entry_fee_percent)
        if self.discount_insurance:
            name += 'Apdr.{0}€ '.format(self.discount_insurance)
        elif self.discount_insurance_percent:
            name += 'Apdr.{0}% '.format(self.discount_insurance_percent)
        return name


@python_2_unicode_compatible
class DiscountCode(TimestampMixin, models.Model):
    campaign = models.ForeignKey('payment.DiscountCampaign')
    code = models.CharField(max_length=20, unique=True)
    usage_times = models.IntegerField(default=1)
    usage_times_left = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '%s - %s' % (self.code, str(self.campaign))

    def calculate_entry_fee(self, fee):
        if self.campaign.discount_entry_fee:
            return fee - self.campaign.discount_entry_fee
        else:
            return fee * float(100 - self.campaign.discount_entry_fee_percent) / 100

    def calculate_insurance(self, fee):
        if self.campaign.discount_insurance:
            return fee - self.campaign.discount_insurance
        else:
            return fee * float(100 - self.campaign.discount_insurance_percent) / 100


@python_2_unicode_compatible
class PaymentChannel(models.Model):
    payment_channel = models.CharField(max_length=20, default='LKDF')
    title = models.CharField(max_length=50)
    image_slug = models.CharField(max_length=50, blank=True)
    erekins_url_prefix = models.CharField(max_length=50, blank=True)
    erekins_auth_key = models.CharField(max_length=100, blank=True)
    erekins_link = models.CharField(max_length=50, blank=True)
    is_bill = models.BooleanField(default=False)

    def __str__(self):
        return ugettext(self.title)

    def translations(self): # This is just place holder for translation strings for unicode function
        ugettext("Receive Bill")


@python_2_unicode_compatible
class ActivePaymentChannel(models.Model):
    payment_channel = models.ForeignKey('payment.PaymentChannel')
    competition = models.ForeignKey('core.Competition')
    from_date = models.DateTimeField()
    till_date = models.DateTimeField()

    def __str__(self):
        return str(self.payment_channel)


class Payment(TimestampMixin, models.Model):
    STATUSES = Choices((10, 'new', _('New')),
                       (20, 'pending', _('Pending')),
                       (30, 'ok', _('OK')),
                       (-10, 'reversed', _('Reversed')),
                       (-20, 'cancelled', _('Cancelled')),
                       (-30, 'timeout', _('Timeout')),
                       (-40, 'declained', _('Declined')),
                       (-50, 'failed', _('Failed')),
                       (-60, 'error', _('Error')),
                       (-70, 'id_not_found', _('ID not found')),
                       )

    legacy_id = models.IntegerField(blank=True, null=True)

    # This model can have relation to either Application or Team
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    channel = models.ForeignKey('payment.ActivePaymentChannel', blank=True, null=True)
    erekins_code = models.CharField(max_length=100, blank=True)  # Erekins code

    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    donation = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    status = models.SmallIntegerField(choices=STATUSES, default=STATUSES.new)
