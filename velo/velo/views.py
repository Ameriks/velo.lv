from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import last_modified
from django.views.i18n import javascript_catalog

from django_select2.views import AutoResponseView


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

