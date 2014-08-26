from django.utils.safestring import mark_safe
from django_tables2.columns import CheckBoxColumn


class CustomCheckBoxColumn(CheckBoxColumn):
    def wrap_checkbox(self):
        return '<label>%s<span class="lbl"></span></label>'

    @property
    def header(self):
        field = super(CustomCheckBoxColumn, self).header
        return mark_safe(self.wrap_checkbox() % field)

    def render(self, value, bound_column):
        field = super(CustomCheckBoxColumn, self).render(value, bound_column)
        return mark_safe(self.wrap_checkbox() % field)
