from allauth import app_settings
from allauth.account.utils import perform_login
from allauth.socialaccount.signals import pre_social_login
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser, PermissionsMixin, AbstractBaseUser, UserManager
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
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

from velo.velo.mixins.models import TimestampMixin, StatusMixin


def _get_insurance_term_upload_path(instance, filename):
    return os.path.join("insurance", str(uuid.uuid4()), filename)


def _get_logo_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("competition", "%02d_%s%s" % (instance.id, filename, ext))

def _get_profile_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    return os.path.join("profile", "%02d_%s%s" % (instance.id, filename, ext))


def _get_map_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = str(uuid.uuid4())
    if instance.competition_id:
        return os.path.join("competition", "maps", "%02d_%s%s" % (instance.competition_id, filename, ext))
    else:
        return os.path.join("competition", "maps", "%s%s" % (filename, ext))


def _get_gpx_upload_path(instance, filename):
    folder = str(uuid.uuid4())
    return os.path.join("competition", "gpx", folder, filename)


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

    class Meta:
        ordering = ("title", )


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_STATUS = XChoices((10, 'not_validated', _('Not yet validated')),
                           (20, 'bounced', _('Bounced')),
                           (40, 'validating', _('Validating')),
                           (50, 'valid', _('Valid')),
                           (-10, 'invalid', _('Invalid')), )

    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=30, blank=True)

    email = models.EmailField(_('Email Address'), unique=True)

    country = CountryField(_('Country'), blank=True, null=True, default="LV")
    ssn = models.CharField(_('Social Security Number'), max_length=12, blank=True)
    birthday = models.DateField(_('Birthday'), blank=True, null=True)
    city = models.ForeignKey('core.Choices', verbose_name=_('City'), related_name='+',
                             limit_choices_to={'kind': Choices.KINDS.city}, blank=True, null=True)
    bike_brand = models.ForeignKey('core.Choices', verbose_name=_('Bike Brand'), related_name='+',
                                   limit_choices_to={'kind': Choices.KINDS.bike_brand}, blank=True, null=True)
    phone_number = models.CharField(_('Phone Number'), max_length=60, blank=True)
    send_email = models.BooleanField(default=True, verbose_name=_('Send Email Newsletters'))

    full_name = models.CharField(_('Full Name'), max_length=60, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    image = ThumbnailerImageField(_("Profile Image"), blank=True, upload_to=_get_profile_upload_path)
    description = models.TextField(_("Description"), blank=True)

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
        return reverse("account:profile")

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


class Competition(MPTTModel):
    KINDS = XChoices((0, 'velo', _('Velo')),
                    (1, 'cross_country', _('Cross Country')), )

    name = models.CharField(max_length=100)
    alias = AutoSlugField(populate_from='name', always_update=True)
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
    logo = ThumbnailerImageField(upload_to=_get_logo_upload_path, blank=True,)
    logo_svg = models.FileField(upload_to=_get_logo_upload_path, blank=True)

    apply_image = ThumbnailerImageField(upload_to=_get_logo_upload_path, blank=True, )

    params = JSONField(blank=True, null=True)

    sms_text = models.CharField(max_length=255, blank=True)

    map_url = models.URLField(blank=True)

    frontpage_ordering = models.PositiveSmallIntegerField(default=0)

    description = models.TextField(blank=True)

    use_official_team_results = models.BooleanField(default=True)

    is_individual = models.BooleanField(default=False, help_text="If the stage should have individual start list")

    class MPTTMeta:
        order_insertion_by = ['competition_date', 'id']

    def __str__(self):
        return self.name

    @property
    def params_dict(self):
        if isinstance(self.params, dict):
            return self.params
        return json.loads(self.params)

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
        photo = Photo.objects.filter(album__competition__tree_id=self.tree_id, is_featured=False, album__gallery_date__year__in=[timezone.now().year, timezone.now().year - 1]).order_by('?').first()
        if photo:
            return photo
        else:
            return Photo.objects.get(id=73105)

    @property
    def is_application_active(self):
        if (self.complex_payment_enddate and self.complex_payment_enddate > timezone.now()) or self.price_set.active().exists():
            return True
        return False

    def get_absolute_url(self):
        return reverse('competition:competition', args=[self.id])


class Distance(TimestampMixin, models.Model):
    competition = models.ForeignKey('core.Competition')
    name = models.CharField(max_length=100)
    distance_text = models.CharField(max_length=50, blank=True)
    distance_m = models.IntegerField(blank=True, null=True, help_text='Distance in meters')
    can_have_teams = models.BooleanField(default=True)
    have_results = models.BooleanField(default=True)

    profile_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    kind = models.CharField(max_length=2, blank=True)  # We need kind to map distances between competitions

    class Meta:
        order_with_respect_to = 'competition'

    def __str__(self):
        return self.name

    def get_participants(self, competition_ids):
        return self.participant_set.filter(competition_id__in=competition_ids)

    def get_teams(self):
        return self.team_set.all()


class InsuranceCompany(models.Model):
    name = models.CharField(max_length=50)
    term = models.TextField(blank=True)
    description = models.TextField(blank=True)

    terms_doc = models.FileField(upload_to=_get_insurance_term_upload_path, blank=True, )

    def __str__(self):
        return self.name


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

    def set_message(self, message, commit=True):
        self.message = message
        if commit:
            self.save()

    def set_object(self, obj, commit=True):
        self.content_object = obj
        if commit:
            self.save()


class Map(models.Model):
    competition = models.ForeignKey(Competition)
    title = models.CharField(max_length=255)
    image = ThumbnailerImageField(upload_to=_get_map_upload_path)
    gpx = models.FileField(upload_to=_get_gpx_upload_path, blank=True, null=True)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ('competition', 'ordering',)

    def __str__(self):
        return self.title

    @property
    def parent_competition(self):
        return self.competition.parent


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    email_address = sociallogin.account.extra_data['email']
    users = User.objects.filter(email=email_address)
    if users:
        perform_login(request, users[0], email_verification=False)
