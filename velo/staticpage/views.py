import xhtml2pdf
from django.http import Http404
from django.views.generic import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from velo.staticpage.models import StaticPage
from velo.velo.mixins.views import SetCompetitionContextMixin


class StaticPageView(SetCompetitionContextMixin, DetailView):
    slug_field = 'url'
    model = StaticPage

    def get_queryset(self):
        queryset = super(StaticPageView, self).get_queryset()

        if self.competition:
            queryset = queryset.filter(competition__in=self.competition.get_ids())

        return queryset

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        queryset = queryset.filter(**{self.get_slug_field(): slug})

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = super(StaticPageView, self).get_context_data(**kwargs)

        content = self.object.content
        # TODO: Write regex for this
        # content = content.replace('<table>', '<table class="table table-striped table-bordered table-hover table-condensed">')
        # content = content.replace('<table', '<div class="table-responsive"><table')
        # content = content.replace('</table>', '</table></div>')

        context.update({'content': content})
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get('kind') == "PDF":
            a = xhtml2pdf
            # create PDF
            pass
        else:
            return super().get(request, *args, **kwargs)
