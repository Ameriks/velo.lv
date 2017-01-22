from django import forms
from django.utils.translation import ugettext as _

import requests
from requests.exceptions import ConnectionError
import math

from velo.core.models import Log


class RequestKwargModelFormMixin(object):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.request_kwargs = kwargs.pop("request_kwargs", None)
        if self.request:
            self.user = self.request.user
        super(RequestKwargModelFormMixin, self).__init__(*args, **kwargs)


class GetClassNameMixin(object):
    prepend = ''

    def get_app_label(self):
        return "%s/%s%s" % (self.get_class()._meta.app_label.lower(), self.prepend, self.get_class().__name__.lower())

    def get_class(self):
        try:
            return self.model
        except:
            return self._meta.model

    @property
    def get_class_name(self):
        return "%s%s" % (self.prepend, self.get_class().__name__)


class CleanEmailMixin(object):
    def email_validate(self, value):
        resp = None
        if len(value) > 0:
            try:
                resp = requests.get('https://api.mailgun.net/v2/address/validate',
                                    params={'api_key': 'pubkey-7049tobos-x721ipc8b3dp68qzxo3ri5', 'address': value})
                resp_json = resp.json()
                if not resp_json.get('is_valid', False):
                    msg = 'Invalid email address.'
                    if resp_json.get('did_you_mean'):
                        msg = msg + ' ' + 'Did you mean:' + resp_json.get('did_you_mean')
                    raise forms.ValidationError(msg, code='invalid_email')
            except ConnectionError:
                Log.objects.create(action='VALIDATE_EMAIL', message='Error connecting to mailgun.net.')
            except ValueError:  # in case json cannot be decoded
                Log.objects.create(action='VALIDATE_EMAIL', message=resp.text if resp else 'No response')

        return value

    def clean_email(self):
        value = self.cleaned_data.get('email', '')
        self.email_validate(value)
        return value


class CleanSSNMixin(object):
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
        return value
