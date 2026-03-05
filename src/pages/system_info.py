'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import standard libraries

# Import 3rd party modules
import streamlit as st

# Import local modules
from utility import (get_client_ip,
                     get_memory_size,
                     get_logger
)
# mark entry into the module
logger = get_logger(__name__)
logger.debug("In module %s", __name__)

st.write(f"Your client IP is: {get_client_ip()}")
st.write(f"Current Memory Size: {get_memory_size()} blocks")
st.write("Session State Contents:")
for key, item in st.session_state.items():
    st.write(f"{key} - {item}")
