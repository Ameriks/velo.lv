from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
import datetime
from django.utils.safestring import mark_safe
from core.tasks import send_email_confirmation

class UserEmailValidMiddleware(object):
    def process_request(self, request):
        # will only add cookie if request does not have it already
        if request.user.is_authenticated():
            request.user.message_set = True

            change_email_url = reverse('email_change_view')

            if request.user.email_status == request.user.EMAIL_NOT_VALIDATED:
                if not request.user.email_validation_expiry:
                    send_email_confirmation.delay(request.user.id)
                messages.info(request, mark_safe((
                    'We sent email verification to your email address: {0}. Please verify that your email address is active. <a href="{1}">Resend</a><a href="{2}">Change email</a>'.format(request.user.email, '', change_email_url))))
