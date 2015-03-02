
from django.http import Http404

from django.views.generic import DetailView
from django.core.exceptions import ObjectDoesNotExist
from flatpages.models import FlatPage
from velo.mixins.views import SetCompetitionContextMixin
from django.utils.translation import ugettext as _


class FlatpageView(SetCompetitionContextMixin, DetailView):
    slug_field = 'url'
    model = FlatPage

    def get_queryset(self):
        queryset = super(FlatpageView, self).get_queryset()

        if self.competition:
            queryset = queryset.filter(competition=self.competition)

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
        context = super(FlatpageView, self).get_context_data(**kwargs)

        content = self.object.content
        content = content.replace('<table>', '<table class="table table-striped table-bordered table-hover table-condensed">')

        context.update({'content': content})
        return context