from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext, ugettext_lazy as _
from redactor.widgets import RedactorEditor


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
        error_message = _("This value must contain only letters, numbers,"
                          " dots, underscores, dashes, slashes or tildes."))

    class Meta:
        model = FlatPage
        fields = '__all__'
        widgets = {
            'content': RedactorEditor(redactor_settings={
                'convertVideoLinks': True,
            }),
        }


    def clean(self):
        url = self.cleaned_data.get('url', None)
        sites = self.cleaned_data.get('sites', None)

        same_url = FlatPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if sites and same_url.filter(sites__in=sites).exists():
            for site in sites:
                if same_url.filter(sites=site).exists():
                    raise forms.ValidationError(
                        _('Flatpage with url %(url)s already exists for site %(site)s'),
                        code='duplicate_url',
                        params={'url': url, 'site': site},
                    )

        return super(FlatpageForm, self).clean()
