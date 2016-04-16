# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import BaseInlineFormSet

from velo.velo.mixins.forms import GetClassNameMixin


class CustomBaseInlineFormSet(GetClassNameMixin, BaseInlineFormSet):
    empty_form_class = None
    application = None
    required = 0
    can_add_new = True
    max_num = None

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.required = kwargs.pop('required', 0)
        self.max_num = kwargs.pop('max_num', 1000)
        self.empty_form_class = kwargs.pop('empty_form_class', self.form)
        self.can_add_new = kwargs.pop('can_add_new', self.can_add_new)

        super(CustomBaseInlineFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        super(CustomBaseInlineFormSet, self).clean()

        initial_num = len(list(filter(lambda f: not self._should_delete_form(f), self.initial_forms)))
        extra_num = len(list(filter(lambda f: f.has_changed() and not self._should_delete_form(f), self.extra_forms)))

        if self.required > 0:
            if initial_num + extra_num < self.required:
                raise forms.ValidationError(_('You must have at least %i record' % self.required))
        if initial_num + extra_num > self.max_num:
            raise forms.ValidationError(_('You can add maximum %i records' % self.max_num))

    def empty_form(self):
        data = {
            'auto_id': self.auto_id,
            'prefix': self.add_prefix('__prefix__'),
            'empty_permitted': True,
        }
        if self.application:
            data.update({'application': self.application,})

        form = self.empty_form_class(**data)
        form.helper.template = None
        self.add_fields(form, None)
        return form

    def save_new_objects(self, commit=True):
        if self.can_add_new:
            return super(CustomBaseInlineFormSet, self).save_new_objects(commit)
        else:
            return []


class OnlyAddBaseInlineFormSet(CustomBaseInlineFormSet):
    def save_existing_objects(self, commit=True):
        return []

    def get_queryset(self):
        return []
