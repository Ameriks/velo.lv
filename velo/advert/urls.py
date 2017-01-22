from django.conf.urls import url

from .views import BannerView, BannerRedirectView


urlpatterns = [
                       url(r'^f/(?P<pk>\d+)/$', BannerView.as_view(), name='banner'),
                       url(r'^f/(?P<pk>\d+)/r/$', BannerRedirectView.as_view(), name='banner_redirect'),
]
