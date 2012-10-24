__author__ = 'nikita'

from django.db import models
from django.contrib.auth.models import User
#consts

ANYONE_PERMISSION = 1
ONLYINLIST_PERMISSION = 2
ONLYME_PERMISSION = 3

EDITPERMISSON = (
    ('a', 'Anyone'),
    ('l', 'Only in list'),
    ('m', 'Only me'),
)
GUESTSTATUS = (
    ('p', 'Pending'),
    ('a', 'Accepted'),
    ('d', 'Declined'),
    )


class Profile(models.Model):
    user = models.ForeignKey(User)
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)


class Calendar(models.Model):
    name = models.CharField(max_length=200)
    description =  models.TextField(blank=True)
    owned_by = models.ForeignKey(User, related_name='+')
    edit_permission = models.CharField(max_length=1, choices=EDITPERMISSON)
    subscribers = models.ManyToManyField(User, blank=True)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description =  models.TextField(blank=True)
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    owned_by = models.ForeignKey(User, related_name='+')
    calendar = models.ForeignKey(Calendar)
    edit_permission = models.CharField(max_length=1, choices=EDITPERMISSON)
    guests = models.ManyToManyField('EventGuest', blank=True, related_name='+')
    def __unicode__(self):
        return self.name

class EventGuest(models.Model):
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1, default='p', choices=GUESTSTATUS)
    event = models.ForeignKey(Event, related_name='+')
    def __unicode__(self):
        return str(self.user)+' '+self.event.name

#    editors = models.ManyToManyField(User)
#    pending = models.ManyToManyField(User)
#    accepted = models.ManyToManyField(User)
#    declined = models.ManyToManyField(User)



#class EventEditors(models.Model):
#    event = models.ManyToManyField(Event)
#    user = models.ManyToManyField(models.User)
#
#class CalendarEditors(models.Model):
#    calendar = models.ManyToManyField(Calendar)
#    user = models.M

