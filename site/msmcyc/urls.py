from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'msmcyc.views.home', name='home'),
    # url(r'^msmcyc/', include('msmcyc.foo.urls')),
    url(r'^add_(event|update|api_key)',views.add_entity),
    url(r'^contact',views.contact),
    url(r'^events',views.events),
    url(r'^signup/([^/]*)',views.signup),
    url(r'^ajax/prev_players/([^/]*)/(.*)$',views.prev_players),
    url(r'^ajax/team_prefix/(.*)$',views.team_prefix),
    url(r'^view/([^/]*)/([1-9][0-9]*)$',views.view),
    url(r'^view/([^/]*)/([1-9][0-9]*)/([^/]*)$',views.view),
    url(r'^export/([^/]*)/([1-9][0-9]*)/([1-9][0-9]*)/([^/]*)$',views.export),
    url(r'^download/([^/]*)/([^/]*)/([1-9][0-9]*)$',views.download),
    url(r'^download/([^/]*)/([^/]*)/([1-9][0-9]*)/([^/]*)$',views.download),
    url(r'',views.index),
)
