import datetime
from decimal import Decimal

from braces.views import CsrfExemptMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import BaseUpdateView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django_downloadview import ObjectDownloadView

from braces.views import JsonRequestResponseMixin
from pathlib import Path

from velo.core.models import Competition
from velo.core.utils import get_client_ip
from velo.payment.forms import ApplicationPayUpdateForm, TeamPayForm
from velo.payment.models import Invoice, Transaction, ActivePaymentChannel, PaymentChannel, DiscountCode
from velo.payment.utils import get_form_message, \
    get_participant_fee_from_price, get_insurance_fee_from_insurance, create_team_invoice, create_application_invoice
from velo.registration.models import Application
from velo.team.models import Team
from velo.velo.mixins.views import RequestFormKwargsMixin, NeverCacheMixin


class CheckPriceView(JsonRequestResponseMixin, DetailView):
    model = Competition

    def post(self, request, *args, **kwargs):
        try:
            year = int(request.POST.get('birthday_year'))
            distance_id = request.POST.get('distance', None)
            insurance_id = request.POST.get('insurance', None)
            if not distance_id or not year:
                raise ValueError
        except ValueError:
            return self.render_json_response({
                'message': _(
                    "<div class='fs14 fw700 c-white uppercase text-align--right'>Please enter all details</div>"),
                'success': False
            })
        messages = get_form_message(self.get_object(), distance_id, year, insurance_id=insurance_id)
        return self.render_json_response({
            'message': ''.join(messages),
            'success': True
        })

    def get(self, request, *args, **kwargs):
        raise Http404


class ApplicationOKView(NeverCacheMixin, RequestFormKwargsMixin, DetailView):
    model = Application
    slug_field = 'code'
    template_name = 'registration/application_ok.html'


class ApplicationPayView(NeverCacheMixin, RequestFormKwargsMixin, UpdateView):
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
                if not self.object.invoice and not participant.is_participating:
                    if participant.price.start_registering > now or participant.price.end_registering < now:
                        participant.price = None
                        participant.save()
                        if valid:
                            messages.error(self.request,
                                           _('Price expired. Start registering participants from step 1.'))
                        valid = False
                        # check if prices are still valid
            if valid:
                if self.object.discount_code:
                    prices = self.object.competition.price_set.filter(till_year__gte=participant.birthday.year, from_year__lte=participant.birthday.year, distance_id=participant.distance_id).order_by('price')

                    self.total_entry_fee += self.object.discount_code.calculate_entry_fee(float(prices[0].price))
                    self.object.discount_code.usage_times_left -= 1
                    self.object.discount_code.save()
                else:
                    self.total_entry_fee += get_participant_fee_from_price(self.object.competition, participant.price)
                if participant.insurance:
                    self.total_insurance_fee += get_insurance_fee_from_insurance(self.object.competition,
                                                                                 participant.insurance)

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
            donation = self.object.competition.params_dict.get('donation', {})
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


class TeamPayView(NeverCacheMixin, LoginRequiredMixin, RequestFormKwargsMixin, UpdateView):
    model = Team
    form_class = TeamPayForm
    template_name = 'team/team_pay.html'
    pk_url_kwarg = 'pk2'

    payment_amount = None

    def get_queryset(self):
        queryset = super(TeamPayView, self).get_queryset()
        queryset = queryset.filter(owner=self.request.user).select_related('distance', 'distance__competition',
                                                                           'distance__competition__parent')
        return queryset

    def get_form_success_url(self, form):
        return form.success_url

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_form_success_url(form))

    def validate(self):

        if self.object.is_featured:
            messages.success(self.request, _('Team profile already payed.'))
            return HttpResponseRedirect(reverse('account:team', kwargs={'pk2': self.object.id}))

        if self.object.distance.competition.is_past_due:
            messages.error(self.request, _('Competition already passed.'))
            return HttpResponseRedirect(reverse('account:team', kwargs={'pk2': self.object.id}))

        self.payment_amount = self.object.distance.profile_price

        if not self.payment_amount or self.payment_amount == 0.0:
            messages.error(self.request, _('Price for team profile not defined.'))
            return HttpResponseRedirect(reverse('account:team', kwargs={'pk2': self.object.id}))
        else:
            # Let's set amount here
            self.object.final_price = self.payment_amount
            self.object.save()

        return False

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        redirect = self.validate()
        if redirect:
            return redirect

        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        redirect = self.validate()
        if redirect:
            return redirect

        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class InvoiceDownloadView(ObjectDownloadView):
    model = Invoice

    def get_file(self):
        self.object = self.model.objects.get(slug=self.request.resolver_match.kwargs.get('slug'))
        my_file = Path(self.object.file.path)

        if not my_file.is_file():
            if self.object.payment.channel is not None:
                active_channel = self.object.payment.channel
            else:
                payment_channel = PaymentChannel.objects.values_list('id', flat=True).filter(is_bill=True)
                active_channel = ActivePaymentChannel.objects.filter(competition_id=self.object.competition.id, payment_channel_id__in=payment_channel).get()

            if self.object.payment.content_type.name == 'team':
                create_team_invoice(self.object.payment.content_object, active_channel, action="", invoice_object=self.object)
            elif self.object.payment.content_type.name == 'application':
                create_application_invoice(self.object.payment.content_object, active_channel, action="", invoice_object=self.object)
            else:
                raise Exception("Unknown invoice.payment.content_type.name %s" % self.object.payment.content_type.name)

        if not self.request.user.has_perm('registration.add_number'):
            if not self.object.access_time or not self.object.access_ip:
                if self.object.payment.status == 10:
                    self.object.payment.status = 20
                self.object.access_ip = get_client_ip(self.request)
                self.object.access_time = datetime.datetime.now()
                self.object.save(update_fields=["access_ip", "access_time"])
        return super(InvoiceDownloadView, self).get_file()


class TransactionRedirectView(NeverCacheMixin, CsrfExemptMixin, DetailView):
    model = Transaction
    slug_field = 'code'
    integration_object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status not in (Transaction.STATUSES.new, Transaction.STATUSES.pending):
            raise Http404('Transaction already finished.')

        self.integration_object = self.object.channel.get_class(self.object)
        response = self.integration_object.response()

        if isinstance(response, str):
            context = self.get_context_data(object=self.object, response=response)
            return self.render_to_response(context)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': self.integration_object.generate_form(), 'form_action': self.object.channel.url})
        return context


class DiscountCheckView(NeverCacheMixin, RequestFormKwargsMixin, View):
    def get(self, request, *args, **kwargs):
        raise Http404("GET not allowed for Discount check view")

    def post(self, request, *args, **kwargs):
        application = Application.objects.get(code=kwargs.get('slug'))

        discount_code = request.POST.get("discount_code", "")
        price = Decimal()
        ret = {"fee": None, "insurance": None}
        if discount_code:
            try:
                discount = DiscountCode.objects.get(code=discount_code)
                if discount.usage_times_left and discount.is_active:
                    if discount.campaign.competition == application.competition and discount.campaign.competition_id == application.competition_id:

                        for participant in application.participant_set.all():
                            prices = application.competition.price_set.filter(till_year__gte=participant.birthday.year,
                                                                              from_year__lte=participant.birthday.year,
                                                                              distance_id=participant.distance_id).order_by(
                                'price')

                            price += Decimal(discount.calculate_entry_fee(float(prices[0].price)))
                        ret['fee'] = {"new_total": price}
                        application.discount_code = discount
                        application.save()
            except:
                pass
        return JsonResponse(ret)
