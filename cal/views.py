from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, date, timedelta
import calendar
from models import Calendar, Event, EventGuest
from forms import EventForm
from django.template import RequestContext
def index_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/calendars')

    t = get_template('index.html')
    html = t.render(Context({'user': request.user}))
    return HttpResponse(html)

def calendars_view(request):
    calendars = Calendar.objects.filter(owned_by=request.user)
    t = get_template('calendars.html')
    html = t.render(Context({'user': request.user, 'calendars': calendars}))
    return HttpResponse(html)

def get_week_days():
    return ['Mon', 'Tue', 'Wen', 'Thr', 'Fri', 'Sat', 'Sun']

def get_month_grid(cal_obj, year, month):

    week_day_names = get_week_days()
    grid = []
    week = []
    cal = calendar.Calendar()
    first_week = True
    for day in cal.itermonthdates(year, month):
        events = Event.objects.filter(calendar=cal_obj, begin_date__gte=day, begin_date__lte=day+timedelta(days=1))
        inactive = False
        istoday = day == date.today()
        day_name = ''

        if day.month != month:
            inactive=True
        if first_week:
            day_name = week_day_names[day.weekday()]
        week.append( dict(date=day, weekday=day.weekday(), inactive=inactive, day_name=day_name, istoday=istoday, events=events ))
        if day.weekday() == 6:
            grid.append(week)
            week = []
            first_week = False
    return grid

def calendar_view(request, calendar_id, year=None, month=None):
    if month == None and year == None:
        now = date.today()
        month = now.month
        year = now.year
    calendar = Calendar.objects.get(id=calendar_id)
    grid = get_month_grid(calendar, year, month)
    t = get_template('calendar.html')
    html = t.render(Context({'grid': grid, 'user': request.user, 'calendar': calendar}))
    return HttpResponse(html)

def events_view(request, calendar_id, year, month, day):
    dt = date(year=int(year), month=int(month), day=int(day))
    cal = Calendar.objects.get(id=calendar_id)
    events = Event.objects.filter(calendar=cal, begin_date__gte=dt, begin_date__lte=dt+timedelta(days=1))
#    if len(events) == 1:
#        return HttpResponseRedirect('/event/'+str(event_id))

    t = get_template('events.html')
    html = t.render(Context({'user': request.user, 'calendar': calendar, 'events': events, 'date': dt}))
    return HttpResponse(html)

def event_view(request, event_id, action=''):
    event = Event.objects.get(id=event_id)
    event_guest = EventGuest.objects.get(event=event, user=request.user)
    if action == 'accept':
        event_guest.status='a'
        event_guest.save()
        return HttpResponseRedirect('/event/'+str(event_id))
    elif action == 'decline':
        event_guest.status='d'
        event_guest.save()
        return HttpResponseRedirect('/event/'+str(event_id))

    accepted =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='a') ]
    pending =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='p') ]
    declined =  [ guest.user for guest in EventGuest.objects.filter(event=event, status='d') ]


    t = get_template('event_view.html')
    html = t.render(Context({'user': request.user, 'event': event, 'accepted': accepted, 'pending': pending, 'declined': declined}))
    return HttpResponse(html)

def event_edit_view(request, event_id):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            event = Event.objects.get(id=event_id)
            event.name = cd['name']
            event.description = cd['description']
            event.begin_date = cd['begin_date']
            event.end_date = cd['end_date']
            event.save()
            return HttpResponseRedirect('/event/'+str(event_id))
    else:
        event = Event.objects.get(id=event_id)
        form = EventForm({'name': event.name, 'description': event.description,
                          'begin_date': event.begin_date, 'end_date': event.end_date})
        form.name=event.name
    t = get_template('event_edit.html')
    html = t.render( RequestContext(request, {'form': form, 'event': event}))
    return HttpResponse(html)
#    return render_to_response('event_edit.html', {'form': form, calendar: cal})