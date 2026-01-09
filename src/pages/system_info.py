'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
import logging

# Import 3rd party modules
import streamlit as st

# Import local modules
import config
from utility import get_client_ip

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(config.LOGLEVEL_APPLICATION)
# Mark entry into page'
logger.debug("entering module: %s", __name__)

st.write(f"Your client IP is: {get_client_ip()}")
