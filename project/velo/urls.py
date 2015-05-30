from django.db.utils import ProgrammingError
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from sitetree.sitetreeapp import register_dynamic_trees, compose_dynamic_tree
from sitetree.sitetreeapp import register_i18n_trees

from core.views import CalendarView
from payment.views import ApplicationPayView, ApplicationOKView
from registration.views import ApplicationUpdate, ApplicationCreate, CompanyApplicationCreate, CompanyApplicationDetail, \
    CompanyApplicationParticipantAdd, MyCompanyApplicationList, CompanyApplicationParticipantAddOK, \
    CompanyApplicationUpdate, ParticipantPDF
from results.views import ResultAllView
from supporter.views import AgencySupporters
from velo.views import CustomAutoResponseView


admin.autodiscover()


register_i18n_trees(['mainmenu', 'competition_admin'])

try:
    register_dynamic_trees((
        compose_dynamic_tree('core', target_tree_alias='mainmenu_lv', parent_tree_item_alias='sacensibas'),
    ))
    register_dynamic_trees((
        compose_dynamic_tree('manager', target_tree_alias='mainmenu_lv', parent_tree_item_alias='manager'),
    ))
except ProgrammingError:
    print 'Seems that migrations should be run.'



js_info_dict = {
    # Not yet used
}

urlpatterns = i18n_patterns('',
    url(r'^$', RedirectView.as_view(url='/lv/sacensibas/47/rezultati/'), name='index'),

    url(_(r'^application/$'), ApplicationCreate.as_view(), name='application'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'), ApplicationUpdate.as_view(), name='application'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/pay/$'), ApplicationPayView.as_view(), name='application_pay'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/ok/$'), ApplicationOKView.as_view(), name='application_ok'),



    url(_(r'^company_application/$'), MyCompanyApplicationList.as_view(), name='companyapplication_list'),
    url(_(r'^company_application/add/$'), CompanyApplicationCreate.as_view(), name='companyapplication'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'), CompanyApplicationDetail.as_view(), name='companyapplication'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/add/$'), CompanyApplicationParticipantAdd.as_view(), name='companyapplication_add'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/ok/$'), CompanyApplicationParticipantAddOK.as_view(), name='companyapplication_ok'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/edit/$'), CompanyApplicationUpdate.as_view(), name='companyapplication_edit'),


    url(_(r'^results/'), ResultAllView.as_view(), name="all_results"),
    url(_(r'^payment/'), include('payment.urls', namespace='payment')),
    url(_(r'^whatever/'), include('advert.urls', namespace='advert')),
    url(_(r'^news/'), include('news.urls', namespace='news')),
    url(_(r'^gallery/'), include('gallery.urls', namespace='gallery')),
    url(_(r'^mk/'), include('marketing.urls', namespace='marketing')),
    url(r'^manager/', include('manager.urls', namespace='manager')),
    url(_(r'^competition/'), include('velo.urls_competition', namespace='competition')),
    url(_(r'^supporters/'), AgencySupporters.as_view(), name="agency_supporters"),
    url(_(r'^calendar/'), CalendarView.as_view(), name="calendar"),
    url(_(r'^accounts/'), include('core.urls', namespace='accounts')),
    url(_(r'^accounts/'), include('social.apps.django_app.urls', namespace='social')),
    url(r'^jsi18n/$', 'velo.views.cached_javascript_catalog', js_info_dict),
)


urlpatterns += patterns('',
    url(r'^$', RedirectView.as_view(url='/lv/')),

    url(_(r'^pdf/(?P<slug>\w+)/'), ParticipantPDF.as_view(), name="participant_number_pdf"),

    url(r'^admin/', include('admin_honeypot.urls')), # Honeypot for losers :)
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^%s/' % settings.ADMIN_URL, include(admin.site.urls)),  # This is real admin with hidden link in ENV

    url(r'^impersonate/search/$', 'velo.views.search_users', {'template': 'impersonate/search_users.html'}, name='impersonate-search'),
    url(r'^impersonate/', include('impersonate.urls')),

    url(r"^json/fields/auto.json$", CustomAutoResponseView.as_view(), name="django_select2_central_json"),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    if 'rosetta' in settings.INSTALLED_APPS:
        urlpatterns += patterns('',
            url(r'^rosetta/', include('rosetta.urls')),
        )