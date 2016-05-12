# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.contrib import messages
from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Layout, Row, Column, Div, Fieldset, HTML, Field
from crispy_forms.helper import FormHelper

from velo.payment.models import ActivePaymentChannel, Payment
from velo.payment.utils import create_application_invoice, create_application_bank_transaction, create_team_invoice, \
    create_team_bank_transaction, approve_payment
from velo.payment.widgets import PaymentTypeWidget, DoNotRenderWidget
from velo.registration.models import Application
from velo.velo.mixins.forms import RequestKwargModelFormMixin, GetClassNameMixin
from velo.velo.utils import load_class


class ApplicationPayUpdateForm(GetClassNameMixin, RequestKwargModelFormMixin, forms.ModelForm):
    accept_terms = forms.BooleanField(label=_(
        "I confirm that my health condition allows me to take part in competition in my chosen distance. I promise to keep regulations, traffic rules and use safety helmet."),
                                      required=True)
    accept_inform_participants = forms.BooleanField(label=_("I will inform all registered participants about rules."),
                                                    required=True)
    accept_insurance = forms.BooleanField(label="", required=False)

    payment_type = forms.ChoiceField(choices=(), label="", widget=PaymentTypeWidget)

    prepend = 'payment_'
    participants = None
    success_url = None

    class Meta:
        model = Application
        fields = ('company_name', 'company_vat', 'company_regnr', 'company_address', 'company_juridical_address',
                  'invoice_show_names', 'donation')
        widgets = {
            'donation': DoNotRenderWidget,  # We will add field manually
        }

    def _post_clean(self):
        super(ApplicationPayUpdateForm, self)._post_clean()
        if not bool(self.errors):
            try:
                instance = self.instance
                instance.set_final_price()  # if donation have changed, then we need to recalculate,
                # because instance is not yet saved and it means,
                # that this function on model is not yet run.

                if instance.final_price == 0:
                    payment = Payment.objects.create(content_object=instance,
                                                     total=instance.final_price,
                                                     status=Payment.STATUSES.ok, )
                    approve_payment(payment, self.request.user, self.request)
                    self.success_url = reverse('application_ok', kwargs={'slug': instance.code})
                else:

                    active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))

                    if active_payment_type.payment_channel.is_bill:
                        instance.external_invoice_code, instance.external_invoice_nr = create_application_invoice(instance,
                                                                                                                  active_payment_type)
                        self.success_url = reverse('application_ok', kwargs={'slug': instance.code})
                        messages.info(self.request,
                                      _('Invoice successfully created and sent to %(email)s') % {'email': instance.email})
                    else:
                        self.success_url = create_application_bank_transaction(instance, active_payment_type)

            except:
                # TODO We need to catch exception and log it to sentry
                self._errors['payment_type'] = self.error_class([_("Error in connection with bank. Try again later.")])

    def save(self, commit=True):
        instance = super(ApplicationPayUpdateForm, self).save(commit=False)
        if self.request:
            instance.updated_by = self.request.user
        if instance.payment_status < Application.PAY_STATUS.waiting:
            instance.payment_status = Application.PAY_STATUS.waiting

        instance.params = self.cleaned_data

        if commit:
            instance.save()

        return instance

    def clean_donation(self):
        donation = self.cleaned_data.get('donation', 0.00)
        # If person have already taken invoice, then we do not allow changing donation amount
        if self.instance.external_invoice_code:
            return float(self.instance.donation)
        else:
            return donation

    def clean(self):
        if not self.cleaned_data.get('donation', ''):
            self.cleaned_data.update({'donation': 0.00})

        super(ApplicationPayUpdateForm, self).clean()
        try:
            active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))
        except:
            active_payment_type = None
        if active_payment_type and active_payment_type.payment_channel.is_bill:  # Hard coded bill ids.
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
        self.participants = kwargs.pop('participants', None)

        super(ApplicationPayUpdateForm, self).__init__(*args, **kwargs)

        insured_participants = self.participants.exclude(insurance=None)
        if insured_participants:
            self.fields['accept_insurance'].required = True
            insurance_company = insured_participants[0].insurance.insurance_company
            terms_doc = "<a href='%s' target='_blank'>Noteikumi</a>" % insurance_company.terms_doc.url if insurance_company.terms_doc else ""
            self.fields['accept_insurance'].label = mark_safe("%s %s" % (insurance_company.term, terms_doc))

        else:
            self.fields['accept_insurance'].widget = forms.HiddenInput()

        now = timezone.now()

        competition = self.instance.competition
        checkboxes = (
            'accept_terms',
            'accept_inform_participants',
            'accept_insurance',
        )

        if competition.processing_class:
            _class = load_class(competition.processing_class)
            processing = _class(competition=competition)
            if hasattr(processing, 'payment_additional_checkboxes'):
                for key, field in processing.payment_additional_checkboxes(application=self.instance):
                    self.fields[key] = field
                    checkboxes += (key,)

        payments = competition.activepaymentchannel_set.filter(from_date__lte=now, till_date__gte=now).select_related(
            'payment_channel')
        # If user have already requested bill, then we are not showing possibility to request one more.
        if self.instance.external_invoice_code:
            payments = payments.filter(payment_channel__is_bill=False)

        if self.instance.final_price == 0:
            self.fields['payment_type'].required = False
            self.fields['payment_type'].widget = forms.HiddenInput()
        else:
            self.fields['payment_type'].choices = [(obj.id, obj) for obj in payments]

        self.fields['donation'].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
                *checkboxes,
                Div(
                    Div(
                      css_class="w100 bottom-margin--30",
                    ),
                    Div(
                        Div(
                            HTML(_("Payment method")) if self.instance.final_price > 0 else HTML(""),
                          css_class="fs14 fw700 uppercase w100 bottom-margin--30"
                        ),
                        Div(
                            Div(
                                Field('payment_type', wrapper_class="row row--gutters-20"),

                                css_class="w100"
                            ),
                            css_class="input-wrap w100"
                        ),

                      css_class="inner no-padding--560"
                    ),
                    css_class="w100 border-top"
                ),



                Div(
                Div(

                    # company_name
                    Div(
                        Div(
                            Field(
                                "company_name",
                                css_class="input-field if--50 if--dark js-placeholder-up",
                            ),
                            css_class="input-wrap w100 bottom-margin--15"
                        ),
                        css_class="col-xl-8 col-m-12 col-s-24"
                    ),

                    # company_vat
                    Div(
                        Div(
                            Field(
                                "company_vat",
                                css_class="input-field if--50 if--dark js-placeholder-up"
                            ),
                            css_class="input-wrap w100 bottom-margin--15"
                        ),
                        css_class="col-xl-8 col-m-12 col-s-24"
                    ),

                    # company_regnr
                    Div(
                        Div(
                            Field(
                                "company_regnr",
                                css_class="input-field if--50 if--dark js-placeholder-up"
                            ),
                            css_class="input-wrap w100 bottom-margin--15"
                        ),
                        css_class="col-xl-8 col-m-12 col-s-24"
                    ),

                    # company_address
                    Div(
                        Div(
                            Field(
                                "company_address",
                                css_class="input-field if--50 if--dark js-placeholder-up"
                            ),
                            css_class="input-wrap w100 bottom-margin--15"
                        ),
                        css_class="col-xl-8 col-m-12 col-s-24"
                    ),

                    # company_juridical_address
                    Div(
                        Div(
                            Field(
                                "company_juridical_address",
                                css_class="input-field if--50 if--dark js-placeholder-up"
                            ),
                            css_class="input-wrap w100 bottom-margin--15"
                        ),
                        css_class="col-xl-8 col-m-12 col-s-24"
                    ),

                    'invoice_show_names',
                    css_class=""
                ),
                    css_class="invoice_fields"
                )
        )


class TeamPayForm(GetClassNameMixin, RequestKwargModelFormMixin, forms.ModelForm):
    payment_type = forms.ChoiceField(choices=(), label=_("Payment Type"), widget=PaymentTypeWidget)

    prepend = 'payment_'
    success_url = None

    class Meta:
        model = Application
        fields = ('company_name', 'company_vat', 'company_regnr', 'company_address', 'company_juridical_address',)

    def _post_clean(self):
        super(TeamPayForm, self)._post_clean()
        if not bool(self.errors):
            try:
                instance = self.instance
                active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))

                if active_payment_type.payment_channel.is_bill:
                    instance.external_invoice_code, instance.external_invoice_nr = create_team_invoice(instance,
                                                                                                       active_payment_type)
                    self.success_url = reverse('account:team', kwargs={'pk2': instance.id})
                    messages.info(self.request,
                                  _('Invoice successfully created and sent to %(email)s') % {'email': instance.email})
                else:
                    self.success_url = create_team_bank_transaction(instance, active_payment_type)

            except:
                #     TODO We need to catch exception and log it to sentry
                self._errors['payment_type'] = self.error_class([_("Error in connection with bank. Try again later.")])

    def clean(self):
        super(TeamPayForm, self).clean()
        try:
            active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))
        except:
            active_payment_type = None
        if active_payment_type and active_payment_type.payment_channel.is_bill:  # Hard coded bill ids.
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

        super(TeamPayForm, self).__init__(*args, **kwargs)

        now = timezone.now()

        competition = self.instance.distance.competition

        payments = competition.activepaymentchannel_set.filter(from_date__lte=now, till_date__gte=now).select_related(
            'payment_channel')
        # If user have already requested bill, then we are not showing possibility to request one more.
        if self.instance.external_invoice_code:
            payments = payments.filter(payment_channel__is_bill=False)

        self.fields['payment_type'].choices = [(obj.id, obj) for obj in payments]

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(
                    css_class='col-sm-8'
                ),
                Column(
                    Div(
                        HTML(
                            "<h4>%s: <span id='final_price' data-amount='%s'>%s</span> €</h4>" % (
                            _('Final Price'), self.instance.final_price, floatformat(self.instance.final_price, -2)),
                        ),
                        css_class='margin-bottom-40'
                    ),
                    'payment_type',
                    Fieldset(
                        _('Invoice Fields'),
                        'company_name',
                        'company_vat',
                        'company_regnr',
                        'company_address',
                        'company_juridical_address',
                        css_class='invoice_fields',
                    ),
                    css_class='col-sm-4',
                )
            ),
        )
