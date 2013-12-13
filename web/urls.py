from django.conf.urls import patterns, include, url

urlpatterns = patterns('web.views',
    url(r'^$', 'clusters'),
    url(r'^(?P<datestr>\d{8})$', 'clusters'),
    url(r'^(?P<datestr>\d{8})/(?P<range>\d{1,3})$', 'clusters'),
)
