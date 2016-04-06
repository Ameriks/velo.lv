# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.db.models import Count

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
