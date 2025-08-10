import streamlit as st

# Header elements for the app
st.title("Portfolio Dashboard")

# Build the navigation menu
pages = [
         st.Page("pages/daily_performance.py", title="Daily Performance"),
         st.Page("pages/manage_balances.py", title="Manage Daily Balances"),
        ]
pg = st.navigation(pages, position="top")

# Display the selected page
pg.run()
