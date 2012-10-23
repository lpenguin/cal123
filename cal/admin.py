__author__ = 'nikita'
from django.contrib import admin
from cal.models import Event, Calendar, EventGuest

admin.site.register(Event)
admin.site.register(EventGuest)
admin.site.register(Calendar)




