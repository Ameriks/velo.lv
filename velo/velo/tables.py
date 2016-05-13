from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django_tables2 import TemplateColumn
from django_tables2.columns import CheckBoxColumn


class CustomCheckBoxColumn(CheckBoxColumn):
    def wrap_checkbox(self):
        return '<label>%s<span class="lbl"></span></label>'

    @property
    def header(self):
        field = super(CustomCheckBoxColumn, self).header
        return mark_safe(self.wrap_checkbox() % field)

    def render(self, value, bound_column, record):
        field = super(CustomCheckBoxColumn, self).render(value, bound_column, record)
        return mark_safe(self.wrap_checkbox() % field)


class CustomSelectionCheckBoxColumn(TemplateColumn):
    def __init__(self, template_code=None, template_name=None, **extra):
        super().__init__(template_name="registration/table/selection.html", **extra)

    @property
    def header(self):
        context = {
            'record': {
                'id': 'all'
            }
        }
        template = get_template(self.template_name)
        return template.render(context)

