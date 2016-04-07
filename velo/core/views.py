# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import redirect, render_to_response, resolve_url
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, RedirectView
from django.contrib.auth import logout
from django.template.context import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login

from django_downloadview import ObjectDownloadView
from braces.views import LoginRequiredMixin
import re

from velo.core.forms import UserCreationForm, ChangeEmailForm, ChangePasswordForm, UserProfileForm, NewEmailForm, \
    AuthenticationFormCustom
from velo.core.models import Competition, Map, User
from velo.core.tasks import send_email_confirmation
from velo.gallery.models import Album, Video
from velo.news.models import News
from velo.results.models import DistanceAdmin
from velo.supporter.models import Supporter
from velo.velo.mixins.views import SetCompetitionContextMixin, RequestFormKwargsMixin, SetPleaseVerifyEmail, \
    CacheControlMixin


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:applications")


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        context.update({'competitions': Competition.objects.filter(is_in_menu=True).order_by('frontpage_ordering')})

        next_competition = Competition.objects.filter(competition_date__gt=timezone.now()).order_by('competition_date')[
                           :1]
        if not next_competition:
            next_competition = Competition.objects.order_by('-competition_date')[:1]

        context.update({'next_competition': next_competition[0]})

        context.update({'news_list': News.objects.published()[:4]})

        context.update({'supporters': Supporter.objects.filter(is_agency_supporter=True).order_by("?")})

        return context


class CompetitionDetail(SetCompetitionContextMixin, DetailView):
    model = Competition

    def get_context_data(self, **kwargs):
        context = super(CompetitionDetail, self).get_context_data(**kwargs)
        context.update({'news_list': News.objects.published(self.object.get_ids())[:3]})

        if self.object.level == 2:
            calendar = Competition.objects.filter(parent_id=self.object.parent_id)
        else:
            children = self.object.get_children()
            if children:
                calendar = children
            else:
                calendar = [self.object, ]
        context.update({'calendar': calendar})

        context.update({'galleries': Album.objects.filter(
            competition_id__in=[self.object.id, self.object.parent_id]).filter(is_processed=True).order_by('-id')[:5]})
        context.update({'videos': Video.objects.filter(
            competition_id__in=[self.object.id, self.object.parent_id]).filter(status=1).order_by('-id')[:3]})

        return context


class MapGPXDownloadView(ObjectDownloadView):
    model = DistanceAdmin
    file_field = 'gpx'
    pk_url_kwarg = 'pk2'
    mimetype = 'application/gpx+xml'


class MapView(SetCompetitionContextMixin, ListView):
    model = Map
    template_name = 'core/maps.html'

    def get_queryset(self):
        queryset = super(MapView, self).get_queryset()
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        return queryset

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)

        distanceadmin = DistanceAdmin.objects.filter(competition=self.competition).exclude(gpx=None).select_related(
            'competition', 'distance', 'competition__parent').order_by('distance__id')

        context.update({'distanceadmin': distanceadmin})

        return context


class UserRegistrationView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'core/user_registration.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        messages.success(self.request, _('User created. Now you can login in your account.'))
        return super(UserRegistrationView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            logout(request)
        return super(UserRegistrationView, self).get(request, *args, **kwargs)


class UserEmailConfirm(DetailView):
    model = User
    slug_field = 'email_validation_code'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object:
            self.object.email_status = User.EMAIL_VALID
            self.object.email_validation_code = ''
            self.object.save()
            messages.success(request, _('Email is validated. Thank you!'))
        return HttpResponseRedirect('/')


class ChangeEmailView(SetPleaseVerifyEmail, RequestFormKwargsMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = ChangeEmailForm
    template_name = 'core/user_registration.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user


class ChangePasswordView(SetPleaseVerifyEmail, RequestFormKwargsMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = ChangePasswordForm
    template_name = 'core/password_change_form.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(SetPleaseVerifyEmail, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'core/user_registration.html'

    def get_object(self, queryset=None):
        return self.request.user


class ResendEmailView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        send_email_confirmation(user.id)
        messages.success(request, _('Email resent. Please check spam folder if email is not in Inbox.'))
        return HttpResponseRedirect(reverse('accounts:profile'))


def new_user_email_view(request):
    form = NewEmailForm
    if request.method == 'POST' and request.POST.get('email'):
        form = NewEmailForm(data=request.POST)
        if form.is_valid():
            request.session['partial_email'] = form.cleaned_data.get('email')
            backend = request.session['partial_pipeline']['backend']
            return redirect('social:complete', backend=backend)
    return render_to_response('core/user_registration.html', {}, RequestContext(request, {'form': form}))


class CalendarView(CacheControlMixin, TemplateView):
    template_name = 'core/calendar_view.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)

        now = timezone.now()

        this_year = Competition.objects.filter(competition_date__year=now.year).order_by(
            'competition_date').select_related('parent')
        next_year = Competition.objects.filter(competition_date__year=(now.year + 1)).order_by('competition_date')

        context.update({
            'this_year': this_year,
            'next_year': next_year,
        })

        return context


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationFormCustom,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if not request.is_secure() and not settings.DEBUG:
        url = request.build_absolute_uri(request.get_full_path())
        return HttpResponsePermanentRedirect(re.sub(r'^http', 'https', url))

    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('accounts:profile'))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
