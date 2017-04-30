import datetime

from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
from django.db import connection

from sitetree.utils import item
from velo.core.models import Competition

from velo.registration.models import Number
from django.core.cache import cache
from velo.results.models import DistanceAdmin


class CompetitionScriptBase(object):
    competition_id = None
    competition = None

    def __init__(self, competition_id=None, competition=None):
        if not competition_id and not competition:
            raise Exception('At least one variable is required.')

        self.competition = competition or Competition.objects.get(id=competition_id)
        self.competition_id = self.competition.id

    def assign_group(self, distance_id, gender, birthday, participant=None):
        raise NotImplementedError()

    def number_ranges(self):
        raise NotImplementedError()

    def generate_diploma(self, result):
        raise NotImplementedError()

    def apply_number_ranges(self):
        assert self.competition_id is not None
        ranges = self.number_ranges()
        for distance_id in ranges:
            numbers = ranges.get(distance_id)
            for number_dict in numbers:
                for number in range(number_dict.get('start'), number_dict.get('end')):
                    print(Number.objects.get_or_create(competition_id=self.competition_id, group=self.get_group_for_number_search(None, None, None, group=number_dict.get('group', '')), distance_id=distance_id, number=number, defaults={'status': 1}))

    def get_group_for_number_search(self, distance_id, gender, birthday, group=None):
        return ''

    def reset_cache(self):
        cache.delete('sitetrees')
        cache.delete('tree_aliases')
        # TODO: Add all other caches that are added manually

    def calculate_points_distance(self, result, top_result=None):
        return 0

    def calculate_points_group(self, result):
        return 0

    def build_flat_pages(self, competition, items, lang):
        for page in competition.staticpage_set.filter(is_published=True, language__in=[lang, '']):
            items.append(item(page.title, 'competition:staticpage %i %s' % (competition.id, page.url)))

        for page in competition.parent.staticpage_set.filter(is_published=True, language__in=[lang, '']):
            items.append(item(page.title, 'competition:staticpage %i %s' % (competition.id, page.url)))

    def calculate_time(self, chip):
        distance_admin = DistanceAdmin.objects.get(competition=chip.competition, distance=chip.nr.distance)

        delta = datetime.datetime.combine(datetime.date.today(), distance_admin.zero) - datetime.datetime.combine(datetime.date.today(), datetime.time(0,0,0,0))
        result_time = (datetime.datetime.combine(datetime.date.today(), chip.time) - delta).time()

        seconds = result_time.hour * 60 * 60 + result_time.minute * 60 + result_time.second
        return result_time, seconds

    def assign_result_place(self):
        """
        Assign result place based on result time. Optimized to use raw SQL.
        """
        cursor = connection.cursor()

        # First assign distance place
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = res2.distance_row_nr,
    result_group = res2.group_row_nr
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing,
row_number() OVER (PARTITION BY nr.distance_id ORDER BY nr.distance_id, res.status, res.time) as distance_row_nr,
row_number() OVER (PARTITION BY nr.distance_id, p.group ORDER BY nr.distance_id, p.group, res.status, res.time) as group_row_nr
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
WHERE p.is_competing is true and res.time IS NOT NULL
) res2
WHERE res2.competition_id = %s and res2.time IS NOT NULL and res2.is_competing is true
AND r.id = res2.id
""", [self.competition_id, ])
        # Then unset places to others
        cursor.execute("""
UPDATE
    results_result r
SET
    result_distance = NULL,
    result_group = NULL
FROM
(
Select res.id, result_distance, res.competition_id, res.time, p.is_competing
FROM results_result As res
INNER JOIN registration_number nr ON res.number_id = nr.id
INNER JOIN registration_participant p ON res.participant_id = p.id
) res2
WHERE res2.competition_id = %s and (res2.time IS NULL or res2.is_competing is false)
AND r.id = res2.id
""", [self.competition_id, ])

    def reset_cache_results(self):
        for lang_key, lang_name in settings.LANGUAGES:
            for distance in self.competition.get_distances():
                cache_key = make_template_fragment_key('results_team_by_teamname', [lang_key, self.competition, distance])
                cache.delete(cache_key)
        for distance in self.competition.get_distances():
            cache.delete('team_results_by_name_%i_%i' % (self.competition.id, distance.id))

    def result_select_extra(self, distance_id):
        return {}
