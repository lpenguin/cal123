#!/usr/bin/python

__author__ = 'npryanichnikov'
import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = "cal123.settings"
sys.path.append('/home/lilacpenguin/opt/lib/python2.6/site-packages/django_coffeescript-0.3-py2.6.egg/')
sys.path.append('/home/lilacpenguin/opt/lib/python2.6/site-packages/Django-1.4.2-py2.6.egg//')

from cal123 import notifier
users_dict =  notifier.get_notifications()
notifier.notify(users_dict )
notifier.notify_events()
