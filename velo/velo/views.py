# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.i18n import javascript_catalog

from django_select2.views import AutoResponseView
from impersonate.decorators import allowed_user_required
from impersonate.helpers import users_impersonable, get_paginator, get_redir_arg, get_redir_field


class CustomAutoResponseView(AutoResponseView):

    def get_queryset(self):
        """Get queryset from cached widget."""
        try:
            return self.widget.filter_queryset(self.term, self.queryset, context=self.request.GET.get('context'))
        except:
            return self.widget.filter_queryset(self.term, self.queryset)

    def get(self, request, *args, **kwargs):
        """
        Return a :class:`.django.http.JsonResponse`.

        Example::

            {
                'results': [
                    {
                        'text': "foo",
                        'id': 123
                    }
                ],
                'more': true
            }

        """
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        ret = []
        for obj in context['object_list']:
            ret2 = { 'text': self.widget.label_from_instance(obj), 'id': obj.pk, }
            if hasattr(self.widget, 'extra_data_from_instance'):
                ret2.update(self.widget.extra_data_from_instance(obj, self.request.GET.get('context')))
            ret.append(ret2)

        return JsonResponse({
            'results': ret,
            'more': context['page_obj'].has_next()
        })


last_modified_date = timezone.now()
@last_modified(lambda req, **kw: last_modified_date)
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)



@allowed_user_required
def search_users(request, template):
    ''' Simple search through the users.
        Will add 7 items to the context.
          * users - All users that match the query passed.
          * paginator - Django Paginator instance
          * page - Current page of objects (from Paginator)
          * page_number - Current page number, defaults to 1
          * query - The search query that was entered
          * redirect - arg for redirect target, e.g. "?next=/foo/bar"
          * redirect_field - hidden input field with redirect argument,
                              put this inside search form
    '''
    query = request.GET.get('q', '')
    search_q = Q(first_name__icontains=query) | \
               Q(last_name__icontains=query) | \
               Q(email__icontains=query)
    users = users_impersonable(request)

    users = users.filter(search_q)
    paginator, page, page_number = get_paginator(request, users)

    return render(request, template, {
        'users': users,
        'paginator': paginator,
        'page': page,
        'page_number': page_number,
        'query': query,
        'redirect': get_redir_arg(request),
        'redirect_field': get_redir_field(request),
    })
