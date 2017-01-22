from django.contrib import admin
from django import forms
from django.forms import BaseInlineFormSet

from velo.supporter.models import Supporter, CompetitionSupporter, Logo


class LogoInline(admin.TabularInline):
    model = Logo
    extra = 0


class CustomBaseInlineFormSet(BaseInlineFormSet):
    def __init__(self, instance=None, *args, **kwargs):
        print(instance)
        super(CustomBaseInlineFormSet, self).__init__(instance=instance, *args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs.update({"supporter": self.instance})
        return kwargs


class CompetitionSupporterForm(forms.ModelForm):
    class Meta:
        model = CompetitionSupporter
        fields = ['competition', 'ordering', 'logo', 'is_large_logo', 'support_title_lv', 'support_title_en', 'support_title_ru']

    def __init__(self, supporter=None, instance=None, *args, **kwargs):
        super().__init__(instance=instance, *args, **kwargs)
        if supporter:
            self.fields['logo'].choices = [(o.id, str(o)) for o in supporter.logo_set.all()]


class CompetitionSupporterInline(admin.TabularInline):
    model = CompetitionSupporter
    extra = 0
    form = CompetitionSupporterForm
    formset = CustomBaseInlineFormSet



class SupporterAdmin(admin.ModelAdmin):
    inlines = (LogoInline, CompetitionSupporterInline)


admin.site.register(Supporter, SupporterAdmin)
