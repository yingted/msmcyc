from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'msmcyc.views.home', name='home'),
    # url(r'^msmcyc/', include('msmcyc.foo.urls')),
    url(r'^add_event',views.add_event),
    url(r'^contact',views.contact),
    url(r'^events',views.events),
    url(r'',views.index),
)
