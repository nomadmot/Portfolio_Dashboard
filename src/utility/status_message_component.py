import streamlit as st

class StatusMessageComponent:

    STATUS_MESSAGE_KEY = "status_message_component"

    @classmethod
    def set_status_message(
        cls,
        msg_function,
        msg_text,
        msg_icon
    ):
        """
        store the data needed to display the current status message
        into the session state for later retrieval and display.
        """
        st.session_state[cls.STATUS_MESSAGE_KEY] = (
                            msg_function,
                            msg_text,
                            msg_icon
        )

    @classmethod
    def display_status_message(cls, container):
        status_message = st.session_state.get(cls.STATUS_MESSAGE_KEY, None)
        if status_message is not None:
            msg_function, msg_text, msg_icon = status_message
            container.msg_function(msg_text, icon=msg_icon)
        else:
            container.info("This area will display status messages")
