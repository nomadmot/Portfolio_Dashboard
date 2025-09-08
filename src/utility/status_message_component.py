"""
Utility component for managing and displaying a status
message in a Streamlit page.
"""
import streamlit as st
import streamlit.logger
import config

# Initialize logging
logger = streamlit.logger.get_logger(st.__name__)
logger.setLevel(config.LOGLEVEL_STREAMLIT)
# mark entry into the module
logger.debug("Entering StatusMessageComponent module")

class StatusMessageComponent:
    """
    Implements a utility component for managing and displaying
    a status message in a Streamlit page. Uses class methods for
    all functionality to avoid the need for instantiation.
    """
    STATUS_MESSAGE_KEY = "status_message_component"

    @classmethod
    def set_status_message(
        cls,
        msg_function,
        msg_text,
        msg_icon
    ):
        """
        Store the data needed to display the current status message
        into the session state for later retrieval and display.
        """
        status_message = (
            msg_function,
            msg_text,
            msg_icon
        )

        # Write out the message to the current interface
        logger.debug("Writing status message to UI: %s", status_message)
        msg_function(msg_text, icon=msg_icon)

        # Store the message in session state for later retrieval
        logger.debug("Setting status message in session state: %s",
                     status_message
                     )
        st.session_state[cls.STATUS_MESSAGE_KEY] = status_message

    @classmethod
    def display_status_message(cls):
        """
        Display the current status message stored in the session state.
        If no status message is stored, display a default informational message.
        """
        status_message = st.session_state.get(cls.STATUS_MESSAGE_KEY, None)
        logger.debug("Received status message from session state: %s",
                     status_message
                     )
        if status_message is not None:
            msg_function, msg_text, msg_icon = status_message
            msg_function(msg_text, icon=msg_icon)
        else:
            st.info("This area will display status messages")

    @classmethod
    def clear_status_message(cls):
        """
        Clear the current status message from the session state.
        """
        if cls.STATUS_MESSAGE_KEY in st.session_state:
            logger.debug("Clearing status message from session state")
            del st.session_state[cls.STATUS_MESSAGE_KEY]
        else:
            logger.debug("No status message found in session state to clear")
