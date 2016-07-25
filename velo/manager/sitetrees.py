from django.utils.translation import activate
from sitetree.utils import tree, item
from velo.core.models import Competition
from velo.velo.utils import load_class


def sitetrees_build():
    activate("lv")
    items = []
    for competition in Competition.objects.filter(is_in_menu=True):
        children = []
        if competition.processing_class:
            _class = load_class(competition.processing_class)
            processing = _class(competition=competition)
            items.append(processing.build_manager_menu())
        else:
            items.append(item(str(competition), '#', url_as_pattern=False, children=children, access_loggedin=True))
    return (tree('dynamic_competition_manager', items=items),)

sitetrees = sitetrees_build()


