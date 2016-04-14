# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, get_language

from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Fieldset, HTML, Column, Submit, Div, Field
import math
import uuid

from velo.core.models import Competition, Insurance
from velo.payment.utils import get_total
from velo.registration.models import Application, Participant, CompanyApplication, CompanyParticipant
from velo.registration.widgets import CompetitionWidget
from velo.velo.mixins.forms import RequestKwargModelFormMixin, GetClassNameMixin, CleanEmailMixin
from velo.velo.utils import bday_from_LV_SSN


class CompanyApplicationCreateForm(GetClassNameMixin, CleanEmailMixin, RequestKwargModelFormMixin, forms.ModelForm):
    change_public_url = forms.BooleanField(label=_("Reset public URL?"), help_text=_(
        'If you reset URL, then nobody will be able to access using previous URL.'), required=False)

    class Meta:
        model = CompanyApplication
        fields = ('competition', 'team_name', 'email', 'description',)

    def save(self, *args, **kwargs):
        if not self.instance.id:
            self.instance.created_by = self.request.user
            self.instance.status = 1  # Active
        self.instance.modified_by = self.request.user

        if self.cleaned_data.get('change_public_url', False):
            self.instance.code = str(uuid.uuid4())

        return super(CompanyApplicationCreateForm, self).save(*args, **kwargs)

    def clean_competition(self):
        competition = self.cleaned_data.get('competition')
        if self.instance.id:
            return self.instance.competition
        else:
            return competition

    def __init__(self, *args, **kwargs):
        super(CompanyApplicationCreateForm, self).__init__(*args, **kwargs)

        self.fields['email'].initial = self.request.user.email

        competitions = Competition.objects.filter(is_in_menu=True).exclude(competition_date__lt=timezone.now())
        self.fields['competition'].choices = [(c.id, c.get_full_name) for c in competitions]

        if self.instance.id:
            competitions = competitions.filter(id=self.instance.competition_id)
            if not competitions:
                c = self.instance.competition
                self.fields['competition'].choices += [(c.id, c.get_full_name), ]
            self.fields['competition'].widget.attrs['readonly'] = True
        else:
            self.fields['change_public_url'].widget = forms.HiddenInput()

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column(
                    'competition',
                    'email',
                    'team_name',
                    'description',
                    css_class='col-sm-6'
                ),
                Column(
                    'change_public_url',
                    css_class='col-sm-6'
                ),
            ),
            Row(
                Column(Submit('submit', _('Save')), css_class='col-sm-2'),
            ),
        )


class ApplicationCreateForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Application
        fields = ('competition',)
        widgets = {
            'competition': CompetitionWidget,
        }

    def __init__(self, *args, **kwargs):
        super(ApplicationCreateForm, self).__init__(*args, **kwargs)

        now = timezone.now()
        competitions = Competition.objects.filter(Q(complex_payment_enddate__gt=now) | Q(price__end_registering__gt=now,
                                                                                         price__start_registering__lte=now)).distinct().order_by(
            'complex_payment_enddate', 'competition_date')

        if not self.request.GET.get('all', None):
            competitions = competitions.exclude(complex_payment_hideon__lt=now)

        self.fields['competition'].choices = [(c.id, c) for c in competitions]

    def save(self, commit=True):
        object = super(ApplicationCreateForm, self).save(commit=False)
        if self.request.user.is_authenticated():
            object.email = self.request.user.email
            object.created_by = self.request.user
        if commit:
            object.save()
        return object


class ApplicationUpdateForm(GetClassNameMixin, CleanEmailMixin, RequestKwargModelFormMixin, forms.ModelForm):
    team_search = forms.CharField(widget=forms.HiddenInput)
    team_search_term = forms.CharField(widget=forms.HiddenInput)
    email2 = forms.EmailField(label=_('E-mail confirmation'),
                              help_text=_("Enter the same e-mail as above, for verification."))

    class Meta:
        model = Application
        fields = ('email',)

    class Media:
        js = ('js/jquery.formset.js', 'plugins/datepicker/bootstrap-datepicker.min.js',
              'plugins/jquery.maskedinput.js', 'plugins/mailgun_validator.js',
              'plugins/typeahead.js/typeahead.bundle.min.js',
              'plugins/handlebars-v3.0.1.js',)
        css = {
            'all': ('plugins/datepicker/datepicker.css',)
        }

    def clean_email2(self):
        email1 = self.cleaned_data.get('email', '')
        email2 = self.cleaned_data.get('email2', '')
        if email1 and email2 and email1 != email2:
            raise forms.ValidationError(
                _("The two email fields didn't match."),
                code='email_mismatch',
            )
        return email2

    def __init__(self, *args, **kwargs):
        super(ApplicationUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

        self.fields['team_search'].initial = reverse('competition:teams_json',
                                                     kwargs={'pk': self.instance.competition_id})
        self.fields['team_search_term'].initial = "{0}?search=%QUERY".format(
            reverse('competition:teams_json', kwargs={'pk': self.instance.competition_id}))

        self.fields['email2'].initial = self.instance.email

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column(
                    'email',
                    'team_search',
                    'team_search_term',
                    css_class='col-sm-6'
                ),
                Column(
                    'email2',
                    css_class='col-sm-6'
                ),
            ),
            Row(
                Column(
                    Fieldset(
                        _('Participants'),
                        HTML('{% load crispy_forms_tags %}{% crispy participant participant.form.helper %}'),
                    ),
                    css_class='col-xs-12'
                )
            ),
            Row(
                Column(Submit('submit_draft', _('Save')),
                       css_class='col-sm-2') if not self.instance.competition.is_past_due else Column(),
                Column(Submit('submit_pay', _('Save & Pay')),
                       css_class='col-sm-2 pull-right') if self.instance.payment_status != Application.PAY_STATUS_PAYED and not self.instance.competition.is_past_due else Column(),
            ),
        )


class ParticipantInlineForm(RequestKwargModelFormMixin, forms.ModelForm):
    insurance = forms.ChoiceField(required=False, choices=(), label=_('Insurance'))
    application = None

    class Meta:
        model = Participant
        fields = (
        'distance', 'first_name', 'last_name', 'country', 'ssn', 'birthday', 'gender', 'phone_number', 'bike_brand2',
        'team_name', 'email')

    def clean_ssn(self):
        if self.cleaned_data.get('country') == 'LV':
            return self.cleaned_data.get('ssn', '').replace('-', '').replace(' ', '')
        else:
            return ''

    def clean_birthday(self):
        if self.cleaned_data.get('country') == 'LV':
            return bday_from_LV_SSN(self.cleaned_data.get('ssn'))
        else:
            return self.cleaned_data.get('birthday')

    def clean_team_name(self):
        return self.cleaned_data.get('team_name').strip()

    def clean_bike_brand2(self):
        return self.cleaned_data.get('bike_brand2').strip()[:20]

    def clean_first_name(self):
        return self.cleaned_data.get('first_name').title()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name').title()

    def clean(self):
        if self.data.get('submit_draft'):
            return self.cleaned_data

        cleaned_data = self.cleaned_data

        ssn = cleaned_data.get('ssn', '')
        country = cleaned_data.get('country')
        birthday = cleaned_data.get('birthday', '')
        distance = cleaned_data.get('distance', '')
        insurance = cleaned_data.get('insurance', None)

        if country == 'LV':
            try:
                if not ssn or not len(ssn) == 11:
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
                checksum = 1
                for i in range(10):
                    checksum -= int(ssn[i]) * int("01060307091005080402"[i * 2:i * 2 + 2])
                if not int(checksum - math.floor(checksum / 11) * 11) == int(ssn[10]):
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
            except:
                self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})

        else:
            if not birthday:
                self._errors.update({'birthday': [_("Birthday is required."), ]})

        if birthday and distance and self.instance.application.payment_status == self.application.PAY_STATUS_NOT_PAYED:
            total = get_total(self.instance.application.competition, distance.id, birthday.year, insurance)
            if not total:
                self._errors.update({'distance': [_("This distance not available for this participant."), ]})

        return cleaned_data

    def save(self, commit=True):
        obj = super(ParticipantInlineForm, self).save(commit=False)

        obj.competition = self.application.competition
        obj.insurance_id = self.cleaned_data.get('insurance')

        if obj.birthday and obj.distance and self.application.payment_status == self.application.PAY_STATUS_NOT_PAYED:
            total = get_total(obj.competition, obj.distance_id, obj.birthday.year, obj.insurance_id)
            if total:
                obj.price = total.get('price_obj', None)
            else:
                obj.price = None

        if commit:
            obj.save()

        return obj

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super(ParticipantInlineForm, self).__init__(*args, **kwargs)

        competition = self.application.competition

        distances = competition.get_distances()
        insurances = competition.get_insurances().filter(status=Insurance.STATUS_ACTIVE)

        if insurances:
            self.fields['insurance'].choices = [('', '------')] + [(insurance.id, insurance.__unicode__()) for insurance
                                                                   in insurances]

            if self.instance.insurance_id:
                self.fields['insurance'].initial = self.instance.insurance_id
            elif not self.fields['insurance'].initial and insurances[0].price == 0.0:
                self.fields['insurance'].initial = insurances[0].id
        else:
            pass

        self.fields['distance'].choices = [('', '------')] + [(distance.id, distance.__unicode__()) for distance in
                                                              distances]

        if get_language() == 'lv':
            self.fields['country'].initial = 'LV'

        self.fields['country'].required = True
        self.fields['gender'].required = True

        self.fields['team_name'].widget.attrs.update({'class': 'team-typeahead'})

        self.fields['team_name'].initial = competition.params.get('default_team', "")
        self.fields['team_name'].help_text = competition.params.get('default_team_help', "")

        self.fields['distance'].widget.attrs.update(
            {'data-url': str(reverse('payment:check_price', kwargs={'pk': self.application.competition_id}))})

        if self.data.get('submit_draft'):
            self.fields['distance'].required = False
            self.fields['birthday'].required = False
            self.fields['first_name'].required = False
            self.fields['last_name'].required = False
            self.fields['gender'].required = False
            self.fields['country'].required = False
            self.fields['ssn'].required = False
        else:
            self.fields['distance'].required = True
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True
            self.fields['gender'].required = True
            self.fields['country'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "bootstrap/velo_whole_uni_formset.html"
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column('distance', css_class='col-xs-6 col-sm-4'),
                        Column('country', css_class='col-xs-6 col-sm-4'),
                        Column('gender', css_class='col-xs-6 col-sm-4'),
                    ),
                    Row(
                        Column('first_name', css_class='col-xs-6 col-sm-4'),
                        Column('last_name', css_class='col-xs-6 col-sm-4'),
                        Column('ssn', css_class='col-xs-6 col-sm-4'),
                        Column(Field('birthday', css_class='dateinput'), css_class='col-xs-6 col-sm-4'),
                    ),
                    Row(
                        Column('team_name', css_class='col-xs-6 col-sm-4'),
                        Column('phone_number', css_class='col-xs-6 col-sm-4'),
                        Column('email', css_class='col-xs-6 col-sm-4'),
                    ),
                    Row(
                        Column(FieldWithButtons('bike_brand2', StrictButton('<span class="caret"></span>',
                                                                            css_class='btn-default bike-brand-dropdown')),
                               css_class='col-xs-6 col-sm-4'),
                        Column('insurance', css_class='col-xs-6 col-sm-4 pull-right'),

                    ) if insurances else Row(Column(FieldWithButtons('bike_brand2',
                                                                     StrictButton('<span class="caret"></span>',
                                                                                  css_class='btn-default bike-brand-dropdown')),
                                                    css_class='col-xs-6 col-sm-4'), ),
                    'id',
                    Div(
                        Field('DELETE', ),
                        css_class='hidden',
                    ),
                    css_class='col-sm-9'
                ),
                Column(
                    Div(css_class='participant_calculation'),
                    css_class='col-sm-3'
                )
            ),
        )


class ParticipantInlineRestrictedForm(ParticipantInlineForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantInlineRestrictedForm, self).__init__(*args, **kwargs)

        ro_fields = ('first_name', 'last_name', 'distance', 'insurance', 'birthday', 'ssn', 'country')

        for field in ro_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True

        self.helper.template = "bootstrap/velo_whole_uni_formset_noadd.html"

    def clean_first_name(self):
        return self.instance.first_name

    def clean_last_name(self):
        return self.instance.last_name

    def clean_distance(self):
        return self.instance.distance

    def clean_insurance(self):
        return self.instance.insurance

    def clean_birthday(self):
        return self.instance.birthday

    def clean_ssn(self):
        return self.instance.ssn

    def clean_country(self):
        return self.instance.country


class ParticipantInlineFullyRestrictedForm(ParticipantInlineRestrictedForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantInlineFullyRestrictedForm, self).__init__(*args, **kwargs)
        ro_fields = ('gender', 'team_name', 'phone_number', 'email', 'bike_brand2')

        for field in ro_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True

    def clean_gender(self):
        return self.instance.gender

    def clean_team_name(self):
        return self.instance.team_name

    def clean_phone_number(self):
        return self.instance.phone_number

    def clean_email(self):
        return self.instance.email

    def clean_bike_brand2(self):
        return self.instance.bike_brand2


class CompanyParticipantInlineForm(RequestKwargModelFormMixin, forms.ModelForm):
    application = None

    class Meta:
        model = CompanyParticipant
        fields = (
        'distance', 'first_name', 'last_name', 'country', 'ssn', 'birthday', 'gender', 'phone_number', 'bike_brand2',
        'email')

    def clean_ssn(self):
        if self.cleaned_data.get('country') == 'LV':
            return self.cleaned_data.get('ssn', '').replace('-', '').replace(' ', '')
        else:
            return ''

    def clean_birthday(self):
        if self.cleaned_data.get('country') == 'LV':
            return bday_from_LV_SSN(self.cleaned_data.get('ssn'))
        else:
            return self.cleaned_data.get('birthday')

    def clean_bike_brand2(self):
        return self.cleaned_data.get('bike_brand2').strip()[:20]

    def clean_first_name(self):
        return self.cleaned_data.get('first_name').title()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name').title()

    def clean(self):
        cleaned_data = self.cleaned_data

        ssn = cleaned_data.get('ssn', '')
        country = cleaned_data.get('country')
        birthday = cleaned_data.get('birthday', '')
        distance = cleaned_data.get('distance', '')

        if country == 'LV':
            try:
                if not ssn or not len(ssn) == 11:
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
                checksum = 1
                for i in range(10):
                    checksum -= int(ssn[i]) * int("01060307091005080402"[i * 2:i * 2 + 2])
                if not int(checksum - math.floor(checksum / 11) * 11) == int(ssn[10]):
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
            except:
                self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})

        else:
            if not birthday:
                self._errors.update({'birthday': [_("Birthday is required."), ]})

        if birthday and distance:
            total = get_total(self.instance.application.competition, distance.id, birthday.year)
            if not total:
                self._errors.update({'distance': [_("This distance not available for this participant."), ]})

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        super(CompanyParticipantInlineForm, self).__init__(*args, **kwargs)

        competition = self.application.competition

        distances = competition.get_distances()

        self.fields['distance'].choices = [('', '------')] + [(distance.id, distance.__unicode__()) for distance in
                                                              distances]

        if get_language() == 'lv':
            self.fields['country'].initial = 'LV'

        self.fields['country'].required = True
        self.fields['gender'].required = True

        self.fields['distance'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = True
        self.fields['country'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "bootstrap/velo_whole_uni_formset.html"
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column('distance', css_class='col-xs-6 col-sm-4'),
                        Column('country', css_class='col-xs-6 col-sm-4'),
                        Column('gender', css_class='col-xs-6 col-sm-4'),
                    ),
                    Row(
                        Column('first_name', css_class='col-xs-6 col-sm-4'),
                        Column('last_name', css_class='col-xs-6 col-sm-4'),
                        Column('ssn', css_class='col-xs-6 col-sm-4'),
                        Column(Field('birthday', css_class='dateinput'), css_class='col-xs-6 col-sm-4'),
                    ),
                    Row(
                        Column('phone_number', css_class='col-xs-6 col-sm-4'),
                        Column('email', css_class='col-xs-6 col-sm-4'),
                        Column(FieldWithButtons('bike_brand2', StrictButton('<span class="caret"></span>',
                                                                            css_class='btn-default bike-brand-dropdown')),
                               css_class='col-xs-6 col-sm-4'),
                    ),
                    'id',
                    Div(
                        Field('DELETE', ),
                        css_class='hidden',
                    ),
                    css_class='col-sm-9'
                ),
            ),
        )


class CompanyApplicationEmptyForm(GetClassNameMixin, CleanEmailMixin, RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = CompanyApplication
        fields = ()

    class Media:
        js = ('js/jquery.formset.js', 'plugins/datepicker/bootstrap-datepicker.min.js',
              'plugins/jquery.maskedinput.js', 'plugins/mailgun_validator.js',
              'plugins/typeahead.js/typeahead.bundle.min.js',
              'plugins/handlebars-v3.0.1.js',)
        css = {
            'all': ('plugins/datepicker/datepicker.css',)
        }

    def __init__(self, *args, **kwargs):
        super(CompanyApplicationEmptyForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        _('New Company Participants'),
                        HTML('{% load crispy_forms_tags %}{% crispy participant participant.form.helper %}'),
                    ),
                    css_class='col-xs-12'
                )
            ),
            Row(
                Column(Submit('submit', _('Save')), css_class='col-sm-2 pull-right'),
            ),
        )

    def get_app_label(self):
        return "registration/application"
