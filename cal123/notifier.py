__author__ = 'npryanichnikov'

from cal123.models import *
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.template import Context
from cal123 import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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








