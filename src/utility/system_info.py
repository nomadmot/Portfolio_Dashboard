"""
Functions related to system information and management
"""
# standard imports
import logging

# 3rd party imports
from streamlit import context

#local imports
import config


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(config.LOGLEVEL_APPLICATION)
# mark entry into the module
logger.debug("Entering module %s", __name__)


def get_client_ip() -> str:
    """
    Get the client IP address. If the IP address is not available in the Streamlit context,
    default to localhost.

    Returns:
        The IP address of the client. (Default: localhost)
    """
    logger.debug("Entering function get_client_ip")

    client_ip = context.ip_address
    if client_ip is None:
        # default to localhost
        logger.debug("context.ip_address is not set")
        client_ip = "127.0.0.1"

    logger.debug("get_client_ip returns: %s", client_ip)
    return client_ip
