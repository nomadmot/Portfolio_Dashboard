'''
Main application file for the Portfolio Dashboard using Streamlit
'''
#standard library imports
import logging

#import 3rd-party libraries
import streamlit as st

#local application imports
import config
from utility import StatusMessageComponent

# Initialize logging
#logger = logging.getLogger(st.__name__)
logger = config.LOGGER
#logger.setLevel(config.LOGLEVEL_STREAMLIT)
# mark entry into the module
logger.debug("Starting Portfolio Dashboard application")
# set the sqlalchemy logging level
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(config.LOGLEVEL_SQLALCHEMY)

# use the stock bull icon
st.logo(image="images/Stock-Bull.png",)
# Build the navigation menu
pages = [
         st.Page("pages/daily_performance.py", title="Daily Performance"),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances"),
         st.Page("pages/detail_performance.py", title="Detail Performance"),
        ]
pg = st.navigation(pages,
                   position="top"
                   )

# Display the selected page
pg.run()

# Clear out any status messages left in the session state
StatusMessageComponent.clear_status_message()
