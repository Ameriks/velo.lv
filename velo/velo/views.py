from django.db.models import Q
from django.shortcuts import render
from django_select2.util import get_field
from django_select2.views import AutoResponseView, NO_ERR_RESP
from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.i18n import javascript_catalog
from impersonate.decorators import allowed_user_required
from impersonate.helpers import users_impersonable, get_paginator, get_redir_arg, get_redir_field


class CustomAutoResponseView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            term = request.GET.get('term', None)
            field = get_field(request.GET.get('field_id'))
            if term is None:
                return self.render_to_response(self._results_to_context(('missing term', False, [], )))
            if not term and not getattr(field, 'get_empty_results', False):
                return self.render_to_response(self._results_to_context((NO_ERR_RESP, False, [], )))

            try:
                page = int(request.GET.get('page', None))
                if page <= 0:
                    page = -1
            except ValueError:
                page = -1
            if page == -1:
                return self.render_to_response(self._results_to_context(('bad page no.', False, [], )))
            context = request.GET.get('context', None)
        else:
            return self.render_to_response(self._results_to_context(('not a get request', False, [], )))

        return self.render_to_response(
            self._results_to_context(
                self.get_results(request, term, page, context)
                )
            )

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
