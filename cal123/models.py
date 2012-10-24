__author__ = 'nikita'

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
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

ACTION = (
    ('c', 'Event created'),
    ('d', 'Event date modified'),
    ('t', 'Event text modified'),
#    ('j', 'Guest joined'),
    ('a', 'Guest accepted'),
    ('d', 'Guest declined'),
    ('r', 'Event cancelled')
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
    canceled = models.BooleanField(default=False)
#    guests = models.ManyToManyField('EventGuest', blank=True, related_name='+')
    def __unicode__(self):
        return self.name


    def save(self, *args, **kwargs):
        if not self.id:
            super(Event, self).save(*args, **kwargs)
            action = EventAction(user=self.owned_by, event=self, type='c', date=datetime.today())
            action.save()
        else:
            selfdb = Event.objects.get(id=self.id)
            if selfdb.begin_date != self.begin_date or selfdb.end_date != self.end_date:
                action = EventAction(user=self.owned_by, event=self, type='d', date=datetime.today())
                action.save()
            if selfdb.description != self.description or selfdb.name != self.name:
                action = EventAction(user=self.owned_by, event=self, type='t', date=datetime.today())
                action.save()
            if self.canceled == True:
                action = EventAction(user=self.owned_by, event=self, type='r', date=datetime.today())
                action.save()
            super(Event, self).save(*args, **kwargs)

         # Call the "real" save() method.

#    def delete(self, *args, **kwargs):
#        if self.id:
#            action = EventAction(user=self.owned_by, event=self, type='r', date=datetime.today())
#            action.save()
#
#        super(Event, self).delete(*args, **kwargs) # Call the "real" save() method.

class EventGuest(models.Model):
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1, default='p', choices=GUESTSTATUS)
    event = models.ForeignKey(Event, related_name='+')
    def __unicode__(self):
        return str(self.user)+' '+self.event.name

    def save(self, *args, **kwargs):
        if self.id:
            if self.status == 'a':
                action = EventAction(user=self.user, event=self.event, type='a', date=datetime.today())
                action.save()
            if self.status == 'd':
                action = EventAction(user=self.user, event=self.event, type='d', date=datetime.today())
                action.save()

        super(EventGuest, self).save(*args, **kwargs) # Call the "real" save() method.


class EventAction(models.Model):
    type = models.CharField(max_length=1, choices=ACTION)
    event = models.ForeignKey(Event)
    user = models.ForeignKey(User)
    date = models.DateTimeField()
    notification  = models.CharField(max_length=1,default='f')
    def __unicode__(self):
        return str(self.user)+' '+self.event.name+' '+self.type

