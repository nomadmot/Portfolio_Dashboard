import streamlit as st
import streamlit.logger
import config

# Initialize logging
logger = streamlit.logger.get_logger(st.__name__)
logger.setLevel(config.LOGLEVEL_STREAMLIT)
# mark entry into the module
logger.debug("Starting Portfolio Dashboard application")
# set the sqlalchemy logging level
sqlalchemy_logger = streamlit.logger.get_logger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(config.LOGLEVEL_SQLALCHEMY)

# use the stock bull icon
st.logo(image="images/Stock-Bull.png",)
# Build the navigation menu
pages = [
         st.Page("pages/daily_performance.py", title="Daily Performance"),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances"),
        ]
pg = st.navigation(pages,
                   position="top"
                   )

# Display the selected page
pg.run()
