import pytest
import datetime

from utility import Periods, get_period_dates, get_period
def test_get_period():
    assert get_period('D90') == Periods.D90
    assert get_period('D50') == Periods.D50
    assert get_period('YTD') == Periods.YTD
    # invalid period defaults to D30
    assert get_period('XXX') == Periods.D30
def test_get_period_dates():
    begin_date, end_date = get_period_dates(Periods.D30)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())
    begin_date, end_date = get_period_dates(Periods.D50)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())
    begin_date, end_date = get_period_dates(Periods.D90)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())
    begin_date, end_date = get_period_dates(Periods.YTD)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())
    begin_date, end_date = get_period_dates(Periods.YR1)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())
    begin_date, end_date = get_period_dates(Periods.ALL)
    assert begin_date is not None
    assert end_date == pytest.approx(datetime.date.today())