from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'spirit.views.home'),
    url(r'^logout/$', 'spirit.views.logout'),
    url(r'^login/$', 'spirit.views.login'),
    url(r'^code/$', 'spirit.views.code'),
    url(r'^season/(\d+)/$', 'spirit.views.season'),
    url(r'^team/(\d+)/$', 'spirit.views.team'),
    url(r'^team/(\d+)/(\d+)-(\d+)-(\d+)/$', 'spirit.views.team_date'),
    url(r'^tournament/(\d+)/$', 'spirit.views.tournament'),
    url(r'^game/(\d+)/$', 'spirit.views.game'),
    url(r'^game/(\d+)/submit/([1|2])/$', 'spirit.views.game_submit'),
    
    # url(r'^spirit/', include('spirit.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()

