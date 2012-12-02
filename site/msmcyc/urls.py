from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'msmcyc.views.home', name='home'),
    # url(r'^msmcyc/', include('msmcyc.foo.urls')),
    url(r'^add_(event|update)',views.add_entity),
    url(r'^contact',views.contact),
    url(r'^events',views.events),
    url(r'^signup/([^/]*)$',views.signup),
    url('^signup/([^/]*)/([1-9][0-9]*)/([A-Za-z_\']*)$',views.signup),
    url(r'^ajax/([^/]*)/(.*)$',views.prev_players),
    url(r'',views.index),
)
