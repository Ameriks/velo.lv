from modeltranslation.translator import translator, TranslationOptions
from .models import Competition


class CompetitionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


translator.register(Competition, CompetitionTranslationOptions)
