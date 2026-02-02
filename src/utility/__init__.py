"""
Initialize the utility module
"""
# Import all utility module components for easy access
from utility.market_calendar import (
    get_closed_count,
    market_is_open,
)
from utility.status_message_component import StatusMessageComponent
from utility.autoupdate_multiselect_component import aumc_get_instance

__all__ = [
    "get_closed_count",
    "market_is_open",
    "StatusMessageComponent",
    "aumc_get_instance",
    ]
