__author__ = 'nikita'
from django.contrib import admin
from cal123.models import Event, Calendar, EventGuest, EventAction

admin.site.register(Event)
admin.site.register(EventGuest)
admin.site.register(Calendar)
admin.site.register(EventAction)




