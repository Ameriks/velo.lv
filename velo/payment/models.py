import datetime
import importlib
import uuid

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.files.storage import FileSystemStorage
from model_utils import Choices
from slugify import slugify

from velo.velo.mixins.models import TimestampMixin
import os

import logging
from django.db import connection


logger = logging.getLogger('velo.payment')

upload_storage = FileSystemStorage(location="config/certificates/")


def _get_next_sequence_value(series, kind="payment"):
    if not series or series == "":
        return False

    series = slugify(series, only_ascii=True, ok="_")
    cursor = connection.cursor()
    sequence_name = "%s_sequence_%s" % (kind, series)
    cursor.execute('CREATE SEQUENCE IF NOT EXISTS %s START 1;' % sequence_name)
    cursor.execute("SELECT nextval('%s');" % sequence_name)
    return cursor.fetchone()[0]


def get_invoice_upload(instance, filename):
    series = instance.series
    if not series or series == "":
        series = "unknown"
    return os.path.join("payment", "invoice", series, filename)


def current_year():
    return datetime.date.today().year


class ActivePriceManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(start_registering__lte=timezone.now(), end_registering__gte=timezone.now())


class Price(TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition', on_delete=models.PROTECT)
    distance = models.ForeignKey('core.Distance', on_delete=models.PROTECT)
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


class DiscountCampaign(models.Model):
    title = models.CharField(max_length=50)
    competition = models.ForeignKey('core.Competition', on_delete=models.PROTECT)
    discount_entry_fee_percent = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_entry_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_insurance_percent = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_insurance = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    discount_kind = models.CharField(max_length=100, blank=True, null=True, default=None)

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


class DiscountCode(TimestampMixin, models.Model):
    campaign = models.ForeignKey('payment.DiscountCampaign', on_delete=models.PROTECT)
    code = models.CharField(max_length=20, )
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


class PaymentChannel(models.Model):
    payment_channel = models.CharField(max_length=20, default='LKDF')
    title = models.CharField(max_length=50)
    image_slug = models.CharField(max_length=50, blank=True)
    erekins_url_prefix = models.CharField(max_length=50, blank=True)
    erekins_auth_key = models.CharField(max_length=100, blank=True)
    erekins_link = models.CharField(max_length=50, blank=True)
    is_bill = models.BooleanField(default=False)
    params = JSONField(default={})

    url = models.CharField(max_length=255, blank=True)
    server_url = models.CharField(max_length=255, blank=True)

    key_file = models.FileField(verbose_name="Private Key", null=True, blank=True, storage=upload_storage)
    cert_file = models.FileField(verbose_name="Certificate or Public Key", null=True, blank=True, storage=upload_storage)

    def __str__(self):
        return ugettext(self.title)

    def translations(self):  # This is just place holder for translation strings for unicode function
        ugettext("Receive Bill")

    @property
    def get_class(self):
        MAPPING = {
            "Swedbank": 'SwedbankIntegration',
            "IBanka": 'IBankIntegration',
            "FirstData": 'FirstDataIntegration',
        }
        class_str = MAPPING.get(self.title, None)
        if not class_str:
            raise Exception("Incorrent BankLink")
        module = importlib.import_module("velo.payment.bank")
        return getattr(module, class_str)


class ActivePaymentChannel(models.Model):
    payment_channel = models.ForeignKey('payment.PaymentChannel', on_delete=models.PROTECT)
    competition = models.ForeignKey('core.Competition', on_delete=models.PROTECT)
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

    # This model can have relation to either Application or Team
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Remove next 2 fields
    channel = models.ForeignKey('payment.ActivePaymentChannel', blank=True, null=True)
    erekins_code = models.CharField(max_length=100, blank=True)  # Erekins code

    total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    donation = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    status = models.SmallIntegerField(choices=STATUSES, default=STATUSES.new)

    competition = models.ForeignKey('core.Competition', null=True, blank=True)  # used for payment matching in analytics


class Invoice(TimestampMixin, models.Model):
    channel = models.ForeignKey('payment.PaymentChannel', on_delete=models.PROTECT)
    competition = models.ForeignKey('core.Competition', verbose_name=_('Competition'), blank=True, null=True, on_delete=models.PROTECT)
    payment = models.ForeignKey(Payment, verbose_name=_('Payment'), blank=True, null=True, on_delete=models.PROTECT)

    company_name = models.CharField(_('Company name / Full Name'), max_length=100, blank=True)
    company_vat = models.CharField(_('VAT Number'), max_length=100, blank=True)
    company_regnr = models.CharField(_('Company number / SSN'), max_length=100, blank=True)
    company_address = models.CharField(_('Address'), max_length=100, blank=True)
    company_juridical_address = models.CharField(_('Juridical Address'), max_length=100, blank=True)
    email = models.EmailField(blank=True, max_length=254)

    invoice_show_names = models.BooleanField(_('Show participant names in invoice'), default=True)

    slug = models.CharField(max_length=50, default=uuid.uuid4, unique=True)
    file = models.FileField(_("Invoice"), upload_to=get_invoice_upload, blank=True)
    series = models.CharField(_('Competition series'), max_length=10, blank=True)
    number = models.IntegerField(_('Series invoice number'), null=True, blank=True)

    access_time = models.TimeField(null=True, blank=True)
    access_ip = models.CharField(max_length=100, null=True, blank=True)

    invoice_data = JSONField(default=dict)

    @property
    def invoice_nr(self):
        return "%s-%03d" % (self.series, self.number)

    def set_number(self):
        if settings.TESTING:
            self.number = 1
        elif not self.number:
            self.number = _get_next_sequence_value(self.series)

    def save(self, *args, **kwargs):
        self.set_number()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("series", "number")


class Transaction(TimestampMixin, models.Model):
    STATUSES = Choices(
        (-70, 'id_not_found', _('ID not found')),
        (-60, 'error', _('Error')),
        (-50, 'failed', _('Failed')),
        (-40, 'declined', _('Declined')),
        (-30, 'timeout', _('Timeout')),
        (-20, 'cancelled', _('Cancelled')),
        (-10, 'reversed', _('Reversed')),
        (10, 'new', _('New')),
        (20, 'pending', _('Pending')),
        (30, 'ok', _('OK')),
    )
    channel = models.ForeignKey('payment.PaymentChannel', on_delete=models.PROTECT)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    code = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
    status = models.SmallIntegerField(choices=STATUSES, default=STATUSES.new)
    external_code = models.CharField(max_length=50, blank=True)
    external_code_requested = models.DateTimeField(blank=True, null=True)

    amount = models.DecimalField(_("Total amount"), max_digits=20, decimal_places=2, default=0.0)

    information = models.CharField(max_length=255, blank=True)

    language = models.CharField(max_length=10, default="lv")

    created_ip = models.GenericIPAddressField(blank=True, null=True)

    server_response_at = models.DateTimeField(blank=True, null=True)
    user_response_at = models.DateTimeField(blank=True, null=True)

    server_response = models.TextField(blank=True)
    user_response = models.TextField(blank=True)

    returned_user_ip = models.GenericIPAddressField(blank=True, null=True)
    returned_server_ip = models.GenericIPAddressField(blank=True, null=True)

    should_be_reviewed = models.BooleanField(default=False)  # This is set if something is weird in transaction.

    integration_id = models.CharField(max_length=50, blank=True)

    @property
    def language_bank(self):
        return {'en': 'ENG', 'lv': 'LAT', 'ru': 'RUS'}.get(self.language)


class DailyTransactionTotals(TimestampMixin, models.Model):
    date = models.DateField()
    channel = models.ForeignKey(PaymentChannel, on_delete=models.PROTECT)
    calculated_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, blank=False, null=False)
    reported_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.0, blank=False, null=False)
    params = JSONField(default={}, null=False, blank=False)

