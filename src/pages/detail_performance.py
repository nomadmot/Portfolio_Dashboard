'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from datetime import date
import streamlit as st
import pandas as pd

# Import local modules
from core import get_security_symbols, get_trades


# configure the page layout
st.set_page_config(layout="wide")

# page subheader
st.subheader("Detail Performance Analysis")

include_options = st.checkbox("Include Options")
symbols = st.multiselect(
    "Select Symbol(s):",
    label_visibility="collapsed",
    placeholder="Select Symbol(s)",
    options=get_security_symbols(include_options=include_options),
    )

if symbols:
    trades = get_trades(symbols=symbols)
    st.table(trades)
