from sitetree.utils import tree, item
from velo.core.models import Competition
from velo.velo.utils import load_class


def sitetrees_build(lang):
    items = []
    for competition in Competition.objects.filter(is_in_menu=True):
        children = []
        if competition.processing_class:
            _class = load_class(competition.processing_class)
            processing = _class(competition=competition)
            items.append(processing.build_menu(lang))
        else:
            items.append(item(str(competition), '#', url_as_pattern=False, children=children))
    return tree('dynamic_competition', items=items),

sitetrees_lv = sitetrees_build('lv')
sitetrees_en = sitetrees_build('en')
sitetrees_ru = sitetrees_build('ru')

