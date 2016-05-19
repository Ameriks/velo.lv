# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.db.models import Count
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import StrictButton, FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, HTML, Div, Field
# from django_select2 import AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget
import math
import requests

from velo.core.models import Competition, Distance, Insurance
# from velo.manager.select2_fields import NumberChoices, UserChoices, NumberChoice, ParticipantChoices, NumberAllChoices
from velo.manager.select2_fields import NumberChoices, UserChoices, NumberAllChoices, ParticipantChoices
from velo.manager.tasks import update_results_for_participant
from velo.manager.widgets import PhotoPickWidget
from velo.news.models import News
from velo.payment.models import ActivePaymentChannel, Price
from velo.payment.utils import create_application_invoice
from velo.registration.models import Participant, Number, Application, PreNumberAssign, ChangedName
from velo.results.models import DistanceAdmin, Result, LapResult, UrlSync
from velo.team.forms import MemberInlineForm, TeamForm
from velo.team.models import Member, Team
from velo.velo.mixins.forms import RequestKwargModelFormMixin, CleanEmailMixin, CleanSSNMixin
from velo.velo.utils import load_class


class InvoiceCreateForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = Application
        fields = ('company_name', 'company_vat', 'company_regnr', 'company_address', 'company_juridical_address', )


    def save(self, commit=True):
        instance = super(InvoiceCreateForm, self).save(commit=False)

        try:
            active_payment_type = ActivePaymentChannel.objects.filter(competition=instance.competition, payment_channel__is_bill=True)[:1]
            if active_payment_type:
                instance.external_invoice_code, instance.external_invoice_nr = create_application_invoice(instance, active_payment_type[0], action="approve")
            else:
                self._errors['company_name'] = self.error_class([_("There is not created invoice link for this competition.")])
        except:
            self._errors['company_name'] = self.error_class([_("Error in connection with bank. Try again later.")])

        if self.request:
            instance.updated_by = self.request.user
        if instance.payment_status < Application.PAY_STATUS.waiting:
            instance.payment_status = Application.PAY_STATUS.waiting

        if not bool(self.errors) and commit:
            instance.save()

        return instance

    def clean(self):
        super(InvoiceCreateForm, self).clean()
        try:
            active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))
        except:
            active_payment_type = None
        if active_payment_type and active_payment_type.payment_channel.is_bill:
            if self.cleaned_data.get('company_name', '') == '':
                self._errors.update({'company_name': [_("Company Name required."), ]})
            if self.cleaned_data.get('company_regnr', '') == '':
                self._errors.update({'company_regnr': [_("Company registration number required."), ]})
            if self.cleaned_data.get('company_address', '') == '':
                self._errors.update({'company_address': [_("Company Address required."), ]})
            if self.cleaned_data.get('company_juridical_address', '') == '':
                self._errors.update({'company_juridical_address': [_("Company Juridical Address required."), ]})

        return self.cleaned_data


    def __init__(self, *args, **kwargs):
        super(InvoiceCreateForm, self).__init__(*args, **kwargs)

        self.fields['company_name'].required = True
        self.fields['company_regnr'].required = True
        self.fields['company_address'].required = True
        self.fields['company_juridical_address'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.
        self.helper.layout = Layout(
            Row(
                Column(
                    Fieldset(
                        'Izveidot jaunu rēķinu?',
                        'company_name',
                        'company_vat',
                        'company_regnr',
                        'company_address',
                        'company_juridical_address',
                        css_class='invoice_fields',
                    ),
                    css_class='col-sm-4 pull-right',
                )
            ),
        )



class NumberListSearchForm(RequestKwargModelFormMixin, forms.Form):
    distance = forms.ChoiceField(choices=(), required=False)
    group = forms.ChoiceField(choices=(), required=False)
    number = forms.CharField(required=False)
    status = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)
        super(NumberListSearchForm, self).__init__(*args, **kwargs)

        self.fields['distance'].choices = [('', '------')] + [(obj.id, str(obj)) for obj in competition.get_distances()]
        self.fields['group'].choices = [('', '------')] + [(obj.get('group'), obj.get('group')) for obj in Number.objects.filter(competition_id__in=competition.get_ids()).exclude(group='').values("group").annotate(Count("id")).order_by()]
        self.fields['status'].choices = (('', '------'), ) + Number.STATUSES

        self.fields['distance'].initial = self.request.GET.get('distance', '')
        self.fields['group'].initial = self.request.GET.get('group', '')
        self.fields['status'].initial = self.request.GET.get('status', '')
        self.fields['number'].initial = self.request.GET.get('number', '')

        self.helper = FormHelper()
        self.helper.form_class = 'participant-search-form'
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(
                Div(
                    'distance',
                    css_class='col-xs-2',
                ),
                Div(
                    'group',
                    css_class='col-xs-2',
                ),
                Div(
                    'number',
                    css_class='col-xs-2',
                ),
                Div(
                    'status',
                    css_class='col-xs-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span> Meklēt', css_class="btn-u btn-u-blue", type="submit"),
                        css_class="buttons",
                    ),
                    css_class='col-xs-4',
                ),
            ),
        )


class ResultListSearchForm(RequestKwargModelFormMixin, forms.Form):
    distance = forms.ChoiceField(choices=(), required=False)
    group = forms.ChoiceField(choices=(), required=False)
    search = forms.CharField(required=False)
    number = forms.CharField(required=False)
    status = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)
        super(ResultListSearchForm, self).__init__(*args, **kwargs)

        self.fields['distance'].choices = [('', '------')] + [(obj.id, str(obj)) for obj in competition.get_distances()]
        self.fields['group'].choices = [('', '------')] + [(obj.get('group'), obj.get('group')) for obj in Participant.objects.exclude(group='').values("group").annotate(Count("id")).order_by()]
        self.fields['status'].choices = [('', '------')] + [(obj.get('status'), obj.get('status')) for obj in Result.objects.filter(competition=competition).exclude(status='').values("status").annotate(Count("id")).order_by()]

        self.fields['distance'].initial = self.request.GET.get('distance', '')
        self.fields['group'].initial = self.request.GET.get('group', '')
        self.fields['search'].initial = self.request.GET.get('search', '')
        self.fields['status'].initial = self.request.GET.get('status', '')
        self.fields['number'].initial = self.request.GET.get('number', '')

        self.helper = FormHelper()
        self.helper.form_class = 'participant-search-form'
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(
                Div(
                    'distance',
                    css_class='col-xs-2',
                ),
                Div(
                    'group',
                    css_class='col-xs-2',
                ),
                Div(
                    'search',
                    css_class='col-xs-2',
                ),
                Div(
                    'number',
                    css_class='col-xs-2',
                ),
                Div(
                    'status',
                    css_class='col-xs-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span> Meklēt', css_class="btn-u btn-u-blue", type="submit"),
                        css_class="buttons",
                    ),
                    css_class='col-xs-4',
                ),
            ),
        )


class ApplicationListSearchForm(RequestKwargModelFormMixin, forms.Form):
    search = forms.CharField(required=False)
    status = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)
        super(ApplicationListSearchForm, self).__init__(*args, **kwargs)

        self.fields['status'].choices = [('', '------'), (-10, 'Atcelts'), (0, 'Nav apmaksāts'), (10, 'Gaida maksājumu'), (20, 'Apmaksāts')]

        self.fields['status'].initial = self.request.session['manager__application_list__status'] = self.request.GET.get('status', self.request.session.get('manager__application_list__status', ''))
        self.fields['search'].initial = self.request.session['manager__participant_list__search'] = self.request.GET.get('search', self.request.session.get('manager__participant_list__search', ''))


        self.helper = FormHelper()
        self.helper.form_class = 'participant-search-form'
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(
                Div(
                    'search',
                    css_class='col-xs-4',
                ),
                Div(
                    'status',
                    css_class='col-xs-4',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span> Meklēt', css_class="btn-u btn-u-blue", type="submit"),
                        css_class="buttons",
                    ),
                    css_class='col-xs-4',
                ),
            ),
        )


class ParticipantListSearchForm(RequestKwargModelFormMixin, forms.Form):
    distance = forms.ChoiceField(choices=(), required=False)
    group = forms.ChoiceField(choices=(), required=False)
    search = forms.CharField(required=False)
    status = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwargs):
        competition = kwargs.pop('competition', None)
        super(ParticipantListSearchForm, self).__init__(*args, **kwargs)

        self.fields['distance'].choices = [('', '------')] + [(obj.id, str(obj)) for obj in competition.get_distances()]
        self.fields['group'].choices = [('', '------')] + [(obj.get('group'), obj.get('group')) for obj in Participant.objects.filter(competition=competition).exclude(group='').values("group").annotate(Count("id")).order_by()]
        self.fields['status'].choices = [('', '------'), (0, 'Nepiedalās'), (1, 'Piedalās')]

        self.fields['distance'].initial = self.request.session['manager__participant_list__distance'] = self.request.GET.get('distance', self.request.session.get('manager__participant_list__distance', ''))
        self.fields['group'].initial = self.request.session['manager__participant_list__group'] = self.request.GET.get('group', self.request.session.get('manager__participant_list__group', ''))
        self.fields['search'].initial = self.request.session['manager__participant_list__search'] = self.request.GET.get('search', self.request.session.get('manager__participant_list__search', ''))
        self.fields['status'].initial = self.request.session['manager__participant_list__status'] = self.request.GET.get('status', self.request.session.get('manager__participant_list__status', ''))


        self.helper = FormHelper()
        self.helper.form_class = 'participant-search-form'
        self.helper.form_tag = True
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Row(
                Div(
                    'distance',
                    css_class='col-xs-2',
                ),
                Div(
                    'group',
                    css_class='col-xs-2',
                ),
                Div(
                    'search',
                    css_class='col-xs-2',
                ),
                Div(
                    'status',
                    css_class='col-xs-2',
                ),
                Div(
                    Div(
                        StrictButton('<span data-icon="&#xe090;"></span> Meklēt', css_class="btn-u btn-u-blue", type="submit"),
                        css_class="buttons",
                    ),
                    css_class='col-xs-4',
                ),
            ),
        )


class DistanceAdminForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = DistanceAdmin
        fields = ('distance', 'zero', 'distance_actual')


    def __init__(self, *args, **kwargs):
        super(DistanceAdminForm, self).__init__(*args, **kwargs)

        self.fields['distance'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            'distance', 'zero', 'distance_actual',
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
            ),
        )


class NumberForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Number
        fields = ('distance', 'number', 'number_text', 'participant_slug')


    def __init__(self, *args, **kwargs):
        super(NumberForm, self).__init__(*args, **kwargs)

        self.fields['distance'].widget.attrs['readonly'] = True
        self.fields['number'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            'distance', 'number', 'number_text', 'participant_slug',
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
            ),
        )


class ManageTeamMemberForm(MemberInlineForm):
    class Meta:
        model = Member
        fields = ('country', 'ssn', 'first_name', 'last_name', 'id', 'birthday', 'gender', 'status' )


    def __init__(self, *args, **kwargs):
        super(ManageTeamMemberForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "wd_forms/whole_uni_formset.html"
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column('first_name', css_class='col-xs-6 col-sm-2'),
                        Column('last_name', css_class='col-xs-6 col-sm-3'),
                        Column('gender', css_class='col-xs-6 col-sm-2'),
                        Column('country', css_class='col-xs-6 col-sm-2'),
                        Column('ssn', css_class='col-xs-6 col-sm-3'),
                        Column('birthday', css_class='col-xs-6 col-sm-3'),
                        Column('status', css_class='col-xs-6 col-sm-3 pull-right'),
                    ),
                    'id',
                    Div(
                        Field('DELETE',),
                        css_class='hidden',
                    ),
                    css_class='col-sm-12'
                ),
            ),
        )


class ManageLapResultForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = LapResult
        fields = ('index', 'time', )
        widgets = {
            'time': forms.TimeInput(format='%H:%M:%S.%f'),
        }

    def __init__(self, *args, **kwargs):
        super(ManageLapResultForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "wd_forms/whole_uni_formset.html"
        self.helper.layout = Layout(
            Row(
                Column('index', css_class='col-xs-6 col-sm-4'),
                Column('time', css_class='col-xs-6 col-sm-4'),
            ),
        )


class ManageTeamForm(TeamForm):
    class Meta:
        model = Team
        fields = (
        'distance', 'title', 'description', 'img', 'shirt_image', 'country', 'contact_person', 'email', 'phone_number',
        'management_info', 'is_featured', 'status')

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column(
                    'distance',
                    'title',
                    'country',
                    'is_featured',
                    'description',
                    'img',
                    css_class='col-sm-6'
                ),
                Column(
                    'contact_person',
                    'email',
                    'phone_number',
                    'status',
                    'management_info',
                    'shirt_image',
                    css_class='col-sm-6'
                ),
            ),
            Row(
                Column(
                    Fieldset(
                        'Dalībnieki',
                        HTML('{% load crispy_forms_tags %}{% crispy member member.form.helper "bootstrap3" %}'),
                    ),
                    css_class='col-xs-12'
                ),
                Column(Submit('submit', _('Save')), css_class='col-sm-12'),
            ),
        )



class ParticipantIneseCreateForm(RequestKwargModelFormMixin, CleanSSNMixin, CleanEmailMixin, forms.ModelForm):
    class Meta:
        model = Participant
        fields = (
            'competition', 'distance', 'first_name', 'last_name', 'birthday', 'gender', 'is_participating',
            'ssn', 'phone_number', 'email',  'country', 'team_name',
            'city', 'bike_brand2', 'occupation', 'price', 'insurance', 'registration_dt',
        )

    class Media:
        js = ('plugins/jquery.maskedinput.js',
              'plugins/mailgun_validator.js',
              'plugins/typeahead.js/typeahead.bundle.min.js',
              'plugins/handlebars-v3.0.1.js',
              'plugins/moment.min.js',
              'plugins/datetimepicker/bootstrap-datetimepicker.min.js',
              'coffee/manager/participant_add.js')
        css = {
            'all': (
              'plugins/datetimepicker/bootstrap-datetimepicker.min.css',
            ),
        }

    def clean(self):
        super(ParticipantIneseCreateForm, self).clean()

        distance = self.cleaned_data.get('distance')
        gender = self.cleaned_data.get('gender')
        birthday = self.cleaned_data.get('birthday')

        if distance and gender and birthday:

            try:
                competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
                if competition.processing_class:
                    class_ = load_class(competition.processing_class)
                    processing_class = class_(competition.id)
                    processing_class.assign_group(distance.id, gender, birthday)

            except:
                self._errors.update({'distance': ['Dalībnieks nevar startēt šajā distancē.', ]})

        return self.cleaned_data


    def __init__(self, *args, **kwargs):
        super(ParticipantIneseCreateForm, self).__init__(*args, **kwargs)

        competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
        competition_ids = competition.get_ids()

        distances = Distance.objects.filter(competition_id__in=competition_ids)
        insurances = Insurance.objects.filter(competition_id__in=competition_ids)
        competitions = Competition.objects.filter(parent_id=competition.parent_id)
        if competition.level == 2:
            comp_choices = [(competition.parent.id, 'Visa sezona')]
            comp_choices += [(c.id, str(c)) for c in competitions]
        else:
            comp_choices = [(competition.id, str(competition))]


        if competition.get_root().id == 1 and competition.level == 1:
            comps = competition.get_descendants()
            prices_obj = comps[0].price_set.all()
            prices = [(price.id, "%s€- %s" % (str(price.price * comps.count() * (100 - competition.complex_discount) / 100), price.distance)) for price in prices_obj]
        else:
            prices = [(str(price.id), "%s€ - %s" % (str(price.price), price.distance)) for price in competition.price_set.all()]

        self.fields['price'].choices = [(u'', u'------'), ] + prices
        self.fields['insurance'].choices = [('', '------')] + [(insurance.id, str(insurance)) for insurance in insurances]

        self.fields['competition'].choices = comp_choices

        self.fields['distance'].choices = [('', '------')] + [(distance.id, str(distance)) for distance in distances]

        self.fields['competition'].initial = self.request_kwargs.get('pk')
        self.fields['country'].initial = 'LV'
        self.fields['is_participating'].initial = True

        self.fields['gender'].required = True
        self.fields['country'].required = True
        self.fields['birthday'].required = True
        self.fields['distance'].required = True

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'smaller'
        self.helper.layout = Layout(
            Fieldset(
                'Add Participant',
                Row(
                    Column('ssn', css_class='col-sm-3'),
                    Column('birthday', css_class='col-sm-3'),
                    Column('team_name', css_class='col-sm-3'),
                ),
                Row(
                    Column('competition', css_class='col-sm-3'),
                    Column('distance', css_class='col-sm-3'),
                    Column('country', css_class='col-sm-3'),
                ),
                Row(
                    Column('first_name', css_class='col-sm-3'),
                    Column('last_name', css_class='col-sm-3'),
                    Column('gender', css_class='col-sm-3'),

                ),
                Row(
                    Column('phone_number', css_class='col-sm-3'),
                    Column('email', css_class='col-sm-3'),
                    Column('is_participating', css_class='col-sm-3'),
                ),
                Row(
                    Column('price', css_class='col-sm-3'),
                    Column('insurance', css_class='col-sm-3'),

                ),

                Row(
                    Column('city', css_class='col-sm-3'),
                    Column('bike_brand2', css_class='col-sm-3'),
                    Column('occupation', css_class='col-sm-3'),
                ),
                Row(
                    Column(Field('registration_dt', css_class='datetime555'), css_class='col-sm-3'),
                ),
            ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
                Column(Submit('submit_and_next', 'Saglabāt un pievienot nākamo'), css_class='col-sm-4 pull-right'),
                Column(Submit('submit_and_continue', 'Saglabāt un turpināt labot'), css_class='col-sm-4 pull-right'),
            ),


        )





class ParticipantCreateForm(RequestKwargModelFormMixin, CleanSSNMixin, CleanEmailMixin, forms.ModelForm):
    # primary_number = NumberChoice(required=False, widget=AutoHeavySelect2Widget(select2_options={
    #     'ajax': {
    #         'dataType': 'json',
    #         'quietMillis': 100,
    #         'data': '*START*django_select2.runInContextHelper(get_participant_params, selector)*END*',
    #         'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
    #     },
    #     "minimumResultsForSearch": 0,
    #     "minimumInputLength": 0,
    #     "closeOnSelect": True
    # }))
    class Meta:
        model = Participant
        widgets = {
            'is_participating': forms.HiddenInput,
            'primary_number': NumberChoices,
        }
        fields = (
            'competition', 'distance', 'first_name', 'last_name', 'birthday', 'gender', 'is_participating',
            'ssn', 'phone_number', 'email',  'country', 'team_name',
            'primary_number')

    class Media:
        js = ('plugins/jquery.maskedinput.js', 'plugins/mailgun_validator.js')


    def clean(self):
        super(ParticipantCreateForm, self).clean()

        distance = self.cleaned_data.get('distance')
        gender = self.cleaned_data.get('gender')
        birthday = self.cleaned_data.get('birthday')

        if distance and gender and birthday:

            try:
                competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
                if competition.processing_class:
                    class_ = load_class(competition.processing_class)
                    processing_class = class_(competition.id)
                    processing_class.assign_group(distance.id, gender, birthday)

            except:
                self._errors.update({'distance': ['Dalībnieks nevar startēt šajā distancē.', ]})

        return self.cleaned_data




    def save(self, commit=True):
        # If this is new record, then create slug.
        if not self.instance.id:
            self.instance.set_slug()

        if commit:
            # Process numbers. Remove link to old number. assign link to new number. Set new primary number.
            number = self.cleaned_data.get('primary_number')
            if number:
                number.participant_slug = self.instance.slug
                number.save()

        return super(ParticipantCreateForm, self).save(commit)


    def __init__(self, *args, **kwargs):
        super(ParticipantCreateForm, self).__init__(*args, **kwargs)

        competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
        competition_ids = competition.get_ids()

        distances = Distance.objects.filter(competition_id__in=competition_ids)

        competitions = Competition.objects.filter(parent_id=competition.parent_id)
        if competition.level == 2:
            comp_choices = [(competition.parent.id, 'Visa sezona')]
            comp_choices += [(c.id, str(c)) for c in competitions]
        else:
            comp_choices = [(competition.id, str(competition))]
        self.fields['competition'].choices = comp_choices

        self.fields['distance'].choices = [('', '------')] + [(distance.id, str(distance)) for distance in distances]

        self.fields['competition'].initial = self.request_kwargs.get('pk')
        self.fields['country'].initial = 'LV'
        self.fields['is_participating'].initial = True

        self.fields['gender'].required = True
        self.fields['country'].required = True
        self.fields['birthday'].required = True
        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['distance'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                'Quick Add',
                Row(
                    Column('competition', css_class='col-sm-3'),
                ),
                Row(
                    Column('primary_number', css_class='col-sm-3'),
                    Column('distance', css_class='col-sm-3'),
                    Column('country', css_class='col-sm-3'),
                ),
                Row(
                    Column('first_name', css_class='col-sm-3'),
                    Column('last_name', css_class='col-sm-3'),
                    Column('gender', css_class='col-sm-3'),

                ),
                Row(
                    Column('ssn', css_class='col-sm-3'),
                    Column('birthday', css_class='col-sm-3'),
                    Column('team_name', css_class='col-sm-3'),
                ),
                Row(
                    Column('phone_number', css_class='col-sm-3'),
                    Column('email', css_class='col-sm-3'),
                )
            ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
                Column(Submit('submit_and_next', 'Saglabāt un pievienot nākamo'), css_class='col-sm-4 pull-right'),
                Column(Submit('submit_and_continue', 'Saglabāt un turpināt labot'), css_class='col-sm-4 pull-right'),
            ),


        )



class ParticipantForm(RequestKwargModelFormMixin, forms.ModelForm):
    numbers = forms.MultipleChoiceField(widget=NumberChoices, required=False, choices=())

    reset_group = False

    class Meta:
        model = Participant
        fields = (
            'competition', 'distance', 'first_name', 'last_name', 'birthday', 'gender', 'slug', 'is_participating', 'is_paying', 'insurance',
            'team', 'team_name', 'ssn', 'phone_number', 'email', 'send_email', 'send_sms', 'country', 'city',
            'bike_brand2', 'occupation', 'where_heard', 'group', 'registrant', 'price', 'comment', 'registration_dt')
        widgets = {
            'registrant': UserChoices,
        }

    def clean_email(self):
        value = self.cleaned_data.get('email', '')
        if len(value) > 0:
            resp = requests.get('https://api.mailgun.net/v2/address/validate',
                                params={'api_key': 'pubkey-7049tobos-x721ipc8b3dp68qzxo3ri5', 'address': value}).json()
            if not resp.get('is_valid', False):
                msg = 'Invalid email address.'
                if resp.get('did_you_mean'):
                    msg = msg + ' ' + 'Did you mean:' + resp.get('did_you_mean')
                raise forms.ValidationError(msg, code='invalid_email')
        return value

    def clean_ssn(self):
        value = self.cleaned_data['ssn'].replace("-", "").strip()
        if value:
            try:
                if not value or not len(value) == 11:
                    raise forms.ValidationError(_("Invalid Social Security Number."))
                checksum = 1
                for i in range(10):
                    checksum = checksum - int(value[i]) * int("01060307091005080402"[i * 2:i * 2 + 2])
                if not int(checksum - math.floor(checksum / 11) * 11) == int(value[10]):
                    raise forms.ValidationError(_("Invalid Social Security Number."))
            except:
                raise forms.ValidationError(_("Invalid Social Security Number."))
                return None
        return value


    def save(self, commit=True):
        # If this is new record, then create slug.
        if not self.instance.id:
            self.instance.set_slug()

        if self.reset_group:
            self.instance.group = ''

        if commit:
            # Process numbers. Remove link to old number. assign link to new number. Set new primary number.
            numbers = self.cleaned_data.get('numbers')
            self.instance.numbers().exclude(id__in=numbers).update(participant_slug='cancelled-%s' % self.instance.slug)
            Number.objects.filter(id__in=numbers).update(participant_slug=self.instance.slug)
            if not numbers:
                self.instance.primary_number = None
            else:
                self.instance.primary_number = Number.objects.filter(id__in=numbers).order_by('-number')[0]


        obj = super(ParticipantForm, self).save(commit)

        # create result update task for participant
        print('recalculate?')
        # TODO: Need to optimize place and point recalculation.
        update_results_for_participant(obj.id)

        return obj

    def clean_slug(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.slug
        else:
            return self.cleaned_data['slug']

    def clean_competition(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and self.instance.primary_number_id:
            return instance.competition
        else:
            return self.cleaned_data['competition']

    # TODO: enable restriction to change distance for SEB competitions (that have multiple stages), but allow where are no stages
    def clean_distance(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            if self.instance.primary_number_id:
                return instance.distance
            elif instance.distance != self.cleaned_data['distance']:
                self.reset_group = True
        return self.cleaned_data['distance']

    def __init__(self, *args, **kwargs):
        super(ParticipantForm, self).__init__(*args, **kwargs)

        competition = Competition.objects.get(id=self.request_kwargs.get('pk'))
        competition_ids = competition.get_ids()

        distances = Distance.objects.filter(competition_id__in=competition_ids)
        insurances = Insurance.objects.filter(competition_id__in=competition_ids)


        competitions = Competition.objects.filter(parent_id=competition.parent_id)
        if competition.level == 2:
            comp_choices = [(competition.parent.id, 'Visa sezona')]
            comp_choices += [(c.id, str(c)) for c in competitions]
        else:
            comp_choices = [(competition.id, str(competition))]
        self.fields['competition'].choices = comp_choices

        self.fields['distance'].choices = [('', '------')] + [(distance.id, str(distance)) for distance in distances]
        self.fields['insurance'].choices = [('', '------')] + [(insurance.id, str(insurance)) for insurance in insurances]

        if competition.get_root().id == 1 and competition.level == 1:
            comps = competition.get_descendants()
            prices_obj = comps[0].price_set.all()
            prices = [(price.id, "%s€- %s" % (str(price.price * comps.count() * (100 - competition.complex_discount) / 100), price.distance)) for price in prices_obj]
        else:
            prices = [(str(price.id), "%s€ - %s" % (str(price.price), price.distance)) for price in competition.price_set.all().select_related('distance')]

        self.fields['price'].choices = [(u'', u'------'), ] + prices

        if self.instance.id:
            numbers = self.instance.numbers()
            self.fields['numbers'].choices = [(obj.id, str(obj)) for obj in Number.objects.filter(competition_id__in=competition_ids)]
            self.fields['numbers'].initial = [obj.id for obj in numbers]
        else:
            self.fields['competition'].initial = self.request_kwargs.get('pk')
            self.fields['country'].initial = 'LV'
            self.fields['is_participating'].initial = True
            # print('initial values here')


        self.fields['slug'].widget.attrs['readonly'] = True
        #self.fields['legacy_id'].widget.attrs['readonly'] = True

        if self.instance and self.instance.pk and self.instance.primary_number_id:
            self.fields['distance'].widget.attrs['readonly'] = True
            self.fields['competition'].widget.attrs['readonly'] = True

        self.fields['gender'].required = True
        self.fields['country'].required = True
        self.fields['birthday'].required = True

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Fieldset(
                'Dalībnieks',
                Row(
                    Column('competition', css_class='col-sm-3'),
                    Column('distance', css_class='col-sm-3'),
                    Column('insurance', css_class='col-sm-3'),
                    Column('price', css_class='col-sm-3'),
                ),
                Row(
                    Column('last_name', css_class='col-sm-3'),
                    Column('first_name', css_class='col-sm-3'),
                    Column('birthday', css_class='col-sm-3'),
                    Column('gender', css_class='col-sm-3'),
                ),
                Row(
                    Column('country', css_class='col-sm-3'),
                    Column('city', css_class='col-sm-3'),
                    Column('ssn', css_class='col-sm-3'),
                    Column('is_participating', 'is_paying', css_class='col-sm-3'),
                ),

            ),
            Row(
                Div(
                   Fieldset(
                    'Kontakti',
                    Row(
                        Column('phone_number', css_class='col-sm-6'),
                        Column('email', css_class='col-sm-6'),
                    ),
                    Row(
                        Column('send_sms', css_class='col-sm-6'),
                        Column('send_email', css_class='col-sm-6'),
                    ),

                    ),
                    css_class='col-sm-6'
                ),
                Div(
                    Fieldset(
                        'Numuri',
                        'numbers',
                    ),
                    css_class='col-sm-6'
                ),
            ),

            Fieldset(
                'Komanda',
                Column('team_name', css_class='col-sm-4'),
                Column('team', css_class='col-sm-4'),
                # Column('where_heard', css_class='col-sm-4'),
            ),
            Fieldset(
                'Aptaujas jautājumi',
                Column('bike_brand2', css_class='col-sm-4'),
                Column('occupation', css_class='col-sm-4'),
                Column('where_heard', css_class='col-sm-4'),
            ),
            Fieldset(
                'Pārējie',
                Column('slug', 'registration_dt', css_class='col-sm-4'),
                Column('registrant', css_class='col-sm-4'),
                Column('group', css_class='col-sm-4'),
            ),
            Div(
                'comment',
            ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
                Column(Submit('submit_and_next', 'Saglabāt un pievienot nākamo'), css_class='col-sm-2 pull-right'),
            ),


        )



class ResultForm(RequestKwargModelFormMixin, forms.ModelForm):
    calculate_time_field = forms.CharField(required=False)
    # participant = ParticipantChoices(required=True, widget=AutoHeavySelect2Widget(select2_options={
    #     'ajax': {
    #         'dataType': 'json',
    #         'quietMillis': 100,
    #         'data': '*START*django_select2.runInContextHelper(get_result_params, selector)*END*',
    #         'results': '*START*django_select2.runInContextHelper(django_select2.process_results, selector)*END*',
    #     },
    #     "minimumResultsForSearch": 0,
    #     "minimumInputLength": 0,
    #     "closeOnSelect": True
    # }))
    zero_time = forms.TimeField(label="Zero Time", required=False, widget=forms.TimeInput(format='%H:%M:%S.%f'))

    class Meta:
        model = Result
        fields = ('competition', 'participant', 'time', 'status', 'leader', 'zero_time', 'number')  # 'number',
        widgets = {
            'time': forms.TimeInput(format='%H:%M:%S.%f'),
            'number': NumberAllChoices,
            'participant': ParticipantChoices,
        }

    class Media:
        js = ('js/jquery.formset.js', 'plugins/datepicker/bootstrap-datepicker.min.js',
              'plugins/jquery.maskedinput.js', 'plugins/mailgun_validator.js')
        css = {
            'all': ('plugins/datepicker/datepicker.css', )
        }

    def clean(self):
        if not self.instance.id:
            number = self.cleaned_data.get('number', None)
            participant = self.cleaned_data.get('participant', None)
            if not number and participant:
                self.cleaned_data.update({'number': participant.primary_number })
            elif number and not participant:
                participant = Participant.objects.filter(is_participating=True, competition_id=self.request_kwargs.get('pk'), distance=number.distance, slug=number.participant_slug)
                if not participant:
                    raise forms.ValidationError("Cannot find participant")
                else:
                    self.cleaned_data.update({'participant': participant[0] })
                    if 'participant' in self._errors:
                        del self._errors['participant']
        return self.cleaned_data
    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)

        self.fields['competition'].widget.attrs['readonly'] = True

        if self.instance.id:
            distance = self.instance.number.distance
            self.fields['calculate_time_field'].widget.attrs['zero_time'] = self.instance.competition.distanceadmin_set.get(distance=distance).zero
        else:
            self.fields['competition'].initial = self.request_kwargs.get('pk')

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('competition', css_class='col-sm-4'),
                Column('participant', css_class='col-sm-4'),
                Column('number', css_class='col-sm-4'),
            ),
            Row(
                Column('time', css_class='col-sm-4'),
                Column('zero_time', css_class='col-sm-4'),

                Column('status', css_class='col-sm-4'),
            ),
            Row(
                Column('leader', css_class='col-sm-6'),
                Column(
                FieldWithButtons('calculate_time_field', StrictButton('Calc', type='button', css_class='btn-primary calculate_time_field_btn')),
                css_class='col-sm-4 pull-right'),
            ),
            Row(
               Fieldset(
                    'Apļi',
                    HTML('{% load crispy_forms_tags %}{% crispy lap lap.form.helper "bootstrap3" %}'),
                ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-2'),
            ),
            ),

        )

    def save(self, commit=True):

        obj = super(ResultForm, self).save(commit)

        # create result update task for participant
        print('recalculate?')
        # TODO: Need to optimize place and point recalculation.
        # update_results_for_result(obj)

        return obj


class UrlSyncForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = UrlSync
        fields = ('competition', 'url', 'expires', 'enabled', )


    def __init__(self, *args, **kwargs):
        super(UrlSyncForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('competition', css_class='col-sm-12'),

            ),
            Row(
                Column('url', css_class='col-sm-12'),
            ),
            Row(
                Column('expires', css_class='col-sm-12'),
            ),
            Row(
                Column('enabled', css_class='col-sm-12'),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-12'),
            ),
            ),

        )

class PriceForm(RequestKwargModelFormMixin, forms.ModelForm):
    competition = None

    class Meta:
        model = Price
        fields = ('distance', 'from_year', 'till_year', 'price', 'start_registering', 'end_registering')

    class Media:
        js = ('plugins/moment.min.js',
              'plugins/datetimepicker/bootstrap-datetimepicker.min.js',
              'coffee/manager/price_form.js')
        css = {
            'all': (
              'plugins/datetimepicker/bootstrap-datetimepicker.min.css',
            ),
        }

    def save(self, commit=True):
        self.instance.competition = self.competition
        return super(PriceForm, self).save(commit)


    def __init__(self, *args, **kwargs):
        super(PriceForm, self).__init__(*args, **kwargs)
        self.competition = Competition.objects.get(id=self.request_kwargs.get('pk'))

        self.fields['distance'].choices = [('', '------')] + [(obj.id, str(obj)) for obj in self.competition.get_distances()]

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('distance', css_class='col-sm-6'),
                Column('price', css_class='col-sm-6'),

            ),
            Row(
                Column('from_year', css_class='col-sm-6'),
                Column('till_year', css_class='col-sm-6'),
            ),
            Row(
                Column('start_registering', css_class='col-sm-6'),
                Column('end_registering', css_class='col-sm-6'),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-12'),
            ),
            ),

        )


class PreNumberAssignForm(RequestKwargModelFormMixin, forms.ModelForm):
    competition = None

    class Meta:
        model = PreNumberAssign
        fields = ('distance', 'number', 'segment', 'participant_slug', 'group_together', 'description')


    def save(self, commit=True):
        self.instance.competition = self.competition
        return super(PreNumberAssignForm, self).save(commit)


    def __init__(self, *args, **kwargs):
        super(PreNumberAssignForm, self).__init__(*args, **kwargs)
        self.competition = Competition.objects.get(id=self.request_kwargs.get('pk'))

        self.fields['distance'].choices = [('', '------')] + [(obj.id, str(obj)) for obj in self.competition.get_distances()]

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('distance', css_class='col-sm-4'),
                Column('participant_slug', css_class='col-sm-4'),

            ),
            Row(
                Column('number', css_class='col-sm-4'),
                Column('segment', css_class='col-sm-4'),
                Column('group_together', css_class='col-sm-4'),
            ),
            Row(
                Column('description', css_class='col-sm-12'),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-12'),
            ),
            ),

        )


class ChangedNameForm(RequestKwargModelFormMixin, forms.ModelForm):
    competition = None

    class Meta:
        model = ChangedName
        fields = ('slug', 'new_slug')

    def __init__(self, *args, **kwargs):
        super(ChangedNameForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('slug', css_class='col-sm-4'),
                Column('new_slug', css_class='col-sm-4'),
            ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-12'),
            ),
        )


class NewsForm(RequestKwargModelFormMixin, forms.ModelForm):

    class Meta:
        model = News
        fields = ('title', 'slug', 'language', 'image', 'competition', 'published_on', 'intro_content', 'content')
        widgets = {
            'image': PhotoPickWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)

        competitions = Competition.objects.filter(level__lte=1)
        competition_choices = [('', '------'),]
        for competition in competitions:
            title = " -- " * competition.level + str(competition)
            competition_choices.append((competition.id, title))

        self.fields['competition'].choices = competition_choices
        self.fields['slug'].required = False

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='col-sm-6'),
                Column('slug', css_class='col-sm-6'),

            ),
            Row(
                Column('language', css_class='col-sm-4'),
                Column('competition', css_class='col-sm-4'),
                Column('published_on', css_class='col-sm-4'),
            ),
            Row(
                Column('intro_content', css_class='col-sm-12'),
            ),
            Row(
                Column('content', css_class='col-sm-12'),
            ),
            Row(
                Column('image', css_class='col-sm-12'),
            ),
            Row(
                Column(Submit('submit', 'Saglabāt'), css_class='col-sm-12'),
            ),

        )

    def save(self, commit=True):
        if not self.instance.slug:
            self.instance.slug = slugify(self.instance.title)[:50]

        if self.request and self.request.user.is_authenticated():
            if not self.instance.id:
                self.instance.created_by = self.request.user
            self.instance.modified_by = self.request.user

        return super(NewsForm, self).save(commit)
