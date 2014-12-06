from django.conf.urls import patterns, include, url

urlpatterns = patterns('web.views',
    url(r'^clusters/$', 'clusters_data'),
    url(r'^clusters/(?P<datestr>\d{8})$', 'clusters_data'),
    url(r'^clusters/(?P<datestr>\d{8})/(?P<range>\d{1,3})$', 'clusters_data'),
    url(r'^topics/$', 'topics_api')
)
