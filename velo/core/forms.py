# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.forms import Select
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django_countries.data import COUNTRIES

from velo.core.models import User, Choices
from velo.core.widgets import ButtonWidget


# NEW
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=False)
    last_name = forms.CharField(max_length=30, label=_('Last Name'), required=False)
    send_email = forms.BooleanField(label=_('I want to receive newsletters'), required=False)
    birthday_day = forms.IntegerField(label=_('Birthday'), required=False)
    birthday_month = forms.IntegerField(label=_('Birthday'), required=False)
    birthday_year = forms.IntegerField(label=_('Birthday'), required=False)
    country = forms.ChoiceField(label=_('Country'), required=False, choices=sorted(COUNTRIES.items(), key=lambda tup: tup[1]))
    city = forms.ModelChoiceField(Choices.objects.filter(kind=Choices.KINDS.city), required=False, label=_('City'), empty_label=_("City"))
    bike_brand = forms.ModelChoiceField(Choices.objects.filter(kind=Choices.KINDS.bike_brand), required=False, label=_('Bike Brand'), empty_label=_("Bike Brand"))
    phone_number = forms.CharField(required=False, label=_('Phone number'))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['country'].initial = 'LV'

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.send_email = self.cleaned_data['send_email']
        user.country = self.cleaned_data['country']
        user.city = self.cleaned_data['city']
        user.bike_brand = self.cleaned_data['bike_brand']
        user.phone_number = self.cleaned_data['phone_number']
        try:
            user.birthday = datetime.date(self.cleaned_data['birthday_year'], self.cleaned_data['birthday_month'], self.cleaned_data['birthday_day'])
        except:
            print("WRONG DATE")

        user.save()


# Is this needed?
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
