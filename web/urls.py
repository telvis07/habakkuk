from django.conf.urls import patterns, url
from web import views

urlpatterns = patterns('web.views',
    url(r'^$', views.biblestudy),
)
