'''
Main application file for the Portfolio Dashboard using Streamlit
'''
#standard library imports

#import 3rd-party libraries
import streamlit as st

#local application imports
import __version__ as ver
from utility import get_logger, show_system_info, get_status_message_component

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("Starting Portfolio Dashboard application in module %s", __name__)

# adjust UI for environment
if ver.__environment__ == "DEV":
    st.set_option("client.showErrorDetails", "full")
    st.set_option("client.toolbarMode", "developer")
else:
    st.set_option("client.showErrorDetails", "type")
    st.set_option("client.toolbarMode", "viewer")

# use the stock bull icon
st.logo(image="images/Stock-Bull.png", size="large")

# create a page-like fragment to display system information on the page
sysinfo_page = st.Page(show_system_info, title="System Info", url_path="sysinfo")
sysinfo_nav = st.navigation(pages=[sysinfo_page], position="hidden")

# set the page configuration
st.set_page_config(
        layout="wide",
        page_icon="images/Stock-Bull.png",
        initial_sidebar_state="expanded",)

# Build the navigation menu
pages = [
         st.Page("pages/performance_summary.py", title="Performance Summary", url_path="performance_summary"),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances", url_path="manage_balances"),
         st.Page("pages/detail_performance.py", title="Detail Performance", url_path="detail_performance"),
        ]
pg = st.navigation(pages,
                   position="top")

# Initialize status message component based on the current page's url_path
status_component_key = f"status_{st.context.ip_address}"
status_component = get_status_message_component(status_component_key)

# add a development header
if ver.__environment__ == "DEV":
    st.header("*** DEVELOPMENT ***", text_alignment="center")

# Display the selected page
pg.run()

# Instantiate a Borg button at the bottom of the sidebar to display system information
with st.sidebar:
    sysinfo_button = st.button(label="",
                               type="tertiary",
                               icon=":material/borg:",
                               help="Geek out")
if sysinfo_button:
    #display the sysinfo page
    sysinfo_nav.run()

# Display any collected status messages
status_component.show_status_messages()
