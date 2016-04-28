# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.views.generic import TemplateView, DetailView, ListView, RedirectView
from django.utils import timezone

from django_downloadview import ObjectDownloadView
from braces.views import LoginRequiredMixin
from velo.core.models import Competition, Map
from velo.gallery.models import Album, Video, Photo
from velo.news.models import News
from velo.supporter.models import CompetitionSupporter
from velo.velo.mixins.views import SetCompetitionContextMixin, CacheControlMixin


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:applications")


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        calendar = Competition.objects.filter(competition_date__year=timezone.now().year).order_by(
            'competition_date').select_related('parent')
        context.update({'calendar': calendar})

        next_competition = Competition.objects.filter(competition_date__gt=timezone.now()).order_by('competition_date')[
                           :1]
        if not next_competition:
            next_competition = Competition.objects.order_by('-competition_date')[:1]
        context.update({'next_competition': next_competition[0]})

        context.update({'front_photo': Photo.objects.filter(album_id=144)[0]})

        context.update({'news_list': News.objects.published().filter(language=get_language())[:4]})

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
        albums = Album.objects.filter(competition__tree_id=self.object.tree_id, is_processed=True).extra(select={
            'is_current': "CASE WHEN competition_id = %s Then true ELSE false END"
        }, select_params=(self.object.id,)).order_by('-is_current', '-gallery_date', '-id')[:6]
        context.update({'galleries': albums})

        # Showing latest featured video in current/parent competition
        try:
            video = Video.objects.filter(competition_id__in=self.object.get_ids()) \
                .filter(status=1, is_featured=True).order_by('-id')[0]
        except IndexError:
            video = None
        context.update({'video': video})

        # Supporters
        context.update({'supporters': CompetitionSupporter.objects \
                       .filter(competition_id__in=self.object.get_ids()) \
                       .order_by('-support_level', 'ordering', '-label') \
                       .select_related('supporter')
                        })

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
        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        return queryset


class CalendarView(CacheControlMixin, TemplateView):
    template_name = 'core/calendar_view.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)

        now = timezone.now()

        this_year = Competition.objects.filter(competition_date__year=now.year).order_by(
            'competition_date').select_related('parent')

        context.update({
            'this_year': this_year,
        })

        return context
