# test_period.py
from datetime import datetime as dt
from budgetreport import report

def test_periodStart():
    assert report.Period("year").getPeriodStart(dt(2021, 1, 1)) == dt(2021, 1, 1)
    assert report.Period("year").getPeriodStart(dt(2021, 6, 3)) == dt(2021, 1, 1)
    assert report.Period("year").getPeriodStart(dt(2021, 12, 31)) == dt(2021, 1, 1)
    assert report.Period("month").getPeriodStart(dt(2021, 3, 1)) == dt(2021, 3, 1)
    assert report.Period("month").getPeriodStart(dt(2021, 3, 15)) == dt(2021, 3, 1)
    assert report.Period("month").getPeriodStart(dt(2021, 3, 31)) == dt(2021, 3, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 1, 1)) == dt(2021, 1, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 4, 3)) == dt(2021, 1, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 6, 30)) == dt(2021, 1, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 7, 1)) == dt(2021, 7, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 9, 12)) == dt(2021, 7, 1)
    assert report.Period("biannual").getPeriodStart(dt(2021, 12, 31)) == dt(2021, 7, 1)
    assert report.Period("week").getPeriodStart(dt(2021, 3, 3)) == dt(2021, 3, 1)
    assert report.Period("week").getPeriodStart(dt(2021, 3, 8)) == dt(2021, 3, 8)
    assert report.Period("week").getPeriodStart(dt(2021, 3, 20)) == dt(2021, 3, 15)
    assert report.Period("week").getPeriodStart(dt(2021, 3, 28)) == dt(2021, 3, 22)
    assert report.Period("day").getPeriodStart(dt(2021, 3, 3)) == dt(2021, 3, 3)
