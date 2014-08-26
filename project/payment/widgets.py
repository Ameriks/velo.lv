# coding=utf-8
from __future__ import unicode_literals
from django.forms.util import flatatt
from django.forms.widgets import Select
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings


class PaymentTypeWidget(Select):
    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs)
        output = [format_html('<div class="btn-group btn-block" data-toggle="buttons" {0}>', flatatt(final_attrs))]
        options = self.render_buttons(name, value)
        if options:
            output.append(options)
        output.append('</div>')
        return mark_safe('\n'.join(output))

    def render_buttons(self, name, value):
        output = []
        for option_value, option_obj in self.choices:
            output.append(self.render_button(option_value, option_obj, name, value))
        return '\n'.join(output)

    def render_button(self, option_value, option, name, current_value):
        attrs = {}
        active = ''

        if option.payment_channel.image_slug:
            active += ' banks_{0}'.format(option.payment_channel.image_slug)

        if current_value == str(option_value):
            active += ' active'
            attrs.update({
                'checked': 'checked'
            })

        if option.payment_channel.is_bill:
            attrs.update({
                'data-bill': True,
            })

        attrs = flatatt(attrs)
        return format_html('<label class="btn btn-default btn-block banks_all {0}"><input type="radio" name="{1}" value="{2}" {3} /><span>{4}</span></label>',
                           active,
                           name,
                           option_value,
                           attrs,
                           force_text(unicode(option.payment_channel)))



