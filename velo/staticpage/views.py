from django.http import Http404, HttpResponse
from django.views.generic import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from xhtml2pdf import pisa
from django.templatetags.static import static

from config.settings.common import APPS_DIR
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
            if not self.competition:
                self.set_competition(kwargs.get('pk'))
            obj = self.get_object()
            content = obj.get_contentmd
            html = "<html><head><meta charset=\"UTF-8\"><title>Nolikums</title></head><body>{}</body></html>".format(content)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(self.competition.alias or "Nolikums")

            with open(str(APPS_DIR.path(static("/css/xhtml2pdf.css")[1:]))) as f:
                css = f.read()
                pisa.CreatePDF(html, dest=response, default_css=css, encoding="utf-8")
                return response
        # else:
        return super().get(request, *args, **kwargs)
