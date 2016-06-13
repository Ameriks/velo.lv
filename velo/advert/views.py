from django.conf import settings
from django.db.models import F
from django.http import HttpResponseRedirect
from django.views.generic import DetailView

from .models import Banner
from velo.velo.mixins.views import CacheControlMixin


class BannerView(CacheControlMixin, DetailView):
    cache_timeout = 60*60
    model = Banner

    def rebuild_html(self):
        html = self.object.converted.replace('https://www.gstatic.com/swiffy/v6.0', '{0}plugins/swiffy'.format(settings.STATIC_URL))

        script = """
        <script>
document.addEventListener('visibilitychange', function(event) {
  if (document.hidden) {
    stage.destroy();
  } else {
      stage = new swiffy.Stage(document.getElementById('swiffycontainer'), swiffyobject);
      stage.start();

  }
});</script>
        """
        html = html.replace('</body>', '{0}</body>'.format(script))

        return html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.converted:
            context.update({'html': self.rebuild_html()})
        return context


class BannerRedirectView(DetailView):
    model = Banner

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        Banner.objects.filter(id=object.id).update(click_count=F('click_count') + 1)
        return HttpResponseRedirect(object.url)
