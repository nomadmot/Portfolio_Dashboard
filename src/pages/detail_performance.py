'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
import streamlit as st

# Import local modules
from core import (get_security_symbols,
                  get_trades,
                  get_last_trade_date,
                  lookup_associated_symbols,
                  Periods
                  )


# configure the page layout
st.set_page_config(layout="wide")

# page subheader
st.subheader("Detail Performance Analysis")
st.markdown(f"*Last Trade Date on file: {get_last_trade_date():%Y-%m-%d}*",)

# set page content layout
with st.container(width="stretch"):
    # we'll use only the first column for inputs
    layout_inputs = st.columns([0.3, 0.7])[0]
    with layout_inputs:
        # container for input elements
        with st.container(border=True):
            #begin date, end date, and options checkbox in the first row
            with st.container(horizontal=True):
                layout_selected_period = st.empty()
                #layout_end_date = st.empty()
                layout_include_options = st.empty()
            # include symbol multiselect in the second row
            with st.container(horizontal=True):
                layout_select_symbols = st.empty()

# collect user inputs
with layout_selected_period:
    # create a selectbox to select the number of days for the chart
    selected_period = st.selectbox(
                            "Select Period:",
                            Periods.get_periods(),
                            format_func=Periods.get_label,
                            index=1,
                            width=300)

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

    selected_trades = get_trades(
        symbols=selected_symbols,
        period=selected_period,
        ascending=True,
    )

    st.dataframe(selected_trades,
                 hide_index=True,
                 width=800,
                 column_config={
                     "Quantity": st.column_config.NumberColumn(format="accounting", width="small"),
                     "Price": st.column_config.NumberColumn(format="dollar"),
                     "Amount": st.column_config.NumberColumn(format="dollar")
                    }
                 )
    st.subheader(f"Total Gain/Loss: ${selected_trades['Amount'].sum():,.2f}")
