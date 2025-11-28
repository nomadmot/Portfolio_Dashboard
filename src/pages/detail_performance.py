'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from datetime import date
import streamlit as st
import pandas as pd

# Import local modules
from core import get_security_symbols, get_trades, lookup_associated_symbols

def filter_trades(symbols, trades, begin_date, end_date):
    """Filter trades based on selected symbols and date range."""
    filtered_trades = trades[
        ((trades["Symbol"].isin(symbols)) &
        (trades["Date"] >= pd.to_datetime(begin_date).date()) &
        (trades["Date"] <= pd.to_datetime(end_date).date())
        )]
    return filtered_trades

# configure the page layout
st.set_page_config(layout="wide")

# page subheader
st.subheader("Detail Performance Analysis")

# set page content layout
with st.container(width="stretch"):
    # we'll use only the first column for inputs
    layout_inputs = st.columns([0.3, 0.7])[0]
    with layout_inputs:
        # container for input elements
        with st.container(border=True):
            #begin date, end date, and options checkbox in the first row
            with st.container(horizontal=True):
                layout_begin_date = st.empty()
                layout_end_date = st.empty()
                layout_include_options = st.empty()
            # include symbol multiselect in the second row
            with st.container(horizontal=True):
                layout_select_symbols = st.empty()

# collect user inputs
# begin and end dates for the performance analysis
with layout_begin_date:
    selected_begin_date = st.date_input(
        "Begin Date:",
        value=date(date.today().year, 1, 1),
        label_visibility="collapsed",
    )
with layout_end_date:
    selected_end_date = st.date_input(
        "End Date:",
        value=date.today(),
        label_visibility="collapsed",
    )

with layout_include_options:
    # option to include options in the symbol list
    include_options = st.checkbox("Include Options")

with layout_select_symbols:
    # multiselect symbols for perormance analysis
    selected_symbols = st.multiselect(
        "Select Symbol(s):",
        label_visibility="collapsed",
        placeholder="Select Symbol(s)",
        options=get_security_symbols(include_options=False),
        )

if selected_symbols:
    if include_options:
        selected_symbols = lookup_associated_symbols(selected_symbols)
    selected_trades = filter_trades(
        selected_symbols,
        get_trades(symbols=selected_symbols),
        selected_begin_date,
        selected_end_date,
    )

    st.dataframe(selected_trades,
                 hide_index=True,
                 use_container_width=False,
                 column_config={
                     "Price": st.column_config.NumberColumn(format="dollar"),
                     "Amount": st.column_config.NumberColumn(format="dollar")
                    }
                 )
    st.subheader(f"Total Gain/Loss: ${selected_trades['Amount'].sum():,.2f}")
