from modeltranslation.translator import translator, TranslationOptions
from .models import CompetitionSupporter


class CompetitionSupporterTranslationOptions(TranslationOptions):
    fields = ('support_title',)


translator.register(CompetitionSupporter, CompetitionSupporterTranslationOptions)
