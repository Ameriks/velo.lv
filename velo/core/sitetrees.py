from sitetree.utils import tree, item
from core.models import Competition
from velo.utils import load_class


def sitetrees_build():
    items = []
    for competition in Competition.objects.filter(is_in_menu=True):
        children = []
        if competition.processing_class:
            _class = load_class(competition.processing_class)
            processing = _class(competition=competition)
            items.append(processing.build_menu())
        else:
            items.append(item(unicode(competition), '#', url_as_pattern=False, children=children))
    return (tree('dynamic_competition', items=items),)

sitetrees = sitetrees_build()


