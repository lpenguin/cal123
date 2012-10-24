from django.conf.urls.defaults import *
from views import *
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
    (r'^about', about_view),

    (r'^calendar/(\d+)/(\d+)/(\d+)', calendar_view),
    (r'^calendar/(\d+)', calendar_view),
    (r'^calendars/', calendars_view),
    (r'^events/(\d+)/(\d+)/(\d+)/(\d+)', events_view),
    (r'^event_add/(\d+)/(\d+)/(\d+)/(\d+)', event_add_view),
    (r'^event_edit/(\d+)/(\w+)$', event_edit_view),
    (r'^event_edit/(\d+)$', event_edit_view),
    (r'^event/(\d+)/$', event_view),
    (r'^event/(\d+)/(\w+)$', event_view),
    (r'^accounts/login_or_register/', login_or_register_view),
    (r'^accounts/login/', login_view),
    (r'^accounts/logout/', logout_view),
    (r'^accounts/register/', register_view),
    (r'calendar_subscribe/(\d+)', calendar_subscribe_view),
    (r'calendar_unsubscribe/(\d+)', calendar_unsubscribe_view),

#    (r'^events_add/(\d+)/(\d+)/(\d+)/(\d+)', events_add_view),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


