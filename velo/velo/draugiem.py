from social.backends.base import BaseAuth
from social.exceptions import AuthCanceled

import hashlib
import urllib


class DraugiemPassportAPI(BaseAuth):
    name = 'draugiem'
    ID_KEY = 'uid'

    LOGIN_URL = 'http://api.draugiem.lv/authorize/'
    ACCESS_TOKEN_URL = 'http://api.draugiem.lv/json/'

    def get_user_details(self, response):
        uid = response.get('uid')
        user_data = response.get('users').get(uid)
        # username = user_data.get('screen_name', '')
        return {
            'username': '%s.%s' % (user_data.get('name').lower(), user_data.get('surname').lower()),
            'email': '',
            'fullname': '',
            'first_name': user_data.get('name')
                                if 'name' in user_data else '',
            'last_name': user_data.get('surname')
                                if 'surname' in user_data else ''
        }

    def user_data(self, access_token, *args, **kwargs):
        return self.data

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        return response

    def auth_url(self):
        hash = hashlib.md5('%s%s' % (self.setting('KEY'), self.redirect_uri)).hexdigest()
        params = {
            'app': self.setting('APP_ID'),
            'hash': hash,
            'redirect': self.redirect_uri
        }
        return '%s?%s' % (self.LOGIN_URL, urllib.urlencode(params))

    def auth_complete(self, *args, **kwargs):
        if self.data.get('dr_auth_status', None) == 'failed':
            raise AuthCanceled(self)

        if self.data.get('dr_auth_status', None) != 'ok' or not self.data.get('dr_auth_code', None):
            raise ValueError('draugiem.lv authentication failed: invalid status returned')

        data = {
            'action': 'authorize',
            'app': self.setting('KEY'),
            'code': self.data.get('dr_auth_code'),
        }
        response = self.get_json(self.ACCESS_TOKEN_URL, data=data, method='POST')
        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def uses_redirect(self):
        return True