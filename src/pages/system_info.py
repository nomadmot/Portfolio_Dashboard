'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
import logging

# Import 3rd party modules
import streamlit as st

# Import local modules
from config import ENVIRONMENT
from utility import get_client_ip, get_memory_size


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(ENVIRONMENT.loglevel_application.to_logging_level())
# Mark entry into page'
logger.debug("entering module: %s", __name__)

st.write(f"Your client IP is: {get_client_ip()}")
st.write(f"Current Memory Size: {get_memory_size()} blocks")
st.write("Session State Contents:")
for key, item in st.session_state.items():
    st.write(f"{key} - {item}")
