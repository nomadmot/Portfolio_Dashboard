'''
exercise functions from core.periods module
'''
# import standard libraries
import sys
import logging

# adjust path for app imports from src directory
sys.path.append("src")

# import application modules
#pylint: disable=wrong-import-position
from core import Periods, get_period_dates


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

begin_date, end_date = get_period_dates(Periods.D30)
logger.info("D30 Period: begin_date=%s, end_date=%s", begin_date, end_date)

begin_date, end_date = get_period_dates(Periods.D50)
logger.info("D50 Period: begin_date=%s, end_date=%s", begin_date, end_date)

begin_date, end_date = get_period_dates(Periods.D90)
logger.info("D90 Period: begin_date=%s, end_date=%s", begin_date, end_date)

begin_date, end_date = get_period_dates(Periods.YTD)
logger.info("YTD Period: begin_date=%s, end_date=%s", begin_date, end_date)

begin_date, end_date = get_period_dates(Periods.YR1)
logger.info("YR1 Period: begin_date=%s, end_date=%s", begin_date, end_date)

begin_date, end_date = get_period_dates(Periods.ALL)
logger.info("ALL Period: begin_date=%s, end_date=%s", begin_date, end_date)
