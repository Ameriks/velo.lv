from django import forms
from django.utils.translation import ugettext_lazy as _

from velo.staticpage.models import StaticPage


class StaticPageForm(forms.ModelForm):
    class Meta:
        model = StaticPage
        fields = '__all__'

    def clean(self):
        url = self.cleaned_data.get('url', None)
        sites = self.cleaned_data.get('sites', None)

        same_url = StaticPage.objects.filter(url=url)
        if self.instance.pk:
            same_url = same_url.exclude(pk=self.instance.pk)

        if sites and same_url.filter(sites__in=sites).exists():
            for site in sites:
                if same_url.filter(sites=site).exists():
                    raise forms.ValidationError(
                        _('Staticpage with url %(url)s already exists for site %(site)s'),
                        code='duplicate_url',
                        params={'url': url, 'site': site},
                    )

        return super(StaticPageForm, self).clean()
