"""
Initialize the utility module
"""
# Export all utility module components for easy access
from .logging import get_logger
from .database import DATABASE_CONNECTION
from .market_calendar import (
    get_closed_count,
    market_is_open,
    calculate_begin_date,
    count_trading_days,
)
from .periods_enum import Periods
from .periods import (
    get_period_dates,
    get_period,
    get_market_days_for_period,
)
from .stock_data import (
    YfPeriods,
    get_stock_history,
    get_security_info,
    get_basic_quote,
)

from .status_message_component import get_status_message_component, StatusType
from .autoupdate_multiselect_component import get_aumc_instance
from .time_machine_component import get_time_machine_component
from .system_info import get_client_ip, get_memory_size, show_system_info

__all__ = [
    "get_logger",
    "DATABASE_CONNECTION",
    "get_closed_count",
    "market_is_open",
    "Periods",
    "get_period_dates",
    "get_period",
    "get_market_days_for_period",
    "YfPeriods",
    "get_security_info",
    "get_basic_quote",
    "get_stock_history",
    "get_status_message_component",
    "StatusType",
    "get_aumc_instance",
    "get_time_machine_component",
    "show_system_info",
    "get_client_ip",
    "get_memory_size",
    "calculate_begin_date",
    "count_trading_days",
]
