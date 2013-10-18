from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^$', 'web.views.home', name='home'),
    url(r'^api/', include('web.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
