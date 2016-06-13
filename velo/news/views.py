from random import shuffle

from django.core.cache import cache
from django.utils import timezone
from django.utils.translation.trans_null import get_language
from django.views.generic import DetailView, ListView
from django.db.models import Count, F


from velo.advert.models import Banner
from velo.core.models import Competition
from velo.news.models import Notification, News
from velo.velo.mixins.views import SetCompetitionContextMixin


class NotificationView(DetailView):
    model = Notification


class NewsMixin(SetCompetitionContextMixin):
    def get_context_data(self, **kwargs):
        context = super(NewsMixin, self).get_context_data(**kwargs)

        context.update(
            {'latest_posts': News.objects.filter(published_on__lte=timezone.now()).order_by('-published_on')[:4]})

        competition_ids_with_news = News.objects.exclude(competition=None).order_by('competition_id').values(
            'competition_id').annotate(Count('id')).values_list('competition_id')

        context.update({'competitions': Competition.objects.filter(id__in=competition_ids_with_news).order_by(
            '-competition_date')})

        return context


class NewsListView(NewsMixin, ListView):
    model = News
    paginate_by = 10
    paginate_orphans = 5

    def get_queryset(self):
        queryset = super(NewsListView, self).get_queryset()

        queryset = queryset.order_by('-published_on').filter(published_on__lte=timezone.now())

        if self.competition:
            queryset = queryset.filter(competition_id__in=(self.competition.id, self.competition.parent_id))

        return queryset


class NewsDetailView(NewsMixin, DetailView):
    model = News
    pk_url_kwarg = 'pk2'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cache_key = 'banners_news_' % get_language()
        side_banner = cache.get(cache_key, None)
        if side_banner is None:
            side_banner = list(Banner.objects.filter(status=1, location=Banner.BANNER_LOCATIONS.news, show_start__lte=timezone.now(), show_end__gte=timezone.now(), language__in=['', get_language()]).values('id', 'kind', 'banner', 'banner_url', 'competition', 'converted', 'show_end', 'show_start', 'url', 'height', 'width'))
            cache.set(cache_key, side_banner, 60*30)  # Cache for 30 minutes

        if side_banner and len(side_banner) > 1:
            shuffle(side_banner)
            side_banner = side_banner[:3]
            Banner.objects.filter(id__in=[obj.get('id') for obj in side_banner]).update(view_count=F('view_count') + 1)

        context.update({
            'side_banner': side_banner,
        })
        return context
