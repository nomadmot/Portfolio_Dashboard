"""
Initialize the utility module
"""
# Export all utility module components for easy access
from utility.logging import get_logger
from utility.database import DATABASE_CONNECTION
from utility.market_calendar import (
    get_closed_count,
    market_is_open,
)
from utility.status_message_component import get_status_message_component, StatusType
from utility.autoupdate_multiselect_component import get_aumc_instance
from utility.time_machine_component import get_time_machine_component
from utility.system_info import get_client_ip, get_memory_size, show_system_info

__all__ = [
    "get_logger",
    "DATABASE_CONNECTION",
    "get_closed_count",
    "market_is_open",
    "get_status_message_component",
    "StatusType",
    "get_aumc_instance",
    "get_time_machine_component",
    "show_system_info",
    "get_client_ip",
    "get_memory_size",
    ]
