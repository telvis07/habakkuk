from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^api/', include('web.api_urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'clusters/$', 'web.views.clusters'),
    url(r'about/$', 'web.views.about'),
    url(r'^biblestudy/', 'web.views.biblestudy'),
    url(r'^topics/(?P<topic_name>[\w\d_]+)?/?$', 'web.views.topics'),
    url(r'^$', RedirectView.as_view(url='/biblestudy/', permanent=True), name='index'),
)

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
