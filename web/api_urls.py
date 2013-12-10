from django.conf.urls import patterns, include, url

urlpatterns = patterns('web.views',
    url(r'^query/$', 'query'),
    url(r'^query/(?P<datestr>\d{8})$', 'query'),
    url(r'^query/(?P<datestr>\d{8})/(?P<range>\d{1,3})$', 'query'),
)
