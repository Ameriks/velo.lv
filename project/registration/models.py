# coding=utf-8
from __future__ import unicode_literals
from django.contrib.contenttypes import generic
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template.defaultfilters import slugify

import uuid
from core.models import Choices, CustomSlug
from payment.models import Payment
from registration.utils import recalculate_participant
from velo.mixins.models import TimestampMixin, StatusMixin
from django_countries.fields import CountryField
from velo.utils import load_class


class Application(TimestampMixin, models.Model):
    PAY_STATUS_CANCELLED = -10
    PAY_STATUS_NOT_PAYED = 0
    PAY_STATUS_APPROVED = 5  # Not used.
    PAY_STATUS_WAITING = 10
    PAY_STATUS_PAYED = 20
    PAY_STATUS = (
        (PAY_STATUS_CANCELLED, _('Cancelled')),
        (PAY_STATUS_NOT_PAYED, _("Haven't Payed")),
        (PAY_STATUS_APPROVED, _("Approved for Payment")),
        (PAY_STATUS_WAITING, _('Waiting for Payment')),
        (PAY_STATUS_PAYED, _('Payed')),
    )
    competition = models.ForeignKey('core.Competition', verbose_name=_('Competition'))
    payment_status = models.SmallIntegerField(_('Payment Status'), default=0, choices=PAY_STATUS)
    discount_code = models.ForeignKey('payment.DiscountCode', blank=True, null=True)

    email = models.EmailField(blank=True, help_text=_("You will receive payment confirmation and information about start numbers."))

    code = models.CharField(max_length=50, default=lambda: str(uuid.uuid4()), unique=True)
    legacy_id = models.IntegerField(blank=True, null=True)

    company_name = models.CharField(_('Company name / Full Name'), max_length=100, blank=True)
    company_vat = models.CharField(_('VAT Number'), max_length=100, blank=True)
    company_regnr = models.CharField(_('Company number / SSN'), max_length=100, blank=True)
    company_address = models.CharField(_('Address'), max_length=100, blank=True)
    company_juridical_address = models.CharField(_('Juridical Address'), max_length=100, blank=True)

    external_invoice_code = models.CharField(_('Invoice code'), max_length=100, blank=True)  # invoice code from e-rekins used to allow downloading invoice from velo.lv
    external_invoice_nr = models.CharField(_('Invoice Number'), max_length=20, blank=True)  # invoice number from e-rekins used in card payment

    donation = models.DecimalField(_('Donation'), max_digits=20, decimal_places=2, default=0.0)

    # Totals
    total_discount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_entry_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_insurance_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    final_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)


    payment_set = generic.GenericRelation(Payment) #, related_name="application")

    def set_final_price(self):
        self.final_price = float(self.total_entry_fee) + float(self.total_insurance_fee) + float(self.donation)

    @property
    def competition_name(self):
        if self.competition.level == 2:
            return '%s - %s' % (self.competition.parent, self.competition)
        else:
            return unicode(self.competition)

    def save(self, *args, **kwargs):
        self.set_final_price()
        return super(Application, self).save(*args, **kwargs)

class Participant(TimestampMixin, models.Model):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
    )
    application = models.ForeignKey(Application, blank=True, null=True)
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance', blank=True, null=True)
    price = models.ForeignKey('payment.Price', blank=True, null=True)

    discount_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    insurance = models.ForeignKey('core.Insurance', blank=True, null=True)

    team = models.ForeignKey('team.Team', blank=True, null=True)  # If participant is in official team, then this is filled
    team_name = models.CharField(_('Team'), max_length=50, blank=True)  # If participant is not within official team, then he can fill this field
    team_name_slug = models.SlugField(blank=True)

    is_participating = models.BooleanField(_('Is Participating'), default=False)
    is_paying = models.BooleanField(_('Is Paying'), default=True)
    is_competing = models.BooleanField(_('Is Competing'), default=True)  # in case this cyclist is participating for fun, then is_competing should be set to false.

    first_name = models.CharField(_('First Name'), max_length=60, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=60, blank=True)
    birthday = models.DateField(_('Birthday'), help_text=_('YYYY-MM-DD'), blank=True, null=True)
    is_only_year = models.BooleanField(default=False)
    slug = models.SlugField(blank=True)

    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES, blank=True)

    ssn = models.CharField(_('Social Security Number'), max_length=12, blank=True)

    phone_number = models.CharField(_('Phone Number'), max_length=60, blank=True, help_text="Uz šo telefona numuru tiks sūtīts rezultāts")
    email = models.EmailField(_('Email'), blank=True)

    send_email = models.BooleanField(_('Send Email'), default=True)
    send_sms = models.BooleanField(_('Send SMS'), default=True)

    country = CountryField(_('Country'), blank=True, null=True)
    city = models.ForeignKey('core.Choices', related_name='+', limit_choices_to={'kind': Choices.KIND_CITY}, verbose_name=_('City'), blank=True, null=True)

    bike_brand = models.ForeignKey('core.Choices', related_name='+', limit_choices_to={'kind': Choices.KIND_BIKEBRAND}, verbose_name=_('Bike Brand'), blank=True, null=True)
    bike_brand2 = models.CharField(_('Bike Brand'), max_length=20, blank=True)


    occupation = models.ForeignKey('core.Choices', related_name='+', limit_choices_to={'kind': Choices.KIND_OCCUPATION}, verbose_name=_('Occupation'), blank=True, null=True)
    where_heard = models.ForeignKey('core.Choices', related_name='+', limit_choices_to={'kind': Choices.KIND_HEARD}, verbose_name=_('Where Heard'), blank=True, null=True)

    group = models.CharField(_('Group'), max_length=50, blank=True, help_text=_('Assigned automatically'))  # moved group away from results

    registrant = models.ForeignKey('core.User', blank=True, null=True, verbose_name=_('Registrant'))
    legacy_id = models.IntegerField(blank=True, null=True)

    full_name = models.CharField(_('Full Name'), max_length=120, blank=True)

    primary_number = models.ForeignKey('registration.Number', blank=True, null=True)

    is_temporary = models.BooleanField(default=False)
    is_sent_number_email = models.BooleanField(default=False)
    is_sent_number_sms = models.BooleanField(default=False)

    registration_dt = models.DateTimeField(_("Registration Date"), blank=True, null=True)

    comment = models.TextField(blank=True)

    total_entry_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    total_insurance_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    final_price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)

    class Meta:
        ordering = ('distance', 'created')
        verbose_name = _('participant')
        verbose_name_plural = _('participants')

    def __unicode__(self):
        return '%s %s - %s %s' % (self.first_name, self.last_name, self.competition, self.distance)

    def set_slug(self):
        if self.birthday:
            try:
                self.slug = CustomSlug.objects.get(first_name=self.first_name, last_name=self.last_name, birthday=self.birthday).slug
            except CustomSlug.DoesNotExist:
                self.slug = slugify('%s-%s-%i' % (self.first_name, self.last_name, self.birthday.year))
        else:
            self.slug = slugify('%s-%s' % (self.first_name, self.last_name))

    def set_group(self):
        if not self.group and self.is_participating:
            if self.competition.processing_class:
                class_ = load_class(self.competition.processing_class)
                processing_class = class_(self.competition_id)
                self.group = processing_class.assign_group(self.distance_id, self.gender, self.birthday)


    def save(self, *args, **kwargs):
        self.full_name = '%s %s' % (self.first_name, self.last_name)  # Full name always should be based on first_name and last_name fields

        self.team_name_slug = slugify(self.team_name.replace(' ', ''))

        # In case first name, last name or birthday is changed, then slug changes as well.
        old_slug = self.slug
        self.set_slug()
        if old_slug != self.slug:
            self.numbers(slug=old_slug).update(participant_slug=self.slug)  # We update number slugs to match new slug

            if self.team:
                team = self.team
                self.team = None  # Remove connection to existing team member.

                # Because of slug change connection to team is disconnected.
                # After disconnection team points are recalculated on every stage team have participated.
                try:
                    member = team.member_set.get(slug=old_slug)
                    for appl in member.memberapplication_set.all():
                        class_ = load_class(appl.competition.processing_class)
                        processing_class = class_(competition=appl.competition)
                        processing_class.recalculate_team_result(team=team)
                        appl.participant = None
                        appl.participant_unpaid = None
                        appl.participant_potential = None
                        appl.save()
                except:
                    pass

            sebs = self.primary_sebstandings_set.filter(competition_id__in=self.competition.get_ids())
            if sebs:
                seb = sebs[0]
                seb.participant_slug = self.slug
                seb.save()



        self.set_group()

        if not self.primary_number and self.is_participating:
            numbers = self.numbers().order_by('-number')
            if numbers:
                self.primary_number = numbers[0]

        if not self.registration_dt:
            self.registration_dt = timezone.now()

        # Recalculate totals. # TODO: This should be done when creating payment, not on any save.
        recalculate_participant(self, commit=False)

        obj = super(Participant, self).save(*args, **kwargs)

        if old_slug != self.slug:
            from team.utils import match_participant_to_applied
            match_participant_to_applied(self)

        return obj

    def numbers(self, slug=None):
        self.set_group()
        if not slug:
            slug = self.slug
        number_queryset = Number.objects.filter(participant_slug=slug, competition_id__in=self.competition.get_ids(), distance=self.distance)
        if self.group and self.group[0] == 'B':
            number_queryset = number_queryset.filter(group=self.group)
        return number_queryset


class Number(StatusMixin, TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    number = models.IntegerField()
    number_text = models.CharField(max_length=50, blank=True)
    participant_slug = models.SlugField(blank=True)
    group = models.CharField(_('Group'), max_length=50, blank=True)

    def __unicode__(self):
        if not self.group:
            return str(self.number)
        else:
            return '%s - %i' % (self.group, self.number)

    class Meta:
        unique_together = ('competition', 'number', 'group')
        ordering = ('distance', 'group', 'number', )


class PreNumberAssign(models.Model):
    competition = models.ForeignKey('core.Competition')
    distance = models.ForeignKey('core.Distance')
    number = models.IntegerField(blank=True, null=True)
    segment = models.IntegerField(blank=True, null=True)
    participant_slug = models.SlugField(blank=True)
    group_together = models.SlugField(blank=True, null=True)