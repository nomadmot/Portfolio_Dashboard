'''
Main application file for the Portfolio Dashboard using Streamlit
'''
#standard library imports
import logging

#import 3rd-party libraries
import streamlit as st

#local application imports
from config import SETTINGS, DATABASE_ENGINE
from utility import StatusMessageComponent

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())
# mark entry into the module
logger.debug("Starting Portfolio Dashboard application in module %s", __name__)

# use the stock bull icon
st.logo(image="images/Stock-Bull.png", size="large")

# set the page configuration
st.set_page_config(
        layout="wide",
        page_icon="images/Stock-Bull.png",
        initial_sidebar_state="expanded",
)
# Build the navigation menu
pages = [
         st.Page("pages/performance_summary.py", title="Performance Summary", default=True),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances"),
         st.Page("pages/detail_performance.py", title="Detail Performance"),
         st.Page("pages/system_info.py", title="System Info"),
        ]
pg = st.navigation(pages,
                   position="top"
                   )

# Display the selected page
pg.run()
# Force the disposal of the database engine
DATABASE_ENGINE.dispose()

# Clear out any status messages left in the session state
StatusMessageComponent.clear_status_message()
