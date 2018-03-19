from modeltranslation.translator import translator, TranslationOptions
from .models import Competition, Distance, InsuranceCompany


class CompetitionTranslationOptions(TranslationOptions):
    fields = ('name', 'description',)


class DistanceTranslationOptions(TranslationOptions):
    fields = ('name',)


class InsuranceCompanyTranslationOptions(TranslationOptions):
    fields = ('term', 'description')


translator.register(Competition, CompetitionTranslationOptions)
translator.register(Distance, DistanceTranslationOptions)
translator.register(InsuranceCompany, InsuranceCompanyTranslationOptions)
