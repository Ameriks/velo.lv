# coding=utf-8
from __future__ import unicode_literals
from django.forms.util import flatatt
from django.forms.widgets import Select
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class CompetitionWidget(Select):
    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs)
        output = [format_html('<div{0}>', flatatt(final_attrs))]
        options = self.render_buttons(name)
        if options:
            output.append(options)
        output.append('</div>')
        return mark_safe('\n'.join(output))

    def render_buttons(self, name):
        output = []
        for option_value, option_obj in self.choices:
            output.append(self.render_button(option_value, option_obj, name))
        return '\n'.join(output)

    def render_button(self, option_value, option, name):
        attrs = {}

        if option.apply_image:
            attrs.update({
                'style': 'background: url(%s) center center;' % option.apply_image.url
            })

        attrs = flatatt(attrs)
        return format_html('<button class="btn btn-default" type="submit" name="{0}" value="{1}"{2}><span>{3}</span></button>',
                           name,
                           option_value,
                           attrs,
                           force_text(option.get_full_name))