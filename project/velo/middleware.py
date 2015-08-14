from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import cookie_date

import hashlib
import time
import uuid
import re


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
