from velo.core.models import Competition


def competitions(request):
    # TODO: Cache
    competitions = Competition.objects.filter(is_in_menu=True).order_by('frontpage_ordering')
    return {'competitions': competitions}
