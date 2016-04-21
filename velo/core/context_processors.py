from django.conf import settings

from velo.core.models import Competition
from velo.supporter.models import Supporter


def competitions(request):
    # TODO: Cache
    competitions = Competition.objects.filter(is_in_menu=True).order_by('frontpage_ordering')
    agency_supporters = Supporter.objects.filter(is_agency_supporter=True).order_by("?").select_related("default_svg")
    return {'front_competitions': competitions, 'agency_supporters': agency_supporters, 'debug': settings.DEBUG}
