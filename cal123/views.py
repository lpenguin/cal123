from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.forms import UserCreationForm

from utils import *
from models import Calendar, Event, EventGuest, EventAction

from forms import *

import notifier


def index_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/calendars')

    t = get_template('index.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)

def about_view(request):
    t = get_template('about.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)

def login_or_register_view(request):
    if 'next' in request.GET:
        request.session['next'] = request.GET['next']
    login_form = LoginForm()
    register_form = RegistrationForm()
    t = get_template('login_or_register.html')
    html = t.render( RequestContext(request, {'login_form': login_form, 'register_form': register_form}))
    return HttpResponse(html)

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.save()
            new_user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth.login(request, new_user)
            next = '/'
            if 'next' in request.session:
                next = request.session['next']
                del request.session['next']
            return HttpResponseRedirect(next)
    else:
        form = RegistrationForm ()
    t = get_template('register.html')
    html = t.render( RequestContext(request, {'form': form}))
    return HttpResponse(html)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = auth.authenticate(username=cd['login'], password=cd['password'])
            if user is not None and user.is_active:
                auth.login(request, user)
                next = '/'
                if 'next' in request.session:
                    next = request.session['next']
                    del request.session['next']
                return HttpResponseRedirect(next)
    else:
        form = LoginForm()
    t = get_template('login.html')
    html = t.render( RequestContext(request, {'form': form}))
    return HttpResponse(html)

@login_required
def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")

@login_required
def calendars_view(request):
    calendars = Calendar.objects.filter(owned_by=request.user)
    subscribe_calendars = Calendar.objects.filter(subscribers=request.user)
    t = get_template('calendars.html')
    html = t.render(Context({'user': request.user, 'calendars': calendars, 'subscribe_calendars': subscribe_calendars}))
    return HttpResponse(html)

@login_required
def calendar_unsubscribe_view(request, calendar_id):
    cal = Calendar.objects.get(id=calendar_id)
    if cal.owned_by == request.user:
        return  HttpResponseRedirect('/calendar/%s' % calendar_id)
    cal.subscribers.remove(request.user)
    today = datetime.today()
    events = Event.objects.filter(calendar=cal, begin_date__gte = today)
    for event in events:
        try:
            guest = EventGuest.objects.get(user=request.user, event=event)
            guest.delete()
        except ObjectDoesNotExist:
            pass

    cal.save()
    return  HttpResponseRedirect('/calendar/%s' % calendar_id)

@login_required
def calendar_subscribe_view(request, calendar_id):
    cal = Calendar.objects.get(id=calendar_id)
    cal.subscribers.add(request.user)
    today = datetime.today()
    events = Event.objects.filter(calendar=cal, begin_date__gte = today)
    notifs = []
    for event in events:
        try:
            guest = EventGuest.objects.get(user=request.user, event=event)
        except ObjectDoesNotExist:
            guest = EventGuest(user=request.user, event=event)
        finally:
            guest.save()
            action = EventAction(user=event.owned_by, event=event, type='c', date=today)
            notifs.append(action)
    notif_users = dict()
    notif_users[request.user.id] = notifs
    notifier.notify(notif_users, False)
    cal.save()
    return  HttpResponseRedirect('/calendar/%s' % calendar_id)

@login_required
def calendar_view(request, calendar_id, year=None, month=None):
    cal = Calendar.objects.get(id=calendar_id)

    if not request.user in cal.subscribers.all():
        t = get_template('calendar_subscribe.html')
        html = t.render(Context({'calendar': cal, 'user': request.user}))
        return HttpResponse(html)
    if month == None and year == None:
        now = date.today()
        month = now.month
        year = now.year
    else:
        year=int(year)
        month=int(month)


    grid = get_month_grid(cal, year, month)

    monthes = [ date(year=year, month=month_num, day=1) for month_num in xrange(1, 13)]

    t = get_template('calendar.html')
    html = t.render(Context({'grid': grid, 'user': request.user, 'calendar': cal,
                             'cal_date': date(year=year, month=month, day=1),
                             'subscribers': cal.subscribers.all(),
                             'monthes': monthes
                            }))
    return HttpResponse(html)

@login_required
def events_view(request, calendar_id, year, month, day):
    dt = date(year=int(year), month=int(month), day=int(day))
    cal = Calendar.objects.get(id=calendar_id)
    events = Event.objects.filter(calendar=cal, begin_date__gte=dt, begin_date__lt=dt+timedelta(days=1), canceled=0)

    t = get_template('events.html')
    html = t.render(Context({'user': request.user, 'calendar': cal, 'events': events, 'date': dt}))
    return HttpResponse(html)

@login_required
def event_view(request, event_id, action=''):
    event = Event.objects.get(id=event_id)

    if action == 'accept':
        event_guest = EventGuest.objects.get(event=event, user=request.user)
        event_guest.status='a'
        event_guest.save()
        return HttpResponseRedirect('/event/'+str(event_id))
    elif action == 'decline':
        event_guest = EventGuest.objects.get(event=event, user=request.user)
        event_guest.status='d'
        event_guest.save()
        return HttpResponseRedirect('/event/'+str(event_id))

    accepted =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='a') ]
    pending =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='p') ]
    declined =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='d') ]


    t = get_template('event_view.html')
    html = t.render(Context({'user': request.user, 'event': event, 'accepted': accepted, 'pending': pending, 'declined': declined}))
    return HttpResponse(html)

@login_required
def event_add_view(request, calendar_id,  year, month, day):
    calendar = Calendar.objects.get(id=calendar_id)

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            event = Event()
            event.begin_date = cd['begin_date']
            event.name = cd['name']
            event.owned_by = request.user
            event.calendar=calendar
            event.description = cd['description']
            event.end_date = cd['end_date']
            event.save()
            guests = []
            for subscriber in calendar.subscribers.all():
                guest = EventGuest(event=event, user=subscriber)
                guest.save()
                guests.append(guest)

            event.guests = guests
            event.save()

            return HttpResponseRedirect('/event/'+str(event.id))
    else:
        form = EventForm()
    begin_date = datetime(year=int(year), month=int(month), day=int(day), hour=12)
    end_date = datetime(year=int(year), month=int(month), day=int(day), hour=15)

    #    form.begin_date = begin_date
    t = get_template('event_edit.html')
    html = t.render( RequestContext(request, {'form': form, 'calendar': calendar, 'begin_date':begin_date, 'end_date': end_date, 'date': begin_date}))
    return HttpResponse(html)

@login_required
def event_edit_view(request, id, action=None):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            event = Event.objects.get(id=id)
            event.name = cd['name']
            event.description = cd['description']
            event.begin_date = cd['begin_date']
            event.end_date = cd['end_date']
            event.save()
            return HttpResponseRedirect('/event/'+str(id))
    else:
        event = Event.objects.get(id=id)
        calendar = event.calendar
        if action == 'cancel':
            event.canceled = True
            event.save()
            return HttpResponseRedirect('/calendar/'+str(calendar.id))

        form = EventForm({'name': event.name, 'description': event.description,
                          'begin_date': event.begin_date, 'end_date': event.end_date})
        form.name=event.name
    t = get_template('event_edit.html')
    html = t.render( RequestContext(request, {'form': form, 'event': event, 'edit': '1'}))
    return HttpResponse(html)
#    return render_to_response('event_edit.html', {'form': form, calendar: cal})