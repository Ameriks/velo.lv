# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.forms.utils import flatatt
from django.forms.widgets import Select, Widget
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class PaymentTypeWidget(Select):
    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs)
        output = []
        options = self.render_buttons(name, value)
        if options:
            output.append(options)
        return mark_safe('\n'.join(output))

    def render_buttons(self, name, value):
        output = []
        index = 0
        for option_value, option_obj in self.choices:
            output.append(self.render_button(option_value, option_obj, name, value, index))
            index += 1
        return '\n'.join(output)

    def render_button(self, option_value, option, name, current_value, index):
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
                'data-bill': 'true',
            })
            label = '<span class="fw700 fs14 uppercase">%s</span>' % _("Get Invoice")
        else:
            label = '<figure class="check-button__image img-wrapper loaded"><img onload="imgLoaded(this)" src="/static/img/banks/%s.png"></figure>' % option.payment_channel.image_slug


        attrs = flatatt(attrs)
        return format_html(
            '<div class="col-xl-6 col-l-12 col-xs-24"><div class="w100 bottom-margin--20"><div class="check-button w100"><input type="radio" name="{0}" value="{1}" id="{5}" class="check-button__input" {2} /><label for="{5}" class="check-button__label flex direction--row justify--center align-items--center {3}">{4}</label></div></div></div>',
            name,
            option_value,
            attrs,
            active,
            mark_safe(label),
            self.get_id(name, index),
            )

    def get_id(self, name=None, index=None):
        return "id_%s_%s" % (name, index)


class DoNotRenderWidget(Widget):
    is_hidden = True

    def render(self, name, value, attrs=None):
        return ''
