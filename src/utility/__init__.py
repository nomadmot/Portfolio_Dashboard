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
    calculate_end_date,
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
from .account_selection_component import get_account_selection_component
from .time_machine_component import get_time_machine_component
from .system_info import get_client_ip, get_memory_size, show_system_info
from .comparison_options import (
    EMP_DASH,
    COMPARISON_PREFIX,
    disambiguated_name,
    comparison_options,
    is_account_option,
    account_name_from_option,
    account_id_for_option,
)

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
    "get_account_selection_component",
    "get_time_machine_component",
    "show_system_info",
    "get_client_ip",
    "get_memory_size",
    "EMP_DASH",
    "COMPARISON_PREFIX",
    "disambiguated_name",
    "comparison_options",
    "is_account_option",
    "account_name_from_option",
    "account_id_for_option",
    "calculate_begin_date",
    "calculate_end_date",
    "count_trading_days",
]
