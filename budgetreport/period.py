# period.py
import re, calendar
from datetime import datetime as dt

class Period:
    def __init__(self, period):
        self.period = period

    def getPeriodStart(self, date):
        if self.period == 'year':
            return dt(date.year, 1, 1)
        elif self.period == 'biannual':
            if date.month < 7:
                return dt(date.year, 1, 1) # 1st January
            else:
                return dt(date.year, 7, 1) # 1st July
        elif self.period == 'month':
            return dt(date.year, date.month, 1)
        elif self.period == 'week':
            if date.day < 8: day = 1
            elif date.day < 15: day = 8
            elif date.day < 22: day = 15
            else: day = 22 # FIXME: Last week may be 7 to 10 days
            return dt(date.year, date.month, day)
        elif self.period == 'day':
            return date
        else:
            return dt(1970, 1, 1) # If period == 'none', then period starts from 1970
 
    def getPeriodEnd(self, date):
        last_day_of_month = calendar.monthrange(date.year, date.month)[1]
        if self.period == 'year':
            return dt(date.year, 12, 31)
        elif self.period == 'biannual':
            if date.month < 7:
                return dt(date.year, 6, 30) # 1st January
            else:
                return dt(date.year, 12, 31) # 1st July
        elif self.period == 'month':
            return dt(date.year, date.month, last_day_of_month)
        elif self.period == 'week':
            if date.day < 8: day = 7
            elif date.day < 15: day = 14
            elif date.day < 22: day = 21
            else: day = last_day_of_month # FIXME: Last week may be 7 to 10 days
            return dt(date.year, date.month, day)
        elif self.period == 'day':
            return date
        else:
            return date
 
