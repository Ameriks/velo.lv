import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Div, Submit, Reset
from django.utils.translation import ugettext_lazy as _

from velo.results.models import ChipScan

__all__ = ['ChipScanFilter', ]


class ChipScanFilter(django_filters.FilterSet):
    class Meta:
        model = ChipScan
        fields = ['is_processed', 'nr_text', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.fields:
            self.filters[field].field.help_text = None

        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.layout = Layout(
            Row(
                Div(
                    'is_processed',
                    css_class='col-sm-2',
                ),
                Div(
                    'nr_text',
                    css_class='col-sm-2',
                ),
                Div(
                    Submit('submit', _('Search'), css_class='btn btn-primary'),
                    Reset('reset', _('Reset'), css_class='btn btn-primary'),
                    css_class='col-sm-4 pull-right',
                ),
            )
        )

