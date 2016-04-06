# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import DetailView

from velo.advert.models import FlashBanner
from velo.velo.mixins.views import CacheControlMixin


class FlashBannerView(CacheControlMixin, DetailView):
    cache_timeout = 60*60
    model = FlashBanner

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
        context = super(FlashBannerView, self).get_context_data(**kwargs)
        context.update({'html': self.rebuild_html()})
        return context


class FlashBannerRedirectView(DetailView):
    model = FlashBanner

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return HttpResponseRedirect(object.url)
