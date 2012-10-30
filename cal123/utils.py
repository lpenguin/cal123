__author__ = 'npryanichnikov'
from datetime import  date, timedelta
from models import Event
import calendar

def get_week_days():
    return ['Mon', 'Tue', 'Wen', 'Thr', 'Fri', 'Sat', 'Sun']

def get_month_grid(cal_obj, year, month):
    week_day_names = get_week_days()
    grid = []
    week = []
    cal = calendar.Calendar()
    first_week = True
    for day in cal.itermonthdates(year, month):
        events = Event.objects.filter(calendar=cal_obj, begin_date__gte=day, begin_date__lt=day+timedelta(days=1), canceled=0)
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