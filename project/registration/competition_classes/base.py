from sitetree.utils import item
from core.models import Competition
from registration.models import Number
from django.core.cache import cache


class CompetitionScriptBase(object):
    competition_id = None
    competition = None

    def __init__(self, competition_id=None, competition=None):
        if not competition_id and not competition:
            raise Exception('At least one variable is required.')

        self.competition = competition or Competition.objects.get(id=competition_id)
        self.competition_id = self.competition.id

    def assign_group(self, distance_id, gender, birthday):
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
                    print Number.objects.get_or_create(competition_id=self.competition_id, group=number_dict.get('group', ''), distance_id=distance_id, number=number, defaults={'status': 1})


    def reset_cache(self):
        cache.delete('sitetrees')
        cache.delete('tree_aliases')
        # TODO: Add all other caches that are added manually

    def calculate_points_distance(self, result):
        return 0

    def calculate_points_group(self, result):
        return 0

    def build_flat_pages(self, competition, items):
        for page in competition.flatpage_set.filter(is_published=True):
            items.append(item(page.title, 'competition:flatpage %i %s' % (competition.id, page.url)))
