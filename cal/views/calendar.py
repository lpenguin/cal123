from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from datetime import datetime, date, timedelta
import calendar

def get_month_grid(year, month):
    grid = []
    week = []
    cal = calendar.Calendar()
    for day in cal.itermonthdates(year, month):
        week.append( dict(date=day, event=None, weekday=day.weekday()))
        if day.weekday() == 6:
            grid.append(week)
            week = []
    return grid
    
def month_view(request, year=None, month=None):
    if month == None and year == None:
        now = date.now()
        month = now.month
        year = now.year
    grid = get_month_grid(year, month)
    html = t.render(Context({'grid': grid}))
    return HttpResponse(html)
        
    
        
        
    