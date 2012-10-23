from django.conf.urls import patterns, include, url
from views import index_view, calendar_view, calendars_view, events_view, event_edit_view, event_view
from django.conf.urls.static import static
import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cal.views.home', name='home'),
    # url(r'^cal/', include('cal.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^$', index_view),
    (r'^calendar/(\d+)', calendar_view),
    (r'^calendars/', calendars_view),
    (r'^events/(\d+)/(\d+)/(\d+)/(\d+)', events_view),
    (r'^event_edit/(\d+)', event_edit_view),
    (r'^event/(\d+)/$', event_view),
    (r'^event/(\d+)/(\w+)$', event_view),

#    (r'^events_add/(\d+)/(\d+)/(\d+)/(\d+)', events_add_view),
)
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


