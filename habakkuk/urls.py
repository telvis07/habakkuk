from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'habakkuk.views.home', name='home'),
    # url(r'^habakkuk/', include('habakkuk.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^web/', include('web.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
