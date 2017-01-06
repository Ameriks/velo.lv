from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

import requests
import datetime
import urllib

from django.utils.http import urlencode

from velo.payment.models import Transaction
import velo.payment.utils


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
        digest = r''
        for value in self.create_ordered_values(values, kind):
            digest += str(len(value)).rjust(3, u'0')
            digest += str(value)
        return digest.encode('utf-8')


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
            return HttpResponseRedirect(self.transaction.link.fail_url.format(urllib.quote(self.transaction.code)))
        else:
            self.transaction.user_response = status_dict.get('RESULT')
            self.transaction.returned_user_ip = velo.payment.utils.get_client_ip(request)
            self.transaction.user_response_at = timezone.now()
            self.transaction.status = self.get_transaction_status(status_dict.get('RESULT'))
            self.transaction.save()
            if self.transaction.payment_set.content_type.model == 'application':
                return HttpResponseRedirect(
                    reverse('application_ok' if status_dict.get('RESULT') == 'OK' else 'application_pay',
                            kwargs={'slug': self.transaction.payment_set.content_object.code}
                            ))
            elif self.transaction.payment_set.content_type.model == 'team':
                return HttpResponseRedirect(
                    reverse('account:team' if status_dict.get('RESULT') == 'OK' else 'account:team_pay',
                            kwargs={'pk2': self.transaction.payment_set.content_object.id}
                            ))

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
            return False
        else:
            if 'error: ' in resp.text:
                return False

            dict_obj = {}
            for _ in resp.text.split('\n'):
                key, value = _.split(': ')
                dict_obj.update({key: value})
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
            return HttpResponseRedirect(self.transaction.link.fail_url)

    def request_transaction_code(self):
        transaction_id = None

        if self.transaction.language == 'LVL':
            language = "lv"
        else:
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

        if resp.text[0:14] == 'TRANSACTION_ID':
            transaction_id = resp.text.strip()[16:]
            self.transaction.external_code = transaction_id
            self.transaction.external_code_requested = datetime.datetime.now()
            self.transaction.save()
            return transaction_id
        else:
            return transaction_id


class Swedbank(BankIntegrationBase):
    pass


class IBanka(BankIntegrationBase):
    pass
