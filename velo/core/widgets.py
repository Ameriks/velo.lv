# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import datetime
import re

from django.forms.utils import flatatt
from django.forms.widgets import Input, FileInput, Widget, Select
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.templatetags.staticfiles import static


RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


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


class ProfileImage(FileInput):
    input_type = 'file'
    needs_multipart_form = True

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        try:
            final_attrs.update({'value': value.url})
        except (ValueError, AttributeError):
            final_attrs.update({'value': static('template/velo-2016/html/img/placeholders/velo-placeholder--1x1.svg')})

        return render_to_string('core/widgets/profile_image.html', final_attrs)


class SplitDateWidget(Widget):

    none_value = [(0, '---'), ]
    day_field = '%s_day'
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, required=True):
        super().__init__(attrs=attrs)
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        self.years = range(1915, datetime.date.today().year)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val, day_val = value.year, value.month, value.day
        except AttributeError:
            year_val = month_val = day_val = None
            if isinstance(value, str):
                match = RE_DATE.match(value)
                if match:
                    year_val, month_val, day_val = [int(v) for v in match.groups()]

        output = []

        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name

        year_choices = [(0, 'YYYY'), ] + [(i, i) for i in reversed(self.years)]
        local_attrs = self.build_attrs({"id": self.year_field % id_, "class": "select"})
        s = Select(choices=year_choices)
        select_html = s.render(self.year_field % name, year_val, local_attrs)
        output.append('<div class="col-xl-8">%s</div>' % select_html)

        month_choices = [(0, 'MM'), ] + list(MONTHS.items())
        local_attrs['id'] = self.month_field % id_
        s = Select(choices=month_choices)
        select_html = s.render(self.month_field % name, month_val, local_attrs)
        output.append('<div class="col-xl-8">%s</div>' % select_html)

        day_choices = [(0, 'DD'), ] + [(i, i) for i in range(1, 32)]
        local_attrs['id'] = self.day_field % id_
        s = Select(choices=day_choices)
        select_html = s.render(self.day_field % name, day_val, local_attrs)
        output.append('<div class="col-xl-8">%s</div>' % select_html)

        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        d = data.get(self.day_field % name)
        if y == m == d == "0":
            return None
        if y and m and d:
            return '%s-%s-%s' % (y, m, d)
        return data.get(name, None)

