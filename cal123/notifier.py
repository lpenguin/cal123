__author__ = 'npryanichnikov'
# -*- coding: windows-1251 -*-

from cal123.models import *
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from cal123 import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

def get_accepted():
    accepted = EventGuest.objects.filter(status='a')
    return accepted

def get_pending():
    return EventGuest.objects.filter(status='p')

def notify_about_event(guest):
    if guest.status == 'a':
        guest_type = 'accepted'
    elif guest.status == 'p':
        guest_type = 'pending'
    else:
        raise NameError('guest status must be "a" or "p"')

    t = get_template('notify/notify_%s.html' % guest_type)
    html = t.render(Context({'guest': guest, 'user': guest.user,  'site_name': settings.SITE_NAME, 'days_left': guest.event.begin_date - timezone.now(),
                             'today':  timezone.now()}))
    if guest.user.email:
        try:
#            send_html_mail('notifier@calendar.com', guest.user.email, 'Calendar updates', html)
            send_html_mail('notifier@calendar.com', 'lpenguin@outlook.com', 'Calendar updates', html)
        finally:
            pass


def notify_events():
    # TODO: ТОДО: Нужно оптимизировать забпрос к БД, и убрать условия из if туда. Так же не нужно проверять уже прошедшие мероприятия
    accepted = get_accepted()
    for days_delta in [4, 1]:
        for guest in accepted:
        #            если до начала мероприятия осталось days_delta дней
        #            и или гость еще не оповещался или гость оповещался давно
        #             - оповестить
            if guest.event.canceled:
                continue

            if guest.event.begin_date - timezone.now() < timedelta(seconds=0):
                continue

            if guest.event.begin_date - timezone.now() > timedelta(days=days_delta-1) and\
               guest.event.begin_date - timezone.now() < timedelta(days=days_delta):
                if (guest.notify_date is None or\
                    timezone.now() - guest.notify_date > timedelta(days=1)):
                    guest.notify_date = timezone.now()
                    guest.save()
                    notify_about_event(guest)

    pending = get_pending()
    for days_delta in [7, 6, 5, 4, 3, 2, 1]:
        for guest in pending:
#            если до начала мероприятия осталось days_delta дней
#            и или гость еще не оповещался или гость оповещался давно
#             - оповестить
            if guest.event.canceled:
                continue

            if guest.event.begin_date - timezone.now() < timedelta(seconds=0):
                continue

            if guest.event.begin_date - timezone.now() > timedelta(days=days_delta-1) and\
               guest.event.begin_date - timezone.now() < timedelta(days=days_delta):
                if (guest.notify_date is None or\
                    timezone.now() - guest.notify_date > timedelta(days=1)):
                    guest.notify_date = timezone.now()
                    guest.save()
                    notify_about_event(guest)




def get_notifications():
    actions = EventAction.objects.filter(notification='f')
    notifications = dict()
    for action in actions:
        if action.type != 'a' and action.type != 'd':
            cal = action.event.calendar
            for user in cal.subscribers.all():
                if not user.id in notifications:
                    notifications[user.id] = []
                notifications[user.id].append(action)
    return notifications

def send_html_mail(me, to, subject, html):
    msg = MIMEMultipart('alternative')
    part_html = MIMEText(html.encode('utf-8'),'html', 'html')
    msg.attach(part_html)


    # me == the sender's email address
    # you == the recipient's email address

    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(settings.SMTP_HOST)
    s.sendmail(me, [to], msg.as_string())
    s.quit()

def notify(users, update_actions=True):
    actions_to_save = None
    for user_id in users.keys():
        user = User.objects.get(id=user_id)
        actions = users[user_id]
        t = get_template('notify/notify.html')
        html = t.render(Context({'user': user, 'actions': actions, 'site_name': settings.SITE_NAME}))
        if user.email:
            try:
                send_html_mail('notifier@calendar.com', user.email, 'Calendar updates', html)
                actions_to_save = actions
            finally:
                pass

    if actions_to_save and update_actions:
        for action in actions_to_save:
            action.notification='t'
            action.save()








