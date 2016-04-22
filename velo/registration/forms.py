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
        self.helper.include_media = False
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
    email2 = forms.EmailField(label=_('E-mail confirmation'), )

    class Meta:
        model = Application
        fields = ('email', 'can_send_newsletters')

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
        self.helper.form_class = "w100 js-form-participants"
        self.helper.include_media = False
        self.helper.layout = Layout(
            'team_search',
            'team_search_term',
            Div(
                Row(
                    Div(
                        css_class="col-xl-2 col-s-24",
                    ),
                    Div(
                        Div(
                            Div(
                                css_class="w100 bottom-margin--40"
                            ),
                            Div(
                                Row(
                                    Div(
                                        Field('email',
                                              css_class="input-field if--50 if--dark  js-placeholder-up",
                                              **{
                                                  "data-rule-required": True,
                                                  "data-rule-email": True,
                                                  "data-msg-required": str(_("This field is required.")),
                                                  "data-msg-email": str(_("Please enter valid email address!"))
                                              }),
                                        css_class='col-xl-12 col-m-24'
                                    ),
                                    Div(
                                        Field('email2',
                                              css_class="input-field if--50 if--dark  js-placeholder-up",
                                              **{
                                                  "data-rule-required": True,
                                                  "data-rule-email": True,
                                                  "data-rule-equalto": "#id_email",
                                                  "data-msg-required": str(_("This field is required.")),
                                                  "data-msg-email": str(_("Please enter valid email address!")),
                                                  "data-msg-equalto": str(_("Emails doesn't match")),
                                              }),

                                        css_class='col-xl-12 col-m-24'
                                    ),
                                    Div(
                                        Div(
                                            HTML(_("To this email address confirmation email will be sent.")),
                                            css_class="fs13 c-white--50 w100 bottom-margin--15",
                                        ),
                                        css_class='col-xl-12 col-m-24'
                                    ),
                                    Div(
                                        Div(
                                            "can_send_newsletters",
                                            css_class="input-wrap w100 bottom-margin--15",
                                        ),
                                        css_class='col-xl-12 col-m-24'
                                    ),
                                    css_class="row row--gutters-20",
                                ),
                                css_class="w100",
                            ),
                            css_class="inner no-padding--560"
                        ),
                        css_class="col-xl-20 col-s-24",
                    ),
                    Div(
                        css_class="col-xl-2 col-s-24",
                    ),
                    Div(
                        Div(
                            css_class="w100 bottom-margin--40",
                        ),
                        Div(

                            Div(
                                Row(
                                    Div(
                                        css_class="col-xl-2 col-s-24"
                                    ),
                                    Div(
                                        HTML(
                                            '{% load crispy_forms_tags %}{% crispy participant participant.form.helper %}'),

                                        # Add participant
                                        Div(
                                            Div(
                                                Div(
                                                    HTML(
                                                        '<svg class="icon"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/static/template/velo-2016/html/img/icons.svg#plus"></use></svg>'),
                                                    css_class="participant__number"
                                                ),
                                                Div(
                                                    HTML(str(_("Add Participant"))),
                                                    css_class="participant__name flex--1"
                                                ),

                                                css_class="participant__head flex wrap--nowrap direction--row justify--start align-items--center c-yellow add-new-row"
                                            ),
                                            css_class="w100 cursor--pointer bottom-margin--30 js-add-participant"
                                        ),

                                        css_class='col-xl-20 col-s-24'
                                    ),
                                    Div(
                                        css_class="col-xl-2 col-s-24"
                                    ),
                                ),
                                css_class="inner no-padding--560"
                            ),
                            css_class="w100",
                        ),
                        css_class="layouts-competition-register-background col-xl-24 border-top bgc-dblue"
                    ),

                    Div(
                        Div(
                            Row(
                                Div(css_class="col-xl-2 col-s-24"),
                                Div(
                                    Div(
                                        css_class="w100 bottom-margin--20"
                                    ),
                                    Div(
                                        Row(
                                            Div(
                                                css_class="col-xs-24 flex--1 fs14 fw700 uppercase bottom-margin--20  js-paricipant-count",
                                            ),
                                            Div(
                                                css_class="col-xs-24 fs14 fw700 uppercase bottom-margin--20",
                                            )
                                        ),
                                        css_class="w100"
                                    ),
                                    css_class="col-xl-20 col-s-24"
                                ),
                            ),
                            css_class="inner",
                        ),
                        css_class="layouts-competition-register-background col-xl-24 border-top bgc-dblue"
                    ),
                    Div(
                        Row(
                            Div(
                                css_class="col-xl-15 col-m-14 col-s-24"
                            ),
                            Div(Submit('submit_pay', _('Save & Pay'),
                                       css_class="btn btn--50 btn--blue btn--blue-hover btn--blue-active w100 flex--important wrap--nowrap justify--space-between align-items--center"),
                                css_class="col-xl-9 col-m-10 col-s-24") if self.instance.payment_status != Application.PAY_STATUS.payed and not self.instance.competition.is_past_due else Div(
                                css_class="col-xl-9 col-m-10 col-s-24"),
                        ),
                        css_class="col-xl-24 border-top border-bottom"
                    ),
                ),
                css_class="w100 border-right border-left no-border--560",
            )
        )


class ParticipantInlineForm(RequestKwargModelFormMixin, forms.ModelForm):
    insurance = forms.ChoiceField(required=False, choices=(), label=_('Insurance'))
    application = None

    class Meta:
        model = Participant
        fields = (
            'distance', 'first_name', 'last_name', 'country', 'ssn', 'birthday', 'gender', 'phone_number',
            'bike_brand2',
            'team_name', 'email')

    def clean_ssn(self):
        if self.cleaned_data.get('country') == 'LV':
            return self.cleaned_data.get('ssn', '').replace('-', '').replace(' ', '')
        else:
            return self.cleaned_data.get('ssn', '')

    def clean_insurance(self):
        insurance = self.cleaned_data.get('insurance', "")
        if insurance != "":
            return self.application.competition.get_insurances().filter(status=Insurance.STATUS_ACTIVE).get(id=insurance)
        return None

    def clean_birthday(self):
        ssn = self.cleaned_data.get('ssn')
        if self.cleaned_data.get('country') == 'LV' and ssn:
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

        cleaned_data = self.cleaned_data

        ssn = cleaned_data.get('ssn', '')
        country = cleaned_data.get('country')
        birthday = cleaned_data.get('birthday', '')
        distance = cleaned_data.get('distance', '')
        insurance = cleaned_data.get('insurance', None)

        if insurance:
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
            elif not ssn:
                self._errors.update({'ssn': [_("SSN is required."), ]})

        if birthday and distance and self.instance.application.payment_status == self.application.PAY_STATUS.not_payed:
            total = get_total(self.instance.application.competition, distance.id, birthday.year, insurance.id if insurance else None)
            if not total:
                self._errors.update({'distance': [_("This distance not available for this participant."), ]})

        return cleaned_data

    def save(self, commit=True):
        obj = super(ParticipantInlineForm, self).save(commit=False)

        obj.competition = self.application.competition
        obj.insurance = self.cleaned_data.get('insurance')

        if obj.birthday and obj.distance and self.application.payment_status == self.application.PAY_STATUS.not_payed:
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
            self.fields['insurance'].choices = [('', _("Select Insurance"))] + [(insurance.id, str(insurance)) for insurance
                                                                   in insurances]

            if self.instance.insurance_id:
                self.fields['insurance'].initial = self.instance.insurance_id
            elif not self.fields['insurance'].initial and insurances[0].price == 0.0:
                self.fields['insurance'].initial = insurances[0].id
        else:
            pass

        self.fields['distance'].choices = [('', _("Select Distance"))] + [(distance.id, str(distance)) for distance in
                                                              distances]

        if get_language() == 'lv':
            self.fields['country'].initial = 'LV'

        self.fields['team_name'].widget.attrs.update({'class': 'team-typeahead'})

        self.fields['team_name'].initial = competition.params_dict.get('default_team', "")
        self.fields['team_name'].help_text = competition.params_dict.get('default_team_help', "")

        self.fields['distance'].widget.attrs.update(
            {'data-url': str(reverse('payment:check_price', kwargs={'pk': self.application.competition_id}))})

        self.fields['distance'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['gender'].required = True
        self.fields['country'].required = True
        self.fields['birthday'].required = True

        self.fields['gender'].choices = Participant.GENDER_CHOICES
        self.fields['gender'].choices.insert(0, ('', _("Select Gender")), )

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.template = "wd_forms/whole_uni_formset.html"
        self.helper.layout = Layout(

            Div(
                Div(
                    Div(css_class="participant__number counter"),
                    Div(HTML(_("Participant")), css_class="participant__name flex--1"),
                    Div(HTML(
                        '<svg class="icon participant__cross"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/static/template/velo-2016/html/img/icons.svg#cross"></use></svg><div>%s</div>' % _(
                            "Remove")),
                        css_class="delete_button participant__remove flex wrap--nowrap direction--row justify--center align-items--center"),
                    Div(
                        Field('DELETE', ),
                        css_class="checkbox bottom-margin--15"
                    ),
                    css_class="participant__head flex wrap--nowrap direction--row justify--start align-items--center c-yellow"
                ),
                Div(
                    Div(
                        # Distance
                        Div(
                            Div(
                                Field(
                                    "distance",
                                    css_class="select-hide js-select",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--20"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),
                        # Country
                        Div(
                            Div(
                                Field(
                                    "country",
                                    css_class="select-hide js-select",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--20"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),
                        # Gender
                        Div(
                            Div(
                                Field(
                                    "gender",
                                    css_class="select-hide js-select",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--20"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # First Name
                        Div(
                            Div(
                                Field(
                                    "first_name",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Last Name
                        Div(
                            Div(
                                Field(
                                    "last_name",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Birthday
                        Div(
                            Div(
                                Field(
                                    "birthday",
                                    css_class="input-field if--50 if--dark js-placeholder-up dateinput",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Team Name
                        Div(
                            Div(
                                Field(
                                    "team_name",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Phone Number
                        Div(
                            Div(
                                Field(
                                    "phone_number",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Email
                        Div(
                            Div(
                                Field(
                                    "email",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # Bike Brand
                        Div(
                            Div(
                                Field(
                                    "bike_brand2",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        # insurance
                        Div(
                            Div(
                                Field(
                                    "insurance",
                                    css_class="select-hide js-select"
                                ),
                                css_class="input-wrap w100 bottom-margin--20"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ) if insurances else Div(),

                        # SSN
                        Div(
                            Div(
                                Field(
                                    "ssn",
                                    css_class="input-field if--50 if--dark js-placeholder-up",
                                    **{
                                        "data-rule-required": True,
                                        "data-msg-required": str(_("This field is required."))
                                    }
                                ),
                                css_class="input-wrap w100 bottom-margin--15"
                            ),
                            css_class="col-xl-8 col-m-12 col-s-24"
                        ),

                        'id',
                        Div(
                            Div(
                                css_class="fs14 fw700 c-white uppercase price"
                            ),
                            css_class="col-xl-24"
                        ),

                        css_class="row row--gutters-10"
                    ),

                    css_class="participant__form"
                ),
                css_class="participant bottom-margin--30 bgc-dgray js-participant"
            )
        )


class ParticipantInlineRestrictedForm(ParticipantInlineForm):
    def __init__(self, *args, **kwargs):
        super(ParticipantInlineRestrictedForm, self).__init__(*args, **kwargs)

        ro_fields = ('first_name', 'last_name', 'distance', 'insurance', 'birthday', 'ssn', 'country')

        for field in ro_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True

        self.helper.template = "base/velo_whole_uni_formset_noadd.html"

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
            'distance', 'first_name', 'last_name', 'country', 'ssn', 'birthday', 'gender', 'phone_number',
            'bike_brand2',
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

        self.fields['distance'].choices = [('', '------')] + [(distance.id, str(distance)) for distance in
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
        self.helper.include_media = False
        self.helper.template = "wd_forms/whole_uni_formset.html"
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
        self.helper.include_media = False
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
