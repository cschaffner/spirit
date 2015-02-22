from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView, RedirectView
from views import MyRedirectView, season, tournament
from django.views.decorators.cache import cache_page


from settings import CACHE_TIME, CACHE_TIME_VIEWS
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'spirit.views.home'),
    url(r'^logout/$', 'spirit.views.logout'),
    url(r'^login/$', 'spirit.views.login'),
    url(r'^code/$', 'spirit.views.code'),
    url(r'^seasons/(\d+)/$', cache_page(CACHE_TIME_VIEWS)(season), name='seasons'),
    url(r'^teams/(\d+)/$', 'spirit.views.team', name='teams'),
    url(r'^teams/(\d+)/(\d+)-(\d+)-(\d+)/$', 'spirit.views.team_date'),
    url(r'^tournaments/(\d+)/$', cache_page(CACHE_TIME_VIEWS)(tournament), name='tournaments'),
    url(r'^result/(\d+)/$', 'spirit.views.result'),
    url(r'^games/(\d+)/$', 'spirit.views.game', name='games'),
    url(r'^delete/(\d+)/$', 'spirit.views.delete'),
    url(r'^games/(\d+)/submit/([1|2])/$', 'spirit.views.game_submit'),
    url(r'^instructions/$', 'spirit.views.instructions'),
    url(r'^team/(?P<id>\d+)/$', MyRedirectView.as_view(url='/teams/')),
    url(r'^season/(?P<id>\d+)/$', MyRedirectView.as_view(url='/seasons/')),
    url(r'^game/(?P<id>\d+)/$', MyRedirectView.as_view(url='/games/')),
    url(r'^tournament/(?P<id>\d+)/$', MyRedirectView.as_view(url='/tournaments/')),


    # url(r'^spirit/', include('spirit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

