import random
import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.views.generic import TemplateView, DetailView, ListView, RedirectView, UpdateView
from django.utils import timezone
from django.db.models import Count, F

from django_downloadview import ObjectDownloadView
from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError

from velo.advert.models import Banner
from velo.core.forms import UserProfileForm
from velo.core.models import Competition, Map, User
from velo.gallery.models import Album, Video, Photo
from velo.news.models import News
from velo.supporter.models import CompetitionSupporter
from velo.velo.mixins.views import SetCompetitionContextMixin, CacheControlMixin, NeverCacheMixin


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("account:applications")


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        try:
            first_id = Competition.objects.filter(is_in_menu=True).order_by('id')[0].id
        except:
            first_id = 1

        calendar = Competition.objects.filter(id__gte=first_id).select_related('parent').extra(select={'is_past': "core_competition.competition_date < now()::date  - interval '3 days'"}).order_by('is_past', 'competition_date', '-name_lv')
        context.update({'calendar': calendar})

        parent_ids = []
        for competition in calendar:
            parent_ids.append(competition.parent_id)
        context.update({'parent_ids': parent_ids})

        cache_key = 'image_top_%s' % get_language()
        front_photo = cache.get(cache_key, None)
        if front_photo is None:
            front_photo = False
            photo = Photo.objects.filter(album_id=144)
            if not photo:
                photo = Photo.objects.all()
            if photo:
                front_photo = photo[0]
            cache.set(cache_key, front_photo, 60 * 30)  # Cache for 30 minutes

        if front_photo:
            context.update({'front_photo': front_photo})


        context.update({'news_list': News.objects.published().filter(language=get_language())[:4]})

        showed_index_banner = self.request.session.get('showed_index_banner', None)
        current_time = int(time.time())
        if not showed_index_banner or int(showed_index_banner) + 60*5 < current_time:
            cache_key = 'banners_top_%s' % get_language()
            banner_top = cache.get(cache_key, None)
            if banner_top is None:
                banner_top = Banner.objects.filter(status=1, location=Banner.BANNER_LOCATIONS.top, show_start__lte=timezone.now(), show_end__gte=timezone.now(), language__in=['', get_language()]).values('id', 'kind', 'banner', 'banner_url', 'competition', 'converted', 'show_end', 'show_start', 'url', 'height', 'width')
                cache.set(cache_key, banner_top, 60*30)  # Cache for 30 minutes

            if banner_top:
                banner_top = random.choice(banner_top)
                Banner.objects.filter(id=banner_top.get('id')).update(view_count=F('view_count') + 1)

            context.update({'banner_top': banner_top})
            self.request.session['showed_index_banner'] = current_time



        def active_index_func():
            next_competition = Competition.objects.filter(competition_date__gt=timezone.now()).order_by('competition_date', '-name_lv')[:1]
            if not next_competition:
                next_competition = Competition.objects.order_by('-competition_date')[:1]

            slide_to = 0
            active_indexes = []
            for index in range(0, len(calendar)):
                if next_competition and calendar[index].id == next_competition[0].id:
                    slide_to = len(active_indexes)
                    active_indexes.append(index)
                elif (not active_indexes or index - active_indexes[-1] > 2) and index % 3 == 2 and index > 0:
                    active_indexes.append(index-2)
                elif index == len(calendar)-1 and (index - active_indexes[-1] > 2):  # LAST ELEMENT
                    active_indexes.append(index - (index - active_indexes[-1]) % 3)

            return active_indexes, 0

        context.update({'active_indexes': active_index_func})

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

        # Showing 6 albums from current type of competition, first showing albums from current competition
        cache_key = 'competition_detail_albums_%i' % self.competition.id
        albums = cache.get(cache_key, None)
        if albums is None:
            albums_query = Album.objects.filter(competition__tree_id=self.object.tree_id, is_processed=True).extra(select={
                'is_current': "CASE WHEN competition_id = %s Then true ELSE false END"
            }, select_params=(self.object.id,)).order_by('-is_current', '-gallery_date', '-id')[:6]
            try:
                albums = [(obj.id,  obj.primary_image.image.get_thumbnail(aliases.get('thumb', target=obj.primary_image.image), silent_template_exception=True).url) for obj in albums_query]
                cache.set(cache_key, albums)
            except InvalidImageFormatError:
                albums = []
        context.update({'galleries': albums})

        # Showing latest featured video in current/parent competition
        cache_key = 'competition_detail_video_%i' % self.competition.id
        video = cache.get(cache_key, None)
        if video is None:
            try:
                video = Video.objects.filter(competition_id__in=self.object.get_ids()) \
                    .filter(status=1, is_featured=True).order_by('-id')[0].url_embed
                cache.set(cache_key, video)
            except IndexError:
                cache.set(cache_key, False)
                video = None
        context.update({'video': video})


        return context


class MapGPXDownloadView(ObjectDownloadView):
    model = Map
    file_field = 'gpx'
    pk_url_kwarg = 'pk2'
    mimetype = 'application/gpx+xml'


class MapView(SetCompetitionContextMixin, ListView):
    model = Map
    template_name = 'core/maps.html'

    def get_queryset(self):
        queryset = super(MapView, self).get_queryset()

        if not self.competition:
            return self.model.objects.none()

        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        return queryset


class CalendarView(CacheControlMixin, TemplateView):
    template_name = 'core/calendar_view.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)

        now = timezone.now()

        year = now.year
        competition = Competition.objects.filter(competition_date__gte=now).order_by('competition_date')
        if competition:
            year = competition[0].competition_date.year

        this_year = Competition.objects.filter(competition_date__year=year).order_by(
            'competition_date', 'id').select_related('parent')

        cache_key = 'banners_calendar_%s' % get_language()
        side_banner = cache.get(cache_key, None)
        if side_banner is None:
            side_banner = Banner.objects.filter(status=1, location=Banner.BANNER_LOCATIONS.calendar, show_start__lte=timezone.now(), show_end__gte=timezone.now(), language__in=['', get_language()]).values('id', 'kind', 'banner', 'banner_url', 'competition', 'converted', 'show_end', 'show_start', 'url', 'height', 'width')
            cache.set(cache_key, side_banner, 60*30)  # Cache for 30 minutes

        if side_banner:
            side_banner = random.choice(side_banner)
            Banner.objects.filter(id=side_banner.get('id')).update(view_count=F('view_count') + 1)

        context.update({
            'this_year': this_year,
            'side_banner': [side_banner, ],
        })



        return context


class ProfileView(NeverCacheMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'core/user_registration.html'

    def get_object(self, queryset=None):
        return self.request.user
