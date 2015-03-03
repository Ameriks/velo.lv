# coding=utf-8
from __future__ import unicode_literals
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin, LoginRequiredMixin
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import BaseUpdateView
from django.core.urlresolvers import reverse
from django_tables2 import SingleTableView
import urllib
from core.models import Competition, Log
from django.utils.translation import ugettext as _
from payment.forms import ApplicationPayUpdateForm
from payment.models import Payment
from payment.utils import get_price, get_form_message, approve_payment, validate_payment, get_total, \
    get_participant_fee_from_price, get_insurance_fee_from_insurance
from registration.models import Application
from velo.mixins.views import RequestFormKwargsMixin
from velo.utils import SessionWHeaders


class CheckPriceView(JsonRequestResponseMixin, DetailView):
    model = Competition
    def post(self, request, *args, **kwargs):
        try:
            year = int(request.POST.get('birthday')[0:4])
            distance_id = request.POST.get('distance', None)
            insurance_id = request.POST.get('insurance', None)
            if not distance_id:
                raise ValueError
        except ValueError:
            return self.render_json_response({
                'message': _('Please enter all details'),
            })
        messages = get_form_message(self.get_object(), distance_id, year, insurance_id=insurance_id)
        return self.render_json_response({
            'message': ''.join(messages),
        })

    def get(self, request, *args, **kwargs):
        raise Http404


class ApplicationOKView(RequestFormKwargsMixin, DetailView):
    model = Application
    slug_field = 'code'
    template_name = 'registration/application_ok.html'


class ApplicationPayView(RequestFormKwargsMixin, UpdateView):
    model = Application
    form_class = ApplicationPayUpdateForm
    slug_field = 'code'
    template_name = 'registration/application_pay.html'

    participants = None
    total_entry_fee = 0.00
    total_insurance_fee = 0.00

    def get_form_success_url(self, form):
        return form.success_url

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_form_success_url(form))



    def get_form_kwargs(self):
        kwargs = super(ApplicationPayView, self).get_form_kwargs()
        kwargs.update({"participants": self.participants})
        return kwargs

    def validate(self):
        self.participants = self.object.participant_set.all()

        now = timezone.now()

        valid = True

        if self.participants.count() == 0:
            messages.error(self.request, _('Please add at least one participant'))
            valid = False

        for participant in self.participants:
            if not participant.last_name or not participant.first_name:
                messages.error(self.request, _('Please specify first name and last name for all participants'))
                valid = False
            elif not participant.birthday:
                messages.error(self.request, _('Please specify birthday for all participants'))
                valid = False
            elif not participant.price:
                messages.error(self.request, _('Not all participants have price added. Did you press save & pay?'))
                valid = False
            else:
                if not self.object.external_invoice_code and not participant.is_participating:
                    if participant.price.start_registering > now or participant.price.end_registering < now:
                        participant.price = None
                        participant.save()
                        if valid:
                            messages.error(self.request, _('Price expired. Start registering participants from step 1.'))
                        valid = False
                # check if prices are still valid
            if valid:
                self.total_entry_fee += get_participant_fee_from_price(self.object.competition, participant.price)
                if participant.insurance:
                    self.total_insurance_fee += get_insurance_fee_from_insurance(self.object.competition, participant.insurance)

        if valid:
            if self.object.total_entry_fee != self.total_entry_fee or self.object.total_insurance_fee != self.total_insurance_fee:
                self.object.total_entry_fee = self.total_entry_fee
                self.object.total_insurance_fee = self.total_insurance_fee
                # This is recalculated on model
                # self.object.final_price = self.total_entry_fee + self.total_insurance_fee + float(self.object.donation)
                self.object.save()
            return None
        else:
            return HttpResponseRedirect(reverse('application', kwargs={'slug': self.object.code}))


    def get_context_data(self, **kwargs):
        context = super(ApplicationPayView, self).get_context_data(**kwargs)
        context.update({'participants': self.participants})
        context.update({'total_entry_fee': self.total_entry_fee})
        context.update({'total_insurance_fee': self.total_insurance_fee})

        if self.object.competition.params:
            donation = self.object.competition.params.get('donation', {})
            if donation.get('enabled', False):
                context.update({'donation': donation})

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # We are not letting to update anything if competition is in past
        if self.object.competition.is_past_due:
            return HttpResponseRedirect(reverse('application', kwargs={'slug': self.object.code}))

        redirect = self.validate()
        if redirect:
            return redirect

        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # We are not letting to update anything if competition is in past
        if self.object.competition.is_past_due:
            return HttpResponseRedirect(reverse('application', kwargs={'slug': self.object.code}))

        redirect = self.validate()
        if redirect:
            return redirect

        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class PaymentReturnView(DetailView):
    model = Payment
    slug_field = 'erekins_code'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.status == Payment.STATUS_OK:
            if self.object.content_type.model == 'application':
                return HttpResponseRedirect(reverse('application_ok', kwargs={'slug': self.object.content_object.code}))

        return validate_payment(self.object, user=True, request=request)

