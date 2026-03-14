'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import standard libraries
from pathlib import Path

# Import 3rd party modules
import streamlit as st

# Import local modules
from utility import (get_client_ip,
                     get_memory_size,
                     get_logger
)
# initialize the logger
file_stem = Path(__file__).stem
logger_name = f"pages.{file_stem}"
logger = get_logger(logger_name)
# mark entry into the module
logger.debug("In module %s", logger_name)

st.write(f"Your client IP is: {get_client_ip()}")
st.write(f"Current Memory Size: {get_memory_size()} blocks")
st.write("Session State Contents:")
for key, item in st.session_state.items():
    st.write(f"{key} - {item}")
