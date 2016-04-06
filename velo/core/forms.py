# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from premailer import transform
from django.utils.encoding import force_bytes

from velo.core.models import User
from velo.core.widgets import ButtonWidget
from velo.marketing.models import MailgunEmail
from velo.velo.mixins.forms import CleanEmailMixin, RequestKwargModelFormMixin
from velo.core.tasks import send_email_confirmation, send_change_email_notification


class NewEmailForm(CleanEmailMixin, forms.Form):
    email = forms.EmailField(help_text=_('Please specify email address to associate account with.'))

    error_messages = {
        'duplicate_email': _("A user with that email address already exists."),
    }

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return super(NewEmailForm, self).clean_email()
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super(NewEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            Submit('change', _('Create Account'), css_class='btn-default'),
        )


class ChangeEmailForm(RequestKwargModelFormMixin, CleanEmailMixin, forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'password_wrong': _("Invalid password. Try again."),
    }

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            'password1',
            Submit('change', _('Change Email'), css_class='btn-default'),
        )

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if not self.request.user.check_password(password1):
            raise forms.ValidationError(
                self.error_messages['password_wrong'],
                code='password_wrong',
            )
        return password1

    def save(self, commit=True):
        prev_user = User.objects.get(id=self.instance.pk)
        user = super(ChangeEmailForm, self).save(commit=False)
        if prev_user.email != user.email:
            user.set_email_validation_code()
            user.email_status = User.EMAIL_NOT_VALIDATED
            if commit:
                send_change_email_notification.delay(user.id, prev_user.email)
                user.save()
                send_email_confirmation.delay(user.id)
        return user


class PasswordChangeFormCustom(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance', None)
        super(PasswordChangeFormCustom, self).__init__(user=self.user, *args, **kwargs)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        if self.user.has_usable_password():
            old_password = self.cleaned_data["old_password"]
            if not self.user.check_password(old_password):
                raise forms.ValidationError(
                    self.error_messages['password_incorrect'],
                    code='password_incorrect',
                )
            return old_password
        else:
            return self.user.password


class SetPasswordFormCustom(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordFormCustom, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-6'

        self.helper.layout = Layout(
            'new_password1',
            'new_password2',
            Submit('set_password', _('Set Password'), css_class='btn-default'),
        )


class AuthenticationFormCustom(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationFormCustom, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            'username',
            'password',
            Submit('log_in', _('Log in'), css_class='btn-default'),
        )


class ChangePasswordForm(RequestKwargModelFormMixin, PasswordChangeFormCustom):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = _('Passwords must be at least 10 characters in length.')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-6'

        if not self.user.has_usable_password():
            self.fields['old_password'].widget = forms.HiddenInput()
            self.fields['old_password'].required = False

        self.helper.layout = Layout(
            'old_password',
            'new_password1',
            'new_password2',
            Submit('change_password', _('Change Password'), css_class='btn-default'),
        )


class UserCreationForm(CleanEmailMixin, forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_email': _("A user with that email address already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = (
        "email", "first_name", "last_name", "country", "birthday", "city", "bike_brand", "phone_number", "send_email")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            'password1',
            'password2',
            'send_email',
            'first_name',
            'last_name',
            'birthday',
            'country',
            'city',
            'bike_brand',
            'phone_number',
            Submit('register', _('Register'), css_class='btn-default'),
        )

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return super(UserCreationForm, self).clean_email()
        raise forms.ValidationError(
            self.error_messages['duplicate_email'],
            code='duplicate_email',
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.last_login = timezone.now()
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    email = forms.CharField(required=False, widget=ButtonWidget())
    password = forms.CharField(required=False, widget=ButtonWidget())

    class Meta:
        model = User
        fields = ("first_name", "last_name", "country", "birthday", "city", "bike_brand", "phone_number", "send_email")

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update(
            {'href': reverse('accounts:email_change_view'), 'class': 'btn btn-primary'})
        self.fields['email'].widget.text = mark_safe(
            "%s <small>%s</small>" % (self.instance.email, ugettext('Change Email')))

        self.fields['password'].widget.attrs.update(
            {'href': reverse('accounts:password_change'), 'class': 'btn btn-primary'})
        self.fields['password'].widget.text = mark_safe("****** <small>%s</small>" % ugettext('Change Password'))

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            'password',

            'first_name',
            'last_name',
            'birthday',
            'country',
            'city',
            'bike_brand',
            'phone_number',
            'send_email',
            Submit('update_profile', _('Update Profile'), css_class='btn-default'),
        )


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, **kwargs):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        email = self.cleaned_data["email"]

        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except:
            return True

        # Make sure that no email is sent to a user that actually has
        # a password marked as unusable
        if not user.has_usable_password():
            return True

        c = {
            'email': user.email,
            'domain': settings.MY_DEFAULT_DOMAIN,
            'site_name': "velo.lv",
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
        }

        template = transform(render_to_string('registration/email/password_reset_email.html', c))
        template_txt = render_to_string('registration/email/password_reset_email.txt', c)

        subject = render_to_string(subject_template_name, c)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        email_data = {
            'em_to': email,
            'subject': subject,
            'html': template,
            'text': template_txt,
            'content_object': user,
        }
        mailgun = MailgunEmail.objects.create(**email_data)
