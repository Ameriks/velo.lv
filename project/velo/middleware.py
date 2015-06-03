from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import cookie_date

import hashlib
import time
import uuid
import re


class JoomlaSessionMiddleware(object):

    # your desired cookie will be available in every django view
    def process_request(self, request):
        # will only add cookie if request does not have it already
        if not request.COOKIES.get('9321b987b127024eb07b497ca93226b0'):
            request.COOKIES['9321b987b127024eb07b497ca93226b0'] = hashlib.sha1(str(uuid.uuid4())).hexdigest()


    def process_response(self, request, response):
        j_cookie = request.COOKIES.get('9321b987b127024eb07b497ca93226b0', None)
        if j_cookie:
            if hasattr(request, 'session'):
                max_age = request.session.get_expiry_age()
                expires_time = time.time() + max_age
                expires = cookie_date(expires_time)

                response.set_cookie('9321b987b127024eb07b497ca93226b0',
                                j_cookie, max_age=max_age,
                                expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                                path=settings.SESSION_COOKIE_PATH,
                                secure=settings.SESSION_COOKIE_SECURE or None,
                                httponly=settings.SESSION_COOKIE_HTTPONLY or None)
        return response


class SSLRedirectMiddleware(object):
    def __init__(self):
        self.redirect_exempt = [re.compile(r) for r in settings.ALWAYS_SSL_PAGES]

    def process_request(self, request):
        if request.is_secure() and not settings.DEBUG:
            url = request.build_absolute_uri(request.get_full_path())
            for ssl_only_page_re in self.redirect_exempt:
                if ssl_only_page_re.match(request.get_full_path()):
                    return None
            if request.user.is_anonymous():
                return HttpResponseRedirect(re.sub(r'^https', 'http', url))
