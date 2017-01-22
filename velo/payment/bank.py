import datetime
import json
import pytz
import requests

from base64 import b64encode, b64decode

from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.utils import flatatt
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from OpenSSL.crypto import load_certificate, load_privatekey, FILETYPE_PEM
from OpenSSL import crypto
from django.utils.translation import activate

from velo.payment.models import Transaction, PaymentChannel, DailyTransactionTotals
from velo.payment.utils import log_message, get_client_ip


class BankSignature(object):
    transaction = None
    values = None

    def __init__(self, transaction, *args, **kwargs):
        self.transaction = transaction

    def create_signature(self, digest):
        pk_string = open(self.transaction.link.key_file.path, 'rt').read()
        key = load_privatekey(FILETYPE_PEM, pk_string)

        signed = crypto.sign(key, str(digest), 'sha1')
        b21 = b64encode(signed)
        return b21

    def verify_signature(self, signature, digest):
        signature = str(signature)
        pk_string = open(self.transaction.link.public_key.path, 'rb').read()
        cert = load_certificate(FILETYPE_PEM, pk_string)

        if crypto.verify(cert, b64decode(signature), digest, 'sha1') is None:
            return True
        else:
            return False


class PaymentRequestForm(forms.Form):
    def redirect_html(self):
        fields = [str(field) for field in self]
        attrs = {
            'action': self.transaction.link.url,
            'method': 'POST',
            'id': 'auto_redirect'
        }
        attrs = flatatt(attrs)
        return format_html(
            """<form{0}>{1}</form>
            <script type="text/javascript">
                document.forms["auto_redirect"].submit();
            </script>""", attrs, mark_safe(''.join(fields)))


class BankIntegrationBase(object):
    transaction = None
    request = None

    def __init__(self, transaction=None):
        if transaction:
            self.transaction = transaction

    @property
    def service_url(self):
        return 'test'

    def generate_form(self):
        pass

    def verify_return(self, request):
        pass

    def check_transaction(self, request=None):
        pass

    def server_check_transaction(self, request):
        pass

    def expected_values(self, kind=None):
        raise Exception('Not Implemented')

    def create_ordered_values(self, values, kind):
        return [values.get(value) for value in self.expected_values(kind) if value in values]

    def generate_digest(self, values, kind=None):
        digest = ''
        for value in self.create_ordered_values(values, kind):
            digest += str(len(value)).rjust(3, u'0')
            digest += str(value)
        return digest

    def final_redirect(self, success):
        activate(self.transaction.language)
        if self.transaction.payment.content_type.model == 'application':
            return HttpResponseRedirect(
                reverse('application_ok' if success else 'application_pay',
                        kwargs={'slug': self.transaction.payment.content_object.code}
                        ))
        elif self.transaction.payment.content_type.model == 'team':
            return HttpResponseRedirect(
                reverse('account:team' if success else 'account:team_pay',
                        kwargs={'pk2': self.transaction.payment.content_object.id}
                        ))
        else:
            return HttpResponse('Something went wrong')


class FirstDataIntegration(BankIntegrationBase):
    @staticmethod
    def get_transaction_status(value):
        if value == 'OK':
            return Transaction.STATUSES.ok
        elif value == 'FAILED':
            return Transaction.STATUSES.failed
        elif value == 'DECLINED':
            return Transaction.STATUSES.declined
        elif value == 'TIMEOUT':
            return Transaction.STATUSES.timeout
        elif value in ('REVERSED', 'AUTOREVERSED'):
            return Transaction.STATUSES.reversed

    def server_check_transaction(self, request=None):
        status_dict = self.check_transaction()
        if status_dict:
            if status_dict.get('RESULT') not in ('CREATED', 'PENDING'):
                self.transaction.status = self.get_transaction_status(status_dict.get('RESULT'))
                self.transaction.server_response = status_dict.get('RESULT')
                self.transaction.server_response_at = timezone.now()
                self.transaction.save()
                return True
            else:
                return False
        else:
            raise Exception('Error retrieving status')

    def verify_return(self, request):
        status_dict = self.check_transaction()
        if not status_dict:
            return super().final_redirect(False)
        else:
            self.transaction.user_response = status_dict.get('RESULT')
            self.transaction.server_response = self.transaction.user_response
            self.transaction.returned_user_ip = get_client_ip(request)
            self.transaction.user_response_at = timezone.now()
            self.transaction.server_response_at = self.transaction.user_response_at
            self.transaction.status = self.get_transaction_status(status_dict.get('RESULT'))
            self.transaction.save()
            return super().final_redirect(status_dict.get('RESULT') == 'OK')

    def check_transaction(self, request=None):
        params = {
            'command': 'c',
            'trans_id': self.transaction.external_code,
        }
        try:
            params.update({'client_ip_addr': self.request.META.get('REMOTE_ADDR', None)})
        except AttributeError:
            params.update({'client_ip_addr': '127.0.0.1'})
        resp = requests.post(
            self.transaction.link.server_url,
            cert=(self.transaction.link.cert_file.path, self.transaction.link.key_file.path),
            data=params,
            verify=False
        )
        if resp.status_code != 200:
            log_message('FAILED VERIFY Transaction', "%i -- %s" % (resp.status_code, resp.text), object=self.transaction)
            return False
        else:
            if 'error: ' in resp.text:
                log_message('ERROR Transaction', resp.text, object=self.transaction)
                return False

            dict_obj = {}
            for _ in resp.text.split('\n'):
                key, value = _.split(': ')
                dict_obj.update({key: value})
            log_message('VERIFIED Transaction', resp.text, params=dict_obj, object=self.transaction)
            return dict_obj

    def response(self):
        if not self.transaction.external_code:
            self.request_transaction_code()

        if self.transaction.external_code:
            from velo.payment.tasks import process_server_response
            process_server_response.apply_async(args=[self.transaction.id], countdown=120)
            return HttpResponseRedirect(
                "%s?%s" % (self.transaction.link.url, urlencode({'trans_id': self.transaction.external_code}))
            )
        else:
            return super().final_redirect(False)

    def request_transaction_code(self):
        transaction_id = None

        language = self.transaction.language
        if language == "ru":
            language = "en"

        params = {
            'command': 'v',
            'amount': int(self.transaction.amount * 100),
            'currency': "978",  # ISO 4217 - EUR = 978
            'description': self.transaction.information,
            'language': language
        }
        try:
            params.update({'client_ip_addr': self.request.META.get('REMOTE_ADDR', None)})
        except AttributeError:
            params.update({'client_ip_addr': '127.0.0.1'})

        resp = requests.post(
            self.transaction.link.server_url,
            cert=(self.transaction.link.cert_file.path, self.transaction.link.key_file.path),
            data=params,
            verify=False,)

        log_message('GOT FD response', resp.text, object=self.transaction)
        if resp.text[0:14] == 'TRANSACTION_ID':
            transaction_id = resp.text.strip()[16:]
            self.transaction.external_code = transaction_id
            self.transaction.external_code_requested = timezone.now()
            self.transaction.save()
            return transaction_id
        else:
            return transaction_id


class SwedbankPaymentRequestForm(PaymentRequestForm):
    VK_SERVICE = forms.CharField(widget=forms.HiddenInput())
    VK_VERSION = forms.CharField(widget=forms.HiddenInput())
    VK_SND_ID = forms.CharField(widget=forms.HiddenInput())
    VK_STAMP = forms.CharField(widget=forms.HiddenInput())
    VK_AMOUNT = forms.CharField(widget=forms.HiddenInput())
    VK_CURR = forms.CharField(widget=forms.HiddenInput())
    VK_REF = forms.CharField(widget=forms.HiddenInput())
    VK_MSG = forms.CharField(widget=forms.HiddenInput())
    VK_MAC = forms.CharField(widget=forms.HiddenInput(), required=False)
    VK_RETURN = forms.CharField(widget=forms.HiddenInput())
    VK_LANG = forms.CharField(widget=forms.HiddenInput())
    VK_ENCODING = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, transaction=None, integrator=None, *args, **kwargs):
        self.transaction = transaction
        self.integrator = integrator
        initial = {}
        initial.update({
            'VK_SERVICE': '1002',
            'VK_VERSION': '008',
            'VK_SND_ID': "VELOV",
            'VK_STAMP': self.transaction.id,
            'VK_AMOUNT': float(self.transaction.amount),
            'VK_CURR': 'EUR',
            'VK_REF': self.transaction.id,
            'VK_MSG': self.transaction.information,
            'VK_RETURN': "%s%s" % (settings.MY_DEFAULT_DOMAIN,
                                   reverse('payment:transaction_done', kwargs=({'code': transaction.code}))),
            'VK_LANG': self.transaction.language_bank,
            'VK_ENCODING': 'UTF-8',
        })

        super(PaymentRequestForm, self).__init__(initial, *args)
        self.transaction.status = Transaction.STATUSES.pending
        self.transaction.save()

        if self.is_valid():
            digest = self.integrator.generate_digest(values=self.cleaned_data)
            self.data['VK_MAC'] = BankSignature(self.transaction).create_signature(digest)
        else:
            raise RuntimeError("invalid initial data")


class SwedbankIntegration(BankIntegrationBase):
    @staticmethod
    def get_transaction_status(value):
        if value == '1101':
            return Transaction.STATUSES.ok
        elif value == '1901':
            return Transaction.STATUSES.failed

    @property
    def get_form(self):
        return SwedbankPaymentRequestForm

    def generate_form(self):
        return self.get_form(transaction=self.transaction, integrator=self)

    def response(self):
        return 'form'

    def expected_values(self, kind=None):
        return 'VK_SERVICE,VK_VERSION,VK_SND_ID,VK_REC_ID,VK_STAMP,VK_T_NO,VK_AMOUNT,VK_CURR,VK_REC_ACC,VK_REC_NAME,VK_SND_ACC,VK_SND_NAME,VK_REF,VK_MSG,VK_T_DATE'.split(',')

    def check_transaction(self, request=None):
        post = {}
        for key in request.POST:
            post.update({key: request.POST.get(key)})

        resp_obj = BankSignature(self.transaction)
        if resp_obj.verify_signature(post.get('VK_MAC'), self.generate_digest(post)):
            log_message('VERIFIED Transaction', params=post, object=self.transaction)
            del post['VK_MAC']  # No need, because already verified
            return post
        else:
            log_message('ERROR Transaction', 'Invalid MAC', params=post, object=self.transaction)
            return False

    def server_check_transaction(self, request=None):
        _get = {}
        for key in request.GET:
            _get.update({key: request.GET.get(key)})
        resp_obj = BankSignature(self.transaction)

        if resp_obj.verify_signature(_get.get('VK_MAC'), self.generate_digest(_get)):
            log_message('VERIFIED Transaction', params=_get, object=self.transaction)
            if _get.get('VK_SERVICE') == '1101':
                self.transaction.server_response = 'OK'
            else:
                self.transaction.server_response = 'FAILED'
            self.transaction.status = self.get_transaction_status(_get.get('VK_SERVICE'))
            self.transaction.server_response_at = timezone.now()
            self.transaction.returned_server_ip = get_client_ip(request)
            self.transaction.save()
            return _get
        else:
            log_message('ERROR Transaction', 'Invalid MAC', params=_get, object=self.transaction)
            raise Exception('Invalid MAC')

    def verify_return(self, request):
        # if user is forwarded, then we receive POST request. From SERVER bank sends GET request.
        if request.POST.get('VK_AUTO', None) == 'N':
            self.transaction = Transaction.objects.get(id=request.POST.get('VK_REF'))
        else:
            self.transaction = Transaction.objects.get(id=request.GET.get('VK_REF'))

        if request.POST.get('VK_AUTO', None) is None:
            self.server_check_transaction(request)
            return HttpResponse('OK')

        status_dict = self.check_transaction(request)

        if not status_dict:
            return super().final_redirect(False)
        else:
            # User response.
            if status_dict.get('VK_SERVICE') == '1101':
                self.transaction.user_response = 'OK'
            else:
                self.transaction.user_response = 'CANCELLED'
            self.transaction.status = self.get_transaction_status(status_dict.get('VK_SERVICE'))
            self.transaction.returned_user_ip = get_client_ip(request)
            self.transaction.user_response_at = timezone.now()
            self.transaction.save()

            return super().final_redirect(status_dict.get('VK_SERVICE') == '1101')


class SEBPaymentRequestForm(PaymentRequestForm):
    IB_SERVICE = forms.CharField(widget=forms.HiddenInput())
    IB_VERSION = forms.CharField(widget=forms.HiddenInput())
    IB_NAME = forms.CharField(widget=forms.HiddenInput())
    IB_SND_ID = forms.CharField(widget=forms.HiddenInput())
    IB_PAYMENT_ID = forms.CharField(widget=forms.HiddenInput())
    IB_AMOUNT = forms.CharField(widget=forms.HiddenInput())
    IB_CURR = forms.CharField(widget=forms.HiddenInput())
    IB_PAYMENT_DESC = forms.CharField(widget=forms.HiddenInput())
    IB_CRC = forms.CharField(widget=forms.HiddenInput(), required=False)
    IB_FEEDBACK = forms.CharField(widget=forms.HiddenInput())
    IB_LANG = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, transaction=None, integrator=None, *args, **kwargs):
        self.transaction = transaction
        self.integrator = integrator
        initial = {}
        initial.update({
            'IB_SERVICE': '0002',
            'IB_VERSION': '001',
            'IB_NAME': "LATVIJAS+KALNU+DIVRITEŅU",
            'IB_SND_ID': "MTBASOC",
            'IB_PAYMENT_ID': self.transaction.id,
            'IB_AMOUNT': float(self.transaction.amount),
            'IB_CURR': 'EUR',
            'IB_PAYMENT_DESC': self.transaction.information,
            'IB_FEEDBACK': "%s%s" % (settings.MY_DEFAULT_DOMAIN, reverse('payment:transaction_done',
                                                                         kwargs={'code': self.transaction.code})),
            'IB_LANG': self.transaction.language_bank,
        })

        super(PaymentRequestForm, self).__init__(initial, *args)

        if self.is_valid():
            digest = self.integrator.generate_digest(values=self.cleaned_data, kind='0002')
            self.data['IB_CRC'] = BankSignature(self.transaction).create_signature(digest)
        else:
            raise RuntimeError("invalid initial data")


class IBankIntegration(BankIntegrationBase):
    @staticmethod
    def get_transaction_status(value):
        if value == 'ACCOMPLISHED':
            return Transaction.STATUSES.ok
        elif value == 'CANCELLED':
            return Transaction.STATUSES.canceled
        else:
            return Transaction.STATUSES.failed

    @property
    def get_form(self):
        return SEBPaymentRequestForm

    def generate_form(self):
        return self.get_form(transaction=self.transaction, integrator=self)

    def response(self):
        return 'form'

    def expected_values(self, kind=None):
        if kind == '0002':
            return ['IB_SND_ID', 'IB_SERVICE', 'IB_VERSION', 'IB_AMOUNT', 'IB_CURR', 'IB_NAME', 'IB_PAYMENT_ID', 'IB_PAYMENT_DESC']
        elif kind == '0003':
            return ['IB_SND_ID', 'IB_SERVICE', 'IB_VERSION', 'IB_PAYMENT_ID', 'IB_AMOUNT', 'IB_CURR', 'IB_REC_ID', 'IB_REC_ACC', 'IB_REC_NAME', 'IB_PAYER_ACC', 'IB_PAYER_NAME', 'IB_PAYMENT_DESC', 'IB_PAYMENT_DATE', 'IB_PAYMENT_TIME', ]
        elif kind == '0004':
            return ['IB_SND_ID', 'IB_SERVICE', 'IB_VERSION', 'IB_REC_ID', 'IB_PAYMENT_ID', 'IB_PAYMENT_DESC', 'IB_FROM_SERVER', 'IB_STATUS', ]

    def check_transaction(self, request=None):
        post = {}
        for key in request.POST:
            post.update({key: request.POST.get(key)})

        resp_obj = BankSignature(self.transaction)
        if resp_obj.verify_signature(post.get('IB_CRC'), self.generate_digest(post, post.get('IB_SERVICE'))):
            log_message('VERIFIED Transaction', params=post, object=self.transaction)
            del post['IB_CRC']  # No need, because already verified
            return post
        else:
            log_message('ERROR Transaction', 'Invalid MAC', params=post, object=self.transaction)
            return False

    def server_check_transaction(self, request=None):
        _get = {}
        for key in request.GET:
            _get.update({key: request.GET.get(key)})
        resp_obj = BankSignature(self.transaction)

        if resp_obj.verify_signature(_get.get('IB_CRC'), self.generate_digest(_get, _get.get('IB_SERVICE'))):
            log_message('VERIFIED Transaction', params=_get, object=self.transaction)
            if _get.get('IB_SERVICE') == '0003':
                self.transaction.status = Transaction.STATUSES.pendind
            else:
                self.transaction.server_response = _get.get('IB_STATUS', '')
                self.transaction.status = self.get_transaction_status(_get.get('IB_STATUS'))
                self.transaction.server_response_at = timezone.now()
                self.transaction.returned_server_ip = get_client_ip(request)

            self.transaction.save()
            return _get
        else:
            log_message('ERROR Transaction', 'Invalid MAC', params=_get, object=self.transaction)
            raise Exception('Invalid MAC')

    def verify_return(self, request):
        # if user is forwarded, then we receive POST request. From SERVER bank sends GET request.
        if request.POST.get('IB_FROM_SERVER', None) == 'N':
            self.transaction = request.account.transaction_set.get(id=request.POST.get('IB_PAYMENT_ID'))
        else:
            self.transaction = request.account.transaction_set.get(id=request.GET.get('IB_PAYMENT_ID'))

        if request.POST.get('IB_FROM_SERVER', None) is None:
            self.server_check_transaction(request)
            return HttpResponse('OK')

        status_dict = self.check_transaction(request)

        if not status_dict:
            return super().final_redirect(False)
        else:
            # User response.
            if status_dict.get('IB_SERVICE') == '0004':
                self.transaction.user_response = status_dict.get('IB_STATUS')
                self.transaction.status = self.get_transaction_status(status_dict.get('IB_STATUS'))
                self.transaction.returned_user_ip = get_client_ip(request)
                self.transaction.user_response_at = timezone.now()
                self.transaction.save()

                return super().final_redirect(status_dict.get('IB_STATUS') == 'ACCOMPLISHED')
            else:
                return HttpResponse('Something went wrong')


def close_business_day():
    riga_tz = pytz.timezone("Europe/Riga")
    dt = timezone.now()
    end_date = datetime.datetime.now(riga_tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = datetime.datetime.now(riga_tz).replace(day=dt.day - 1, hour=0, minute=0, second=0, microsecond=0)
    datetime.datetime.now(riga_tz)

    transactions = Transaction.objects.filter(
        status=Transaction.STATUSES.ok,
        user_response_at__range=[start_date, end_date]
    ).values('link_id', 'amount')

    payment_totals_by_bank = {}
    for trans in transactions:
        link_id = trans.get('link_id')
        if trans.get('link_id') in payment_totals_by_bank:
            amount = payment_totals_by_bank.get(link_id)
            payment_totals_by_bank.update({link_id: amount + trans.get('amount')})
        else:
            payment_totals_by_bank.update({link_id: trans.get('amount')})

    payment_channel_ids = PaymentChannel.objects.all().values('id', 'title').order_by('id')

    for channel in payment_channel_ids:
        reported_totals = 0
        params = {}

        if channel.get('title') == "FirstData":
            try:
                payment_channel_object = PaymentChannel.objects.filter(pk=4).get()
                resp = requests.post(
                    payment_channel_object.server_url,
                    cert=(payment_channel_object.cert_file.path, payment_channel_object.key_file.path),
                    data={'command': 'b'},
                    verify=False, )
                params = {}
                for field in resp.text.split('\n'):
                    values = field.split(': ')
                    params.update({values[0]: values[1]})
                reported_totals = params.get('FLD_086') + params.get('FLD_088')
                params = json.dumps(params)
            except:
                continue

        DailyTransactionTotals.objects.create(
            date=None,
            channel=PaymentChannel.objects.filter(pk=channel.get('id')),
            calculated_total=payment_totals_by_bank.get(channel.get('id'), default=0),
            reported_total=reported_totals,
            params=params
        )
