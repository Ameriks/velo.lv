from django.core.urlresolvers import reverse
from django.db.models import Q, Min
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.views.generic import ListView, TemplateView, DetailView
from django.db import connection
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

import datetime
from django_tables2 import SingleTableView

from velo.core.models import Competition
from velo.results.models import Result, SebStandings, TeamResultStandings
from velo.results.tables import ResultTeamStandingTable
from velo.team.models import MemberApplication
from velo.velo.mixins.views import SetCompetitionContextMixin
from velo.velo.utils import load_class


class ResultAllView(TemplateView):
    template_name = 'results/all_view.html'

    def get_context_data(self, **kwargs):
        context = super(ResultAllView, self).get_context_data(**kwargs)

        years = []
        for year in range(2014, datetime.date.today().year + 1):
            years.append((year, _("Year %(year)i Results") % {"year": year}))

        competitions = Competition.objects.filter(Q(competition_date__lt=timezone.now())|Q(complex_payment_enddate__lt=timezone.now())).order_by('competition_date')

        context.update({'years': years, 'competitions': competitions})

        return context

    def post(self, request, *args, **kwargs):
        try:
            competition = Competition.objects.get(id=request.POST.get('competition'))
            if competition.get_children():
                return HttpResponseRedirect(reverse("competition:standings_list", kwargs={'pk': competition.id}))
            return HttpResponseRedirect(reverse("competition:result_distance_list", kwargs={'pk': competition.id}))
        except:
            return self.get(request, *args, **kwargs)


class ResultList(SetCompetitionContextMixin, SingleTableView):
    """
    Class used to display participant result.
    Optimized view
    """
    model = Result
    template_name = 'results/participant.html'
    paginate_by = 100

    def get_table_class(self):
        try:
            return self.get_competition_class().get_result_table_class(self.distance, self.request.GET.get('group', None))
        except ValueError as e:
            raise Http404()

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))

        if not self.competition:
            raise Http404

        self.set_distances(have_results=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(ResultList, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ResultList, self).get_context_data(**kwargs)
        context.update({'groups': self.get_competition_class().groups.get(self.distance.id, ())})
        return context

    def get_queryset(self):
        queryset = super(ResultList, self).get_queryset()

        if self.distance:
            queryset = queryset.filter(participant__distance=self.distance)

        if self.request.GET.get('group', None):
            queryset = queryset.filter(participant__group=self.request.GET.get('group', None))
        if self.request.GET.get('gender', None):
            queryset = queryset.filter(participant__gender=self.request.GET.get('gender', None))

        search = self.request.GET.get('search', None)
        if search:
            search_slug = slugify(search)
            queryset = queryset.filter(
                Q(participant__slug__icontains=search_slug) | Q(number__number__icontains=search_slug) | Q(
                    participant__team_name__icontains=search.upper())).filter(participant__is_shown_public=True)

        queryset = queryset.filter(competition_id__in=self.competition.get_ids())
        try:
            queryset = queryset.extra(select=self.get_competition_class().result_select_extra(self.distance.id))
        except ValueError:
            raise Http404

        queryset = queryset.select_related('competition', 'participant__distance', 'participant',
                                           'participant__bike_brand',
                                           'participant__team', 'number', 'leader')

        return queryset


class SebStandingResultList(SetCompetitionContextMixin, SingleTableView):
    """
    Class used to display participant standings.
    Optimized view
    """
    model = SebStandings
    template_name = 'results/participant_standing.html'
    paginate_by = 100

    def get_table_class(self):
        try:
            return self.get_competition_class().get_standing_table_class(self.distance, self.request.GET.get('group', None))
        except:
            raise Http404

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(have_results=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(SebStandingResultList, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SebStandingResultList, self).get_context_data(**kwargs)
        context.update({'groups': self.get_competition_class().groups.get(self.distance.id, ())})
        return context

    def get_queryset(self):
        queryset = super(SebStandingResultList, self).get_queryset()

        if self.distance:
            queryset = queryset.filter(distance=self.distance)

        if self.request.GET.get('group', None):
            queryset = queryset.filter(participant__group=self.request.GET.get('group', None))
        if self.request.GET.get('gender', None):
            queryset = queryset.filter(participant__gender=self.request.GET.get('gender', None))

        search = self.request.GET.get('search', None)
        if search:
            search_slug = slugify(search)
            queryset = queryset.filter(Q(participant__slug__icontains=search_slug) | Q(
                participant__primary_number__number__icontains=search_slug) | Q(
                participant__team_name__icontains=search.upper())).filter(participant__is_shown_public=True)

        queryset = queryset.filter(competition_id__in=self.competition.get_ids())

        queryset = queryset.select_related('competition', 'distance', 'participant', 'participant__primary_number',
                                           'participant__team')

        return queryset


class SebTeamResultList(SetCompetitionContextMixin, ListView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    model = TeamResultStandings
    template_name = 'results/team.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        distance = self.request.GET.get('distance', None)
        if distance:
            distance = distance[1:] if distance.startswith("S") else distance
        self.set_distance(distance)

        return super(SebTeamResultList, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(SebTeamResultList, self).get_queryset()
        queryset = queryset.filter(team__member__memberapplication__competition=self.competition,
                                   team__member__memberapplication__kind=MemberApplication.KIND_PARTICIPANT,
                                   team__member__memberapplication__participant__result__competition=self.competition)

        queryset = queryset.filter(team__distance=self.distance)

        index = self.get_competition_class().competition_index  # Get stage index
        queryset = queryset.order_by('-points%i' % index, '-team__is_featured', 'team__title',
                                     '-team__member__memberapplication__participant__result__points_distance',
                                     'team__member__memberapplication__participant__primary_number__number', )

        queryset = queryset.values_list('team__id', 'team__title', 'team__is_featured',
                                        'team__teamresultstandings__points%i' % index,
                                        'team__member__first_name', 'team__member__last_name', 'team__member__birthday',
                                        'team__member__memberapplication__participant__primary_number__number',
                                        'team__member__memberapplication__participant__result__points_distance',
                                        )

        if self.request.GET.get('distance', "").startswith("S"):
            queryset = queryset.filter(team__is_w=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("distance", "").startswith("S"):
            context.update({"is_w": True})
        return context


class SebTeamResultStandingList(SetCompetitionContextMixin, SingleTableView):
    """
    This class is used to view team standings.
    Optimized class.
    """
    model = TeamResultStandings
    template_name = 'results/team_standing.html'
    paginate_by = 100

    def get_table_class(self):
        return ResultTeamStandingTable

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        distance = self.request.GET.get('distance', None)
        if distance:
            distance = distance[1:] if distance.startswith("S") else distance
        self.set_distance(distance)

        return super(SebTeamResultStandingList, self).get(*args, **kwargs)

    def get_queryset(self):
        queryset = super(SebTeamResultStandingList, self).get_queryset()

        queryset = queryset.filter(team__distance=self.distance).order_by('-points_total', '-team__is_featured',
                                                                          'team__title')
        if self.request.GET.get("distance", "").startswith("S"):
            queryset = queryset.filter(team__is_w=True)
        queryset = queryset.select_related('team')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("distance", "").startswith("S"):
            context.update({"is_w": True})
        return context


class TeamResultsByTeamName(SetCompetitionContextMixin, TemplateView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    template_name = 'results/team_by_teamname.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        self.set_distances(only_w_teams=True)  # Based on self.competition
        self.set_distance(self.request.GET.get('distance', None))

        return super(TeamResultsByTeamName, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(TeamResultsByTeamName, self).get_context_data(**kwargs)

        cache_key = 'team_results_by_name_%i_%i' % (self.competition.id, self.distance.id)

        default_timeout = 60 * 30
        if self.competition.competition_date == datetime.date.today():
            default_timeout = 60
        print(default_timeout)

        object_list = cache.get(cache_key)
        if not object_list:
            cursor = connection.cursor()
            cursor.execute("""
    Select *, DATE_TRUNC('second', total) from (
    Select kopa.team_name_slug, count(*) counter, sum(kopa.time) total
    from (
    Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) kopa group by kopa.team_name_slug
    having count(*)>1
    order by total
    ) team
    left outer join
    (
    Select p.team_name, p.team_name_slug, p.time,p.first_name,p.last_name,p.birthday,p.team_name,p.number from (
    SELECT
        a.*,
        r.time,
        nr.number,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        left outer join registration_number nr on nr.id = a.primary_number_id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %s
        order by a.team_name_slug, r.time
    ) p where p.row <= 4
    ) participant on team.team_name_slug = participant.team_name_slug
    order by counter desc, total, team.team_name_slug, time
    """, [self.distance.id, self.distance.id])
            object_list = cursor.fetchall()
            cache.set(cache_key, object_list, default_timeout)

        context.update({
            'object_list': object_list,
        })
        return context


class TeamResultsByTeamNameBetweenDistances(SetCompetitionContextMixin, TemplateView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    template_name = 'results/team_by_teamname_between_distances.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))

        return super(TeamResultsByTeamNameBetweenDistances, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super(TeamResultsByTeamNameBetweenDistances, self).get_context_data(**kwargs)

        cache_key = 'team_results_by_name_btw_distances_%i' % self.competition.id

        default_timeout = 60 * 30
        if self.competition.competition_date == datetime.date.today():
            default_timeout = 60
        print(default_timeout)

        object_list = cache.get(cache_key)
        if not object_list:
            distance_ids = {
                "v": self.competition.distance_set.get(kind="V").id,
                "s": self.competition.distance_set.get(kind="S").id,
                "t": self.competition.distance_set.get(kind="T").id,
            }

            cursor = connection.cursor()
            cursor.execute("""
    Select team.*, participant.*, distance.name, DATE_TRUNC('second', total) from (
    Select kopa.team_name_slug, count(*) counter, sum(kopa.time) total
    from (

    (Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(v)i
        order by a.team_name_slug, r.time
    ) p where p.row <= 2)
    UNION
    (Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(s)i
        order by a.team_name_slug, r.time
    ) p where p.row <= 2)
    UNION
    (Select p.team_name_slug, p.time from (
    SELECT
        a.team_name_slug,
        r.time,
        row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
    FROM
        registration_participant a
        left outer join results_result r on r.participant_id = a.id
        where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(t)i and a.gender='F'
        order by a.team_name_slug, r.time
    ) p where p.row <= 1)


    ) kopa group by kopa.team_name_slug
    having count(*)=5
    order by total
    ) team
    left outer join
    (
    Select p.team_name, p.team_name_slug, p.time,p.first_name,p.last_name,p.birthday,p.team_name,p.number,p.distance_id from (

	(SELECT * from
	    (SELECT
		a.*,
		r.time,
		nr.number,
		row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
	    FROM
		registration_participant a
		left outer join results_result r on r.participant_id = a.id
		left outer join registration_number nr on nr.id = a.primary_number_id
		where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(v)i
		order by a.team_name_slug, r.time
        ) x where x.row <= 2)
		UNION
	(SELECT * from
	    (SELECT
		a.*,
		r.time,
		nr.number,
		row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
	    FROM
		registration_participant a
		left outer join results_result r on r.participant_id = a.id
		left outer join registration_number nr on nr.id = a.primary_number_id
		where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(s)i
		order by a.team_name_slug, r.time
        ) x where x.row <= 2)
		UNION
	(SELECT * from
	    (SELECT
		a.*,
		r.time,
		nr.number,
		row_number() OVER (PARTITION BY team_name_slug ORDER BY r.time) AS row
	    FROM
		registration_participant a
		left outer join results_result r on r.participant_id = a.id
		left outer join registration_number nr on nr.id = a.primary_number_id
		where a.team_name_slug <> '' and a.team_name_slug <> '-' and r.time is not null and a.is_competing is true and a.distance_id = %(t)i and a.gender='F'
		order by a.team_name_slug, r.time
        ) x where x.row <= 1)

    ) p
    ) participant on team.team_name_slug = participant.team_name_slug
    left outer join core_distance distance on distance.id =  participant.distance_id
    order by counter desc, total, team.team_name_slug, participant.distance_id, time
    """ % distance_ids)
            object_list = cursor.fetchall()
            cache.set(cache_key, object_list, default_timeout)

        context.update({
            'object_list': object_list,
        })
        return context


class ResultDiplomaPDF(DetailView):
    pk_url_kwarg = 'pk2'
    model = Result

    def get(self, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.participant.is_shown_public:
            raise Http404("Anonymous participant cannot get diploma.")

        if self.object.competition.processing_class:
            _class = load_class(self.object.competition.processing_class)
        else:
            raise Http404
        try:
            processing_class = _class(self.object.competition_id)
            file_obj = processing_class.generate_diploma(self.object)
        except:
            raise Http404
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s.pdf' % self.object.participant.slug
        response.write(file_obj.read())
        file_obj.close()
        return response


class TeamResultsByPointsBetweenDistances(SetCompetitionContextMixin, TemplateView):
    """
    This class is used to view team results for one competition/stage.
    This is fully optimized view.
    """
    template_name = 'results/team_top_point_results.html'

    def get(self, *args, **kwargs):
        self.set_competition(kwargs.get('pk'))
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        cache_key = 'team_results_by_name_btw_distances_%i' % self.competition.id

        default_timeout = 60 * 30
        if self.competition.competition_date == datetime.date.today():
            default_timeout = 60

        object_list = cache.get(cache_key)
        if not object_list:
            distances = self.competition.get_distances()
            to_dist = {
                "v": distances.filter(kind="V"),
                "s": distances.filter(kind="S"),
                "t": distances.filter(kind="T"),
            }
            distance_ids = {
                "v": to_dist["v"][0].pk if to_dist["v"] else 0,
                "s": to_dist["s"][0].pk if to_dist["s"] else 0,
                "t": to_dist["t"][0].pk if to_dist["t"] else 0,
            }

            cursor = connection.cursor()
            cursor.execute("""SELECT team.*, participant.*, distance.name, team.total FROM (
    SELECT kopa.team_name_slug, count(*) counter, sum(kopa.points_distance) total FROM (
        SELECT p.team_name_slug, p.points_distance FROM (
            SELECT a.team_name_slug, r.points_distance, row_number() OVER (PARTITION BY team_name_slug ORDER BY r.points_distance) AS row
            FROM registration_participant a
            LEFT OUTER JOIN results_result r ON r.participant_id = a.id
            WHERE a.team_name_slug <> '' AND a.team_name_slug <> '-' AND r.points_distance IS NOT NULL AND a.is_competing is true AND a.distance_id IN ({v}, {s}, {t}) AND r.competition_id={competition_id}
            ORDER BY a.team_name_slug, r.points_distance
        ) p
        WHERE p.row <= 4
    ) kopa group by kopa.team_name_slug ORDER BY total DESC
) team
LEFT OUTER JOIN (
    SELECT p.team_name, p.team_name_slug, p.points_distance,p.first_name,p.last_name,p.birthday,p.team_name,p.number,p.distance_id FROM (
        SELECT * FROM (
            SELECT a.*, r.points_distance, nr.number, row_number() OVER (PARTITION BY team_name_slug ORDER BY r.points_distance) AS row
            FROM registration_participant a
            LEFT OUTER JOIN results_result r ON r.participant_id = a.id
            LEFT OUTER JOIN registration_number nr ON nr.id = a.primary_number_id
            WHERE a.team_name_slug <> '' AND a.team_name_slug <> '-' AND r.points_distance IS NOT NULL AND a.is_competing is true AND a.distance_id IN ({v}, {s}, {t}) AND r.competition_id={competition_id}
            ORDER BY a.team_name_slug, r.points_distance
        ) x
    ) p
) participant ON team.team_name_slug = participant.team_name_slug
LEFT OUTER JOIN core_distance distance ON distance.id =  participant.distance_id
ORDER BY total DESC, team.team_name_slug, points_distance DESC""".format(competition_id=self.competition.pk,
                                                                         **distance_ids))
            object_list = cursor.fetchall()
            cache.set(cache_key, object_list, default_timeout)
        context.update({
            'object_list': object_list,
        })
        return context
