from django.conf import settings
from django.core.cache import cache

from velo.core.models import Competition
from velo.supporter.models import Supporter


def competitions(request):
    cache_key = 'global_competitions'
    competitions = cache.get(cache_key, None)
    if not competitions:
        competitions = Competition.objects.filter(is_in_menu=True).order_by('frontpage_ordering')
        cache.set(cache_key, competitions, 60 * 30)  # Cache for 30 minutes

    cache_key = 'global_supporters'
    agency_supporters = cache.get(cache_key, None)
    if not agency_supporters:
        agency_supporters = Supporter.objects.filter(is_agency_supporter=True).order_by("?").select_related("default_svg")
        cache.set(cache_key, agency_supporters, 60 * 30)  # Cache for 30 minutes

    return {'front_competitions': competitions, 'agency_supporters': agency_supporters, 'debug': settings.DEBUG}
