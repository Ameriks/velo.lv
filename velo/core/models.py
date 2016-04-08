# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function
from builtins import bytes, dict, int, list, object, range, str, ascii, chr, hex, input, next, oct, open, pow, round, super, filter, map, zip

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser, PermissionsMixin, AbstractBaseUser, UserManager
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields import JSONField

import datetime
import json
import os
import uuid
from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices as XChoices
from mptt.models import MPTTModel, TreeForeignKey
from django_countries.fields import CountryField
from autoslug import AutoSlugField

from velo.marketing.models import MailgunEmail
from velo.velo.mixins.models import TimestampMixin, StatusMixin


def _get_insurance_term_upload_path(instance, filename):
    return os.path.join("insurance", str(uuid.uuid4()), filename)


def _get_logo_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("competition", "%02d_%s%s" % (instance.id, filename, ext))


def _get_map_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    if instance.competition_id:
        return os.path.join("competition", "maps", "%02d_%s%s" % (instance.competition_id, filename, ext))
    else:
        return os.path.join("competition", "maps", "%s%s" % (filename, ext))


@python_2_unicode_compatible
class FailedTask(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=125)
    full_name = models.TextField()
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    exception_class = models.TextField()
    exception_msg = models.TextField()
    traceback = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=36)
    failures = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ('-updated_at',)

    def __str__(self):
        return '%s %s [%s]' % (self.name, self.args, self.exception_class)

    def retry_and_delete(self, inline=False):

        import importlib

        # Import real module and function
        mod_name, func_name = self.full_name.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)

        args = json.loads(self.args) if self.args else ()
        kwargs = json.loads(self.kwargs) if self.kwargs else {}
        if inline:
            try:
                res = func(*args, **kwargs)
                self.delete()
                return res
            except Exception as e:
                raise e

        self.delete()
        return func.delay(*args, **kwargs)


@python_2_unicode_compatible
class Choices(models.Model):  # TODO: Rename model
    KINDS = XChoices((10, 'bike_brand', _('Bike Brand')),
                    (20, 'occupation', _('Occupation')),
                    (30, 'heard', _('Where Heard')),
                    (40, 'city', _('City')),)

    kind = models.SmallIntegerField(choices=KINDS)
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_STATUS = XChoices((10, 'not_validated', _('Not yet validated')),
                           (20, 'bounced', _('Bounced')),
                           (40, 'validating', _('Validating')),
                           (50, 'valid', _('Valid')),
                           (-10, 'invalid', _('Invalid')), )

    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=True)

    email = models.EmailField(_('Email Address'), unique=True)
    email_status = models.SmallIntegerField(default=EMAIL_STATUS.not_validated, choices=EMAIL_STATUS)

    country = CountryField(_('Country'), blank=True, null=True, default="LV")
    ssn = models.CharField(_('Social Security Number'), max_length=12, blank=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True, help_text='YYYY-MM-DD')
    city = models.ForeignKey('core.Choices', verbose_name=_('City'), related_name='+',
                             limit_choices_to={'kind': Choices.KINDS.city}, blank=True, null=True)
    bike_brand = models.ForeignKey('core.Choices', verbose_name=_('Bike Brand'), related_name='+',
                                   limit_choices_to={'kind': Choices.KINDS.bike_brand}, blank=True, null=True)
    phone_number = models.CharField(_('Phone Number'), max_length=60, blank=True)
    send_email = models.BooleanField(default=True, verbose_name=_('Send Email Newsletters'))
    legacy_id = models.IntegerField(blank=True, null=True)

    full_name = models.CharField(_('Full Name'), max_length=60, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        if self.full_name:
            return self.full_name
        else:
            return self.email

    def save(self, *args, **kwargs):
        if self.last_login is None:
            self.last_login = timezone.now()  # Bug fix due to error creating user
        self.full_name = ('%s %s' % (self.first_name, self.last_name)).strip()

        return super(User, self).save(*args, **kwargs)

    def set_email_validation_code(self):
        self.email_validation_code = str(uuid.uuid4())
        self.email_validation_expiry = timezone.now() + datetime.timedelta(days=1)

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)  # TODO: Fix url

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    @property
    def username(self):
        return self.email


@python_2_unicode_compatible
class Competition(MPTTModel):
    KINDS = XChoices((0, 'velo', _('Velo')),
                    (1, 'cross_country', _('Cross Country')), )

    name = models.CharField(max_length=100)
    alias = AutoSlugField(populate_from='name')
    short_name = models.CharField(max_length=50, blank=True)

    created_by = models.ForeignKey('core.User', related_name='created_%(class)s_set', null=True, blank=True)
    modified_by = models.ForeignKey('core.User', related_name='modified_%(class)s_set', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    place_name = models.CharField(max_length=50, blank=True)
    competition_date = models.DateField(blank=True, null=True)
    competition_date_till = models.DateField(blank=True, null=True)

    kind = models.SmallIntegerField(choices=KINDS, default=KINDS.velo)

    complex_payment_enddate = models.DateTimeField(blank=True, null=True)
    complex_payment_hideon = models.DateTimeField(blank=True, null=True)
    complex_discount = models.SmallIntegerField(default=0)

    bill_series = models.CharField(max_length=20, blank=True, default='B')
    payment_channel = models.CharField(max_length=20, default='LKDF')

    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    # class path that will do processing tasks. Example for result creation.
    processing_class = models.CharField(max_length=100, blank=True)

    legacy_id = models.IntegerField(blank=True, null=True)

    sitetree = models.ForeignKey('sitetree.TreeItem', blank=True, null=True, on_delete=models.SET_NULL)

    is_in_menu = models.BooleanField(default=False)

    skin = models.CharField(max_length=50, blank=True)
    logo = ThumbnailerImageField(upload_to=_get_logo_upload_path, blank=True, )

    apply_image = ThumbnailerImageField(upload_to=_get_logo_upload_path, blank=True, )

    params = JSONField(blank=True, null=True)

    sms_text = models.CharField(max_length=255, blank=True)

    map_url = models.URLField(blank=True)

    frontpage_ordering = models.PositiveSmallIntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['competition_date', 'id']

    def __str__(self):
        return self.name

    def get_ids(self):
        if self.level == 2:
            return self.id, self.parent_id
        else:
            return self.id,

    def get_all_children_ids(self):
        if self.level == 2:
            return tuple(obj.id for obj in Competition.objects.filter(parent_id=self.parent_id))
        elif self.get_root().id == 1:
            return tuple(obj.id for obj in Competition.objects.filter(parent_id=self.id))
        else:
            return self.id,

    def get_distances(self):
        return Distance.objects.filter(competition_id__in=self.get_ids()).select_related('competition')

    def get_insurances(self):
        insurances = Insurance.objects.filter(competition_id__in=self.get_ids())
        if self.level == 1 and self.get_root().id == 1:
            insurances = insurances.filter(in_complex=True)
        return insurances.select_related('competition')

    @property
    def get_full_name(self):
        if self.level == 2:
            return '%s - %s' % (self.parent.name, self.name)
        else:
            return self.name

    def get_logo(self):
        if self.level == 2:
            return self.parent.logo
        else:
            return self.logo

    @property
    def competition_header(self):
        if not self.skin:
            return None
        return "core/competition_header/%s.html" % self.skin

    @property
    def is_past_due(self):
        if not self.competition_date and self.competition_date_till:
            if datetime.date.today() < self.competition_date_till:
                return False
            else:
                return True

        if datetime.date.today() >= self.competition_date:
            return True
        return False

    def get_random_image(self):
        from velo.gallery.models import Photo
        return Photo.objects.filter(album__competition__tree_id=self.tree_id, is_featured=True).order_by('?').first()

    def get_absolute_url(self):
        return reverse('competition:competition', args=[self.id])


@python_2_unicode_compatible
class Distance(TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition')
    name = models.CharField(max_length=100)
    distance_text = models.CharField(max_length=50, blank=True)
    distance_m = models.IntegerField(blank=True, null=True, help_text='Distance in meters')
    can_have_teams = models.BooleanField(default=True)
    have_results = models.BooleanField(default=True)

    profile_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    kind = models.CharField(max_length=1, blank=True)  # We need kind to map distances between competitions

    class Meta:
        order_with_respect_to = 'competition'

    def __str__(self):
        return self.name

    def get_participants(self, competition_ids):
        return self.participant_set.filter(competition_id__in=competition_ids)

    def get_teams(self):
        return self.team_set.all()


@python_2_unicode_compatible
class InsuranceCompany(models.Model):
    name = models.CharField(max_length=50)
    term = models.TextField(blank=True)

    terms_doc = models.FileField(upload_to=_get_insurance_term_upload_path, blank=True, )

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Insurance(StatusMixin, models.Model):
    insurance_company = models.ForeignKey(InsuranceCompany)
    competition = models.ForeignKey(Competition)
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    in_complex = models.BooleanField(default=True)
    complex_discount = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ('competition', 'price',)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class CustomSlug(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    birthday = models.DateField()
    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.slug


class Log(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, null=True, blank=True)
    action = models.CharField(max_length=50, blank=True)
    message = models.CharField(max_length=255, blank=True)
    params = JSONField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @classmethod
    def from_mailgun_request(cls, request, commit=True):
        email_code = request.POST.get('email_code')
        if not email_code:
            return None

        event_obj = cls()
        try:
            event_obj.content_object = MailgunEmail.objects.get(code=email_code)
        except MailgunEmail.DoesNotExist:
            return
        event_obj.action = request.POST.get('event')
        event_obj.message = request.POST.get('recipient', '')

        json_dict = {
            'dt': datetime.datetime.fromtimestamp(int(request.POST.get('timestamp'))),
            'ip': request.POST.get('ip', ''),
            'device_type': request.POST.get('device-type', ''),
            'user_agent': request.POST.get('user-agent', ''),
            'client_name': request.POST.get('client-name', ''),
            'client_os': request.POST.get('client-os', ''),
            'client_type': request.POST.get('client-type', ''),
            'description': request.POST.get('url', '')
        }

        if event_obj.action not in ('delivered', 'opened', 'clicked'):
            json_dict.update({
                'description': str(request.POST)
            })
        event_obj.params = json_dict

        if commit:
            event_obj.save()

        return event_obj


@python_2_unicode_compatible
class Map(models.Model):
    competition = models.ForeignKey(Competition)
    title = models.CharField(max_length=255)
    image = ThumbnailerImageField(upload_to=_get_map_upload_path)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ('competition', 'ordering',)

    def __str__(self):
        return self.title

    @property
    def parent_competition(self):
        return self.competition.parent
