# period.py
import re, calendar
from datetime import datetime as dt

class Period:
    def __init__(self, period):
        self.period = period

    def getPeriodStart(self, date):
        ret = None
        if self.period == 'year':
            ret = dt(date.year, 1, 1)
        elif self.period == 'biannual':
            if date.month < 7:
                ret = dt(date.year, 1, 1) # 1st January
            else:
                ret = dt(date.year, 7, 1) # 1st July
        elif self.period == 'quarter':
            if date.month >= 1 and date.month <= 3:
                ret = dt(date.year, 1, 1)
            elif date.month >= 4 and date.month <= 6:
                ret = dt(date.year, 4, 1)
            elif date.month >= 7 and date.month <= 9:
                ret = dt(date.year, 7, 1)
            else:
                ret = dt(date.year, 10, 1)
        elif self.period == 'month':
            ret = dt(date.year, date.month, 1)
        elif self.period == 'week':
            if date.day < 8: day = 1
            elif date.day < 15: day = 8
            elif date.day < 22: day = 15
            else: day = 22 # FIXME: Last week may be 7 to 10 days
            ret = dt(date.year, date.month, day)
        elif self.period == 'day':
            ret = date
        else:
            ret = dt(1970, 1, 1) # If period == 'none', then period starts from 1970
        return ret.date()

    def getPeriodEnd(self, date):
        ret = None
        last_day_of_month = calendar.monthrange(date.year, date.month)[1]
        if self.period == 'year':
            ret = dt(date.year, 12, 31)
        elif self.period == 'biannual':
            if date.month < 7:
                ret = dt(date.year, 6, 30) # 1st January
            else:
                ret = dt(date.year, 12, 31) # 1st July
        elif self.period == 'quarter':
            if date.month >= 1 and date.month <= 3:
                ret = dt(date.year, 3, 31)
            elif date.month >= 4 and date.month <= 6:
                ret = dt(date.year, 6, 30)
            elif date.month >= 7 and date.month <= 9:
                ret = dt(date.year, 9, 30)
            else:
                ret = dt(date.year, 12, 31)
        elif self.period == 'month':
            ret = dt(date.year, date.month, last_day_of_month)
        elif self.period == 'week':
            if date.day < 8: day = 7
            elif date.day < 15: day = 14
            elif date.day < 22: day = 21
            else: day = last_day_of_month # FIXME: Last week may be 7 to 10 days
            ret = dt(date.year, date.month, day)
        elif self.period == 'day':
            ret = date
        else:
            ret = date
        return ret.date()
