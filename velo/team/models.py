from django.db import models
from django.utils.translation import ugettext_lazy as _

import os
import uuid
from autoslug import AutoSlugField
from django_countries.fields import CountryField
from easy_thumbnails.fields import ThumbnailerImageField
from slugify import slugify

from velo.core.models import CustomSlug
from velo.results.models import Result
from velo.velo.mixins.models import StatusMixin, TimestampMixin


def get_team_upload(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("teams", "%s%s" % (filename, ext))


class Team(StatusMixin, TimestampMixin, models.Model):
    distance = models.ForeignKey('core.Distance')
    title = models.CharField(_('Title'), max_length=100)
    slug = AutoSlugField(populate_from='title', always_update=True)

    description = models.TextField(_('Description'), blank=True)
    img = models.ImageField(_('Image'), upload_to=get_team_upload, blank=True)
    shirt_image = models.ImageField(_('Shirt Image'), upload_to=get_team_upload, blank=True)
    country = CountryField(_('Country'))

    contact_person = models.CharField(_('Contact Person'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=50, blank=True)
    show_contact_info = models.BooleanField(_("Show contact information in public team profile"), default=True)

    management_info = models.TextField(_('Management Info'), blank=True)

    is_featured = models.BooleanField(default=False)

    owner = models.ForeignKey('core.User')

    legacy_id = models.IntegerField(blank=True, null=True)

    # This is for invoice
    final_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    company_name = models.CharField(_('Company name / Full Name'), max_length=100, blank=True)
    company_vat = models.CharField(_('VAT Number'), max_length=100, blank=True)
    company_regnr = models.CharField(_('Company number / SSN'), max_length=100, blank=True)
    company_address = models.CharField(_('Address'), max_length=100, blank=True)
    company_juridical_address = models.CharField(_('Juridical Address'), max_length=100, blank=True)
    external_invoice_code = models.CharField(_('Invoice code'), max_length=100, blank=True)  # invoice code from e-rekins used to allow downloading invoice from velo.lv
    external_invoice_nr = models.CharField(_('Invoice Number'), max_length=20, blank=True)  # invoice number from e-rekins used in card payment
    invoice = models.ForeignKey('payment.Invoice', null=True, blank=True)
    is_w = models.BooleanField(_('Women team'), default=False, )

    class Meta:
        ordering = ('distance', '-is_featured', 'title')

    def __str__(self):
        return self.title

    @property
    def competition(self):
        return self.distance.competition


class Member(StatusMixin, models.Model):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
    )
    team = models.ForeignKey(Team)
    first_name = models.CharField(_('First Name'), max_length=60)
    last_name = models.CharField(_('Last Name'), max_length=60)
    birthday = models.DateField(_('Birthday'))
    slug = models.SlugField()
    ssn = models.CharField(_('SSN'), max_length=12, blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=60, blank=True,
                                    help_text=_("Result will be sent to this phone number"))

    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES, blank=True)

    country = CountryField(_('Country'))
    license_nr = models.CharField(_('License NR'), max_length=50, blank=True)

    image = ThumbnailerImageField(_("Image"), blank=True, upload_to=get_team_upload)

    def __str__(self):
        return '%s %s %s' % (self.first_name, self.last_name, self.birthday)

    def save(self, *args, **kwargs):
        try:
            self.slug = CustomSlug.objects.get(first_name=self.first_name, last_name=self.last_name,
                                               birthday=self.birthday).slug
        except CustomSlug.DoesNotExist:
            self.slug = slugify('%s-%s-%i' % (self.first_name, self.last_name, self.birthday.year), only_ascii=True)
        return super(Member, self).save(*args, **kwargs)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)


class MemberApplication(models.Model):
    KIND_PARTICIPANT = 10
    KIND_RESERVE = 20
    KIND = (
        (KIND_PARTICIPANT, _('Participant')),
        (KIND_RESERVE, _('Reserve')),
    )
    member = models.ForeignKey(Member)
    competition = models.ForeignKey('core.Competition')
    kind = models.SmallIntegerField(_('Kind'), choices=KIND, db_index=True)

    participant = models.ForeignKey('registration.Participant', blank=True, null=True)  # when participant applies, then team profile updates. And other way round.
    participant_unpaid = models.ForeignKey('registration.Participant', related_name='memberapplication_unpaid_set', blank=True, null=True)  # when participant applies, then team profile updates. And other way round.
    participant_potential = models.ForeignKey('registration.Participant', related_name='memberapplication_potential_set',blank=True, null=True)

    legacy_id = models.IntegerField(blank=True, null=True)

    @property
    def get_result(self):
        return Result.objects.get(competition=self.competition, participant=self.participant)
