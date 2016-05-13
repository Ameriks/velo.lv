from modeltranslation.translator import translator, TranslationOptions
from .models import Competition, Distance


class CompetitionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


class DistanceTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Competition, CompetitionTranslationOptions)
translator.register(Distance, DistanceTranslationOptions)
