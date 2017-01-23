from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.utils import timezone
from django.views.generic import DetailView
from slugify import slugify

from velo.manager.forms import PriceForm, InvoiceListSearchForm
from velo.manager.tables import ManagePriceTable
from velo.manager.tables.tables import ManageInvoiceTable
from velo.manager.views.permission_view import ManagerPermissionMixin
from velo.payment.models import Price, Invoice
from velo.payment.utils import approve_payment
from velo.velo.mixins.views import SingleTableViewWithRequest, CreateViewWithCompetition, \
    UpdateViewWithCompetition, SetCompetitionContextMixin

__all__ = [
    'ManagePriceList', 'ManagePriceCreate', 'ManagePriceUpdate', 'ManageInvoiceList', 'ManageInvoice'
]

def gather_participants(instance):
    if instance.content_type.model == 'application':
        invoice_data = instance.content_object.participant_set.all()
    elif instance.content_type.model == 'team':
        invoice_data = instance.content_object.members_set.all()
    else:
        invoice_data = None
    return invoice_data


class ManagePriceList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Price
    table_class = ManagePriceTable
    template_name = 'bootstrap/manager/table.html'

    @property
    def add_link(self):
        return reverse_lazy('manager:price', kwargs={'pk': self.competition.id})


    def get_queryset(self):
        queryset = super(ManagePriceList, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        return queryset


class ManagePriceCreate(ManagerPermissionMixin, CreateViewWithCompetition):
    pk_url_kwarg = 'pk2'
    model = Price
    template_name = 'bootstrap/manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})


class ManagePriceUpdate(ManagerPermissionMixin, UpdateViewWithCompetition):
    pk_url_kwarg = 'pk2'
    model = Price
    template_name = 'bootstrap/manager/form.html'
    form_class = PriceForm

    def get_success_url(self):
        messages.success(self.request, 'Price created.')
        return reverse('manager:price_list', kwargs={'pk': self.kwargs.get('pk')})


class ManageInvoiceList(ManagerPermissionMixin, SingleTableViewWithRequest):
    model = Invoice
    table_class = ManageInvoiceTable
    template_name = 'bootstrap/manager/table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'search_form': InvoiceListSearchForm(request=self.request, competition=self.competition)})
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        query_attrs = self.request.GET.copy()

        if query_attrs.get('status'):
            queryset = queryset.filter(payment__status=query_attrs.get('status'))

        if query_attrs.get('series'):
            queryset = queryset.filter(series=query_attrs.get('series'))
        else:
            queryset = queryset.filter(series=self.competition.bill_series)

        if query_attrs.get('search'):
            slug = slugify(query_attrs.get('search'))
            queryset = queryset.filter(
                Q(series__icontains=slug) |
                Q(file__icontains=query_attrs.get('search'))
            )

        return queryset


class ManageInvoice(ManagerPermissionMixin, SetCompetitionContextMixin, DetailView):
    model = Invoice
    pk_url_kwarg = 'pk2'
    template_name = 'bootstrap/manager/invoice.html'

    invoice_from = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'participants': gather_participants(self.object.payment)})
        context.update({'old_invoice': self.object.created < timezone.now() - timezone.timedelta(weeks=26)})
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def process_post(self, request):
        action = request.POST.get('action', '')
        if action == 'mark_as_payed' and not self.object.created < timezone.now() - timezone.timedelta(weeks=26):
            payment_object = self.object.payment
            if approve_payment(payment_object):
                payment_object.status = payment_object.STATUSES.ok
                payment_object.save()


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.process_post(request)
        return super().get(request, *args, **kwargs)
