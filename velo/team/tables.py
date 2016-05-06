# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A

from velo.team.models import Team


class TeamTable(tables.Table):
    is_featured = tables.TemplateColumn(verbose_name=" ", accessor='is_featured', empty_values=(), template_name='team/table/is_featured.html')

    def render_title(self, record, **kwargs):
        url = reverse('competition:team', kwargs={'pk': self.request_kwargs.get('pk'), 'pk2': record.id})
        return mark_safe('<a href="%s">%s</a>' % (url, record.title))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.request_kwargs = kwargs.pop('request_kwargs', None)
        super(TeamTable, self).__init__(*args, **kwargs)

    class Meta:
        model = Team
        attrs = {"class": "table-block"}
        fields = ("is_featured", "title", "country", "contact_person")
        empty_text = _("There are no teams")
        per_page = 200
        template = "base/table.html"


class TeamMyTable(tables.Table):
    is_featured = tables.TemplateColumn(verbose_name=" ", accessor='is_featured', empty_values=(), template_name='team/table/is_featured.html')

    title = tables.LinkColumn('account:team', args=[A('id')])
    competition = tables.Column(verbose_name=_('Competition'), accessor='distance.competition.get_full_name', order_by='distance.competition.name')
    apply = tables.Column(verbose_name=" ", empty_values=())

    def render_apply(self, record, **kwargs):
        ret = ''
        if record.distance.competition.params_dict.get('teams_should_apply', False):
            ret = mark_safe("<a href='%s'>%s</a>" % (reverse('account:team_apply_list', kwargs={'pk2': record.id}), ugettext('Apply')))

        if record.distance.profile_price and not record.is_featured:
            if ret != '':
                ret += mark_safe('<br />')
            ret += mark_safe("<a href='%s'>%s</a>" % (reverse('account:team_pay', kwargs={'pk2': record.id}), ugettext('Pay for team account')))

        return ret


    class Meta:
        model = Team
        attrs = {"class": "table-block"}
        fields = ("title", "is_featured", "distance")
        sequence = ("is_featured", "title", "competition", "distance", "apply")
        empty_text = _("You haven't created any official team.")
        order_by = ("-id")
        per_page = 20
        template = "base/table.html"
