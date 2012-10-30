#!/usr/bin/python

__author__ = 'npryanichnikov'
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = "cal123.settings"


from cal123 import notifier


sys.path.append('/home/lilacpenguin/opt/lib/python2.6/site-packages/django_coffeescript-0.3-py2.6.egg/')
sys.path.append('/home/lilacpenguin/opt/lib/python2.6/site-packages/django-1.4-py2.6.egg/')


os.environ['DJANGO_SETTINGS_MODULE'] = "cal123.settings"


users_dict =  notifier.get_notifications()
notifier.notify(users_dict )
notifier.notify_events()






