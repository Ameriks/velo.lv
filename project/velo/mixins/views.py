from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.cache import patch_response_headers
from django.views.generic import ListView, CreateView, UpdateView
from django_tables2 import SingleTableView
from django.utils.safestring import mark_safe
from django.utils import timezone
import datetime
from advert.models import FlashBanner
from core.models import Competition, Distance
from django.core.cache import cache
from velo.utils import load_class
from core.tasks import send_email_confirmation
from django.utils.translation import ugettext_lazy as _


class CacheControlMixin(object):
    cache_timeout = 60*5

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        response = super(CacheControlMixin, self).dispatch(*args, **kwargs)
        patch_response_headers(response, self.get_cache_timeout())
        return response


class SetPleaseVerifyEmail(object):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            request.user.message_set = True

            change_email_url = reverse('accounts:email_change_view')
            resend_email_url = reverse('accounts:email_resend_view')

            if request.user.email_status == request.user.EMAIL_NOT_VALIDATED:
                if not request.user.email_validation_expiry:
                    request.user.email_validation_expiry = timezone.now() + datetime.timedelta(days=1)
                    request.user.save()
                    send_email_confirmation.delay(request.user.id)
                messages.info(request, mark_safe(_(
                    'We sent email verification to your email address: {0}. Please verify that your email address is active. <a href="{1}">Resend</a> or <a href="{2}">Change email</a>'.format(request.user.email, resend_email_url, change_email_url))))
        return super(SetPleaseVerifyEmail, self).get(request, *args, **kwargs)


class RequestFormKwargsMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RequestFormKwargsMixin, self).get_form_kwargs()
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"request": self.request})
        kwargs.update({"request_kwargs": self.kwargs})
        return kwargs


class SetCompetitionContextMixin(object):
    competition = None
    distances = None
    distance = None
    competition_class = None

    def get_competition_class(self):
        if not self.competition_class:
            class_ = load_class(self.competition.processing_class)
            self.competition_class = class_(competition=self.competition)
        return self.competition_class


    def get_banners(self):
        if not self.competition:
            return None
        return FlashBanner.objects.filter(status=1).filter(competition__in=self.competition.get_ids())


    def set_competition(self, pk):
        if self.competition:
            return self.competition

        cache_key = 'competition_%s' % pk
        self.competition = cache.get(cache_key)
        if not self.competition:
            try:
                self.competition = Competition.objects.get(id=pk)
            except Competition.DoesNotExist:
                return None
            cache.set(cache_key, self.competition)
        return self.competition

    def set_distances(self, all=True, only_w_teams=False, have_results=False):
        if self.distances:
            return self.distances
        if only_w_teams:
            cache_key = 'competition_distances_w_teams_%s' % self.competition.id
        elif have_results:
            cache_key = 'competition_distances_w_results_%s' % self.competition.id
        else:
            cache_key = 'competition_distances_%s' % self.competition.id
        self.distances = cache.get(cache_key)
        if not self.distances:
            self.distances = self.competition.get_distances()
            if only_w_teams:
                self.distances = self.distances.filter(can_have_teams=True)
            elif have_results:
                self.distances = self.distances.filter(have_results=True)

            cache.set(cache_key, self.distances)
        return self.distances

    def set_distance(self, pk):
        if pk:

            try:
                pk = int(pk)
                cache_key = 'distance_%s' % pk
                self.distance = cache.get(cache_key)
                if not self.distance:
                    self.distance = Distance.objects.get(id=pk)
                    cache.set(cache_key, self.distance)
                return self.distance
            except:
                pass

        self.set_distances()  # Set distances if not set
        if self.distances:
            self.distance = self.distances[0]  # Set primary distance to first

        return self.distance

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        return super(SetCompetitionContextMixin, self).get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        return super(SetCompetitionContextMixin, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SetCompetitionContextMixin, self).get_context_data(**kwargs)
        if self.competition:
            context.update({'competition': self.competition})
        if self.distances:
            context.update({'distances': self.distances})
        if self.distance:
            context.update({'distance_active': self.distance})

        context.update({'banners': self.get_banners()})

        return context


class SingleTableViewWithRequest(SetCompetitionContextMixin, SingleTableView):
    add_link = None

    def table_order_by(self):
        return None

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        table = self.get_table(request=self.request, request_kwargs=self.kwargs, order_by=self.table_order_by())
        context[self.get_context_table_name(table)] = table
        context.update({'competition': self.competition})
        context.update({'add_link': self.add_link})
        return context


class CreateViewWithCompetition(RequestFormKwargsMixin, SetCompetitionContextMixin, CreateView):
    pass

class UpdateViewWithCompetition(RequestFormKwargsMixin, SetCompetitionContextMixin, UpdateView):
    pass