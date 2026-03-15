"""
Utility component for managing and displaying status
messages in a Streamlit page.
"""
# standard library imports
from typing import NamedTuple
from enum import Enum

# third party imports
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# local application imports
from utility import get_logger

# mark entry into the module
logger = get_logger(__name__)
logger.debug("In module %s", __name__)

class StatusTypeStyle(NamedTuple):
    """
    Styling parameters for StatusType
    """
    material: str   # the icon to display
    color: str      # the text color to be used

class StatusType(Enum):
    """
    Enumeration to define status types and corresponding styles
    """
    INFO = StatusTypeStyle(":material/thumb_up:","blue"),
    SUCCESS = StatusTypeStyle(":material/check:","green"),
    WARNING = StatusTypeStyle(":material/warning:","yellow"),
    ERROR = StatusTypeStyle(":material/error:","red"),

# Named tuple contains parameters for a status message
class StatusMessage(NamedTuple):
    """
    Structure to contain all the elements of a status message
    """
    # the StatusType for the message (INFO, SUCCESS, WARNING, ERROR)
    msg_status: StatusType
    # the text to display in the message area
    msg_text: str

_COMPONENT_INSTANCES = {}

class StatusMessageComponent:
    """
    Implements a utility component for managing and displaying status messages in a Streamlit page.
    """
    def __init__(self, key: str):
        """
        Initialize a StatusMessageComponent instance.

        Arguments:
            key (str) -- A string to use as the key for this instance
        """
        # mark entry into the function
        logger.debug("initializing status message with key = %s", key)
        # store the unique key assigned to this instance
        self._component_key: str = key

        # initialize the list of messages
        self._status_messages: list[StatusMessage] = []

    def set_status_message(
        self,
        msg_status: StatusType,
        msg_text: str,
    ):
        """
        Store the data needed to display the current status message
        into the session state for later retrieval and display.
        
        :param msg_status: the StatusType to use for displaying the message
        :param msg_text: the text to display in the status message
        """
        status_message = StatusMessage(msg_status, msg_text)
        logger.debug("Received status message: %s", status_message)
        self._status_messages.append(status_message)


    def show_status_messages(self):
        """
        Display the current list of status message and initialize to defaults
        """
        logger.debug("Displaying %s status messages", len(self._status_messages))
        for message in self._status_messages:
            status_style = message.msg_status.value[0]
            st.toast(
                    f":{status_style.color}[{message.msg_text}]",
                    icon=status_style.material,
                    )

        # reset the list of messages
        self._status_messages = []

def get_status_message_component(key: str) -> StatusMessageComponent:
    """
    Returns a StatusMessageComponent for the given key. If a component doesn't exist,
    a new one is created.

    Arguments:
        key -- the key for the requested StatusMessageComponent

    Returns:
        A StatusMessageComponent instance
    """
    # log entry into the function
    logger.debug("In get_status_message_component with key=%s", key)

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        logger.debug("Creating new instance")
        _COMPONENT_INSTANCES[key] = StatusMessageComponent(key)

    # log exit from the function
    logger.debug("Exiting get_status_message_component with key=%s", key)
    return _COMPONENT_INSTANCES[key]
