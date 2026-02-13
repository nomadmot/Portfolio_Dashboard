"""
Utility component for managing and displaying a status
message in a Streamlit page.
"""
# standard library imports
import logging
from types import MethodType
from typing import NamedTuple

# third party imports
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# local application imports
from config import SETTINGS

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
# mark entry into the module
logger.debug("Entering StatusMessageComponent module")

# Named tuple contains parameters for a status message
class StatusMessage(NamedTuple):
    """
    Structure to contain all the elements of a status message
    """
    # the Streamlit function to set the message (info, warn, error)
    msg_function: MethodType
    # the text to display in the message area
    msg_text: str
    # the icon (if any) to display in the message area
    msg_icon: str|None

_DEFAULT_TEXT = ""
_COMPONENT_INSTANCES = {}

class StatusMessageComponent:
    """
    Implements a utility component for managing and displaying
    a status message in a Streamlit page.
    """
    def __init__(self, key: str, default_text: str|None):
        """
        Initialize a StatusMessageComponent instance. Optionally specify default text
        to use in an empty component

        Arguments:
            key (str) -- A string to use as the key for this instance
            default_text -- Text to be displayed when there is no other message
        """
        # mark entry into the function
        logger.debug("initializing status message with key = %s and default text = %s",
                     key, default_text)
        # store the unique key assigned to this instance
        self._component_key: str = key
        # set the default text
        if default_text:
            self._default_text = default_text
        else:
            self._default_text = _DEFAULT_TEXT
        # create the default message to display the default text
        self._default_message: StatusMessage = StatusMessage(st.info,
                                                            self._default_text,
                                                            None
                                                            )
        # initialize the current message to display the default
        self._current_message = self._default_message
        # Streamlit placeholder for the message component
        self._placeholder: DeltaGenerator

    def render(self):
        """
        Place the status message component on the Streamlit page
        """
        logger.debug("in render, current message is %s", self._current_message)
        # create the streamlit placeholder
        self._placeholder = st.empty()

        # display the message
        with self._placeholder:
            # unpack the current message
            msg_function, msg_text, msg_icon = self._current_message
            # display the current message
            msg_function(msg_text, icon=msg_icon)


    def set_status_message(
        self,
        msg_function: MethodType,
        msg_text: str,
        msg_icon:str|None = None
    ):
        """
        Store the data needed to display the current status message
        into the session state for later retrieval and display.
        
        :param msg_function: the Streamlit method to use for posting the message
            (st.info, st.warn, or st.error)
        :param msg_text: the text to display in the status message
        :param msg_icon: an icon to display in the status message
            (defaults to None)
        
        """
        self._current_message = StatusMessage(
                                            msg_function,
                                            msg_text,
                                            msg_icon
                                            )

        # Write out the message to the current interface
        logger.debug("Writing status message to UI: %s", self._current_message)
        with self._placeholder:
            msg_function(msg_text, icon=msg_icon)


    def clear_status_message(self):
        """
        Clear the current status message and initialize to defaults
        """
        logger.debug("Setting status message to default: %s", self._default_message)
        self._current_message = self._default_message


def get_status_message_component(key: str, default_text: str|None = None) -> StatusMessageComponent:
    """
    Returns a StatusMessageComponent for the given key. If a component doesn't exist,
    a new one is created.

    Arguments:
        key -- the key for the requested TimeMachineComponent
        default_text -- the default text to display

    Returns:
        A TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In get_status_message_component with key=%s, default_text=%s", key, default_text)

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        logger.debug("Creating new instance")
        _COMPONENT_INSTANCES[key] = StatusMessageComponent(key, default_text)

    # log exit from the function
    logger.debug("Exiting get_status_message_component with key=%s", key)
    return _COMPONENT_INSTANCES[key]
