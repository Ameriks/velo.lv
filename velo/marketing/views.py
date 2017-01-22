from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView

from braces.views import CsrfExemptMixin, SuperuserRequiredMixin
import hashlib
import hmac

from velo.core.models import Log
from velo.marketing.forms import SendyCreateForm
from velo.marketing.models import SMS
from velo.marketing.tasks import copy_mc_template
from velo.registration.models import Participant, Application


class SMSReportView(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        smsid = request.GET.get('smId')
        status = request.GET.get('status')

        sms = SMS.objects.filter(response=smsid).exclude(status="DELIVRD")
        if sms:
            sms.update(status=status)

        return HttpResponse('ok')


def mailgun_verify(api_key, token, timestamp, signature):
    return signature == hmac.new(
        key=api_key,
        msg='{}{}'.format(timestamp, token),
        digestmod=hashlib.sha256).hexdigest()


class TestEmailTemplate(SuperuserRequiredMixin, TemplateView):
    template_name = 'registration/email/rm2015/number_email.html'

    def get_context_data(self, **kwargs):
        context = super(TestEmailTemplate, self).get_context_data(**kwargs)
        participants = Participant.objects.filter(competition_id=47, slug="agris-ameriks-1987")

        participants = Application.objects.get(id=33728).participant_set.order_by('primary_number__number')

        primary_competition = participants[0].competition

        context.update({
            'participants': participants,
            'domain': settings.MY_DEFAULT_DOMAIN,
            'competition': primary_competition,
            'application': True,
        })

        return context


class CreateSendyView(PermissionRequiredMixin, TemplateView):
    template_name = "bootstrap/manager/form.html"
    permission_required = "marketing.can_update_marketing"

    def get_form(self):
        return SendyCreateForm(data=self.request.POST)

    def get_context_data(self, **kwargs):
        context = super(CreateSendyView, self).get_context_data(**kwargs)
        context.update({'form': self.get_form(), "title": "Izveidot Sendy"})
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            template_id = int(form.cleaned_data.get('template'))
            copy_mc_template.delay(template_id, dict(form.fields['template'].choices).get(template_id))
            return HttpResponseRedirect("https://sendy.velo.lv/app?i=1")
        else:
            messages.error(request, "Kļūda.")
            return super(CreateSendyView, self).get(request, *args, **kwargs)
