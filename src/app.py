'''
Main application file for the Portfolio Dashboard using Streamlit
'''
#standard library imports

#import 3rd-party libraries
import streamlit as st

#local application imports
from utility import get_logger, DATABASE_ENGINE

# mark entry into the module
logger = get_logger(__name__)
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
         st.Page("pages/performance_summary.py", title="Performance Summary"),
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
