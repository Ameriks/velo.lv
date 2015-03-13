# coding=utf-8
from __future__ import unicode_literals
from crispy_forms.layout import Layout, Row, Column, Div, Fieldset, HTML
from django import forms
from crispy_forms.helper import FormHelper
from django.contrib import messages
from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.safestring import mark_safe
from payment.models import ActivePaymentChannel
from payment.utils import create_application_invoice, create_application_bank_transaction
from payment.widgets import PaymentTypeWidget, DoNotRenderWidget
from registration.models import Application
from velo.mixins.forms import RequestKwargModelFormMixin, GetClassNameMixin
from django.utils.translation import ugettext, ugettext_lazy as _
from velo.utils import load_class


class ApplicationPayUpdateForm(GetClassNameMixin, RequestKwargModelFormMixin, forms.ModelForm):
    accept_terms = forms.BooleanField(label=_("I confirm that my health condition allows me to take part in competition in my chosen distance. I promise to keep regulations, traffic rules and use safety helmet."), required=True)
    accept_inform_participants = forms.BooleanField(label=_("I will inform all registered participants about rules."), required=True)
    accept_insurance = forms.BooleanField(label="", required=False)

    payment_type = forms.ChoiceField(choices=(), label=_("Payment Type"), widget=PaymentTypeWidget)

    prepend = 'payment_'
    participants = None
    success_url = None

    class Meta:
        model = Application
        fields = ('company_name', 'company_vat', 'company_regnr', 'company_address', 'company_juridical_address', 'invoice_show_names', 'donation')
        widgets = {
            'donation': DoNotRenderWidget, # We will add field manually
        }

    def _post_clean(self):
        super(ApplicationPayUpdateForm, self)._post_clean()
        if not bool(self.errors):
            try:
                instance = self.instance
                instance.set_final_price() # if donation have changed, then we need to recalculate,
                                           # because instance is not yet saved and it means,
                                           # that this function on model is not yet run.
                active_payment_type = ActivePaymentChannel.objects.get(id=self.cleaned_data.get('payment_type'))

                if active_payment_type.payment_channel.is_bill:
                    instance.external_invoice_code, instance.external_invoice_nr = create_application_invoice(instance, active_payment_type)
                    self.success_url = reverse('application_ok', kwargs={'slug': instance.code})
                    messages.info(self.request, _('Invoice successfully created and sent to %(email)s') % {'email': instance.email})
                else:
                    self.success_url = create_application_bank_transaction(instance, active_payment_type)

            except:
                # TODO We need to catch exception and log it to sentry
                self._errors['payment_type'] = self.error_class([_("Error in connection with bank. Try again later.")])


    def save(self, commit=True):
        instance = super(ApplicationPayUpdateForm, self).save(commit=False)
        if self.request:
            instance.updated_by = self.request.user
        if instance.payment_status < Application.PAY_STATUS_WAITING:
            instance.payment_status = Application.PAY_STATUS_WAITING

        if commit:
            instance.save()

        return instance

    def clean_donation(self):
        donation = self.cleaned_data.get('donation')
        # If person have already taken invoice, then we do not allow changing donation amount
        if self.instance.external_invoice_code:
            return self.instance.donation
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
                    checkboxes += (key, )


        payments = competition.activepaymentchannel_set.filter(from_date__lte=now, till_date__gte=now).select_related('payment_channel')
        # If user have already requested bill, then we are not showing possibility to request one more.
        if self.instance.external_invoice_code:
            payments = payments.filter(payment_channel__is_bill=False)

        self.fields['payment_type'].choices = [(obj.id, obj) for obj in payments]

        self.fields['donation'].required = False

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(
                    *checkboxes,
                    css_class='col-sm-8'
                ),
                Column(
                    Div(
                        HTML(
                            "<h4>%s: <span id='final_price' data-amount='%s'>%s</span> €</h4>" % (_('Final Price'), self.instance.total_entry_fee + self.instance.total_insurance_fee, floatformat(self.instance.final_price, -2)),
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
                        'invoice_show_names',
                        css_class='invoice_fields',
                    ),
                    css_class='col-sm-4',
                )
            ),
        )
