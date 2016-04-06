# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.forms.utils import flatatt
from django.forms.widgets import Input
from django.utils.html import format_html


class ButtonWidget(Input):
    input_type = 'button'
    text = ''

    def __init__(self, attrs=None):
        if attrs is not None:
            self.text = attrs.pop('text', self.text)
        super(ButtonWidget, self).__init__(attrs)

    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html(u'<a{0}>{1}</a>', flatatt(final_attrs), self.text)
