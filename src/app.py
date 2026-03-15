'''
Main application file for the Portfolio Dashboard using Streamlit
'''
#standard library imports

#import 3rd-party libraries
import streamlit as st

#local application imports
import __version__ as ver
from utility import get_logger, DATABASE_ENGINE, show_system_info

# mark entry into the module
logger = get_logger(__name__)
logger.debug("Starting Portfolio Dashboard application in module %s", __name__)

# use the stock bull icon
st.logo(image="images/Stock-Bull.png", size="large")

# create a page-like fragment to display system information on the page
sysinfo_page = st.Page(show_system_info, title="System Info", url_path="sysinfo")
sysinfo_nav = st.navigation(pages=[sysinfo_page], position="hidden")

# set the page configuration
st.set_page_config(
        layout="wide",
        page_icon="images/Stock-Bull.png",
        initial_sidebar_state="expanded",
)

# Build the navigation menu
pages = [
         st.Page("pages/performance_summary.py", title="Performance Summary"),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances"),
         st.Page("pages/detail_performance.py", title="Detail Performance"),
        ]
pg = st.navigation(pages,
                   position="top"
                   )

# display a development header
if ver.__environment__ == "DEV":
    st.header("*** DEVELOPMENT ***", text_alignment="center")

# Display the selected page
pg.run()

# Instantiate a Borg button at the bottom of the sidebar to display system information
with st.sidebar:
    sysinfo_button = st.button(label="", type="tertiary", icon=":material/borg:")
if sysinfo_button:
    #display the sysinfo page
    sysinfo_nav.run()

# Force the disposal of the database engine
DATABASE_ENGINE.dispose()
