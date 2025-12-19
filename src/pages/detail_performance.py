'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
import streamlit as st
import pandas as pd

# Import local modules
from config import LOGGER
from core import (get_security_symbols,
                  get_trades,
                  get_last_trade_date,
                  lookup_associated_symbols,
                  get_basic_quote,
                  Periods
                  )

# function to analyze trades
def analyze_trades(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the current status of a trade using the trade data from the input Dataframe

    Arguments:
        trades_df -- input DataFrame containing trade data to be analyzed

    Returns:
        DataFrame with additional columns for analysis
    """
    # mark entry in log
    LOGGER.debug("in analyze_trades: %s rows to analyze", trades_df.shape[0])

    # initialize variables
    total_shares = 0.0
    total_cost = 0.0
    market_value = 0.0

    # add columns for analysis
    trades_df.insert(6, "Cost", 0.0)
    trades_df.insert(7, "Realized P/L", 0.0)

    # loop through each row to compute analysis metrics
    for index in range(trades_df.shape[0]):
        row = trades_df.iloc[index]
        LOGGER.debug("analyzing row %s: %s", index, row.to_dict())
        # calculate the current quantity for each trade
        total_shares = total_shares + row["Quantity"]
        trades_df.at[index, "Holding"] = total_shares
        if total_shares == 0:
            # calculate the total realized profit/loss
            realized_pl = row["Amount"] - total_cost
            # If current holdings equal 0 the current market value and cost is also 0
            market_value = 0.0
            total_cost = 0.0
        else:
            # realized profit/loss is 0 if holdings are not zero
            realized_pl = 0.0
            # calculate the current market value
            # sign of market value is opposite of trade amount
            market_value = total_shares * row["Price"]
            # update the total cost
            total_cost = total_cost - row["Amount"]
        trades_df.at[index, "Cost"] = total_cost
        trades_df.at[index, "Realized P/L"] = realized_pl
        trades_df.at[index, "Market Value"] = market_value

    return trades_df


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

    trades = analyze_trades(selected_trades.copy())

    st.dataframe(trades,
                 hide_index=True,
                 width=1000,
                 column_config={
                     "Symbol": st.column_config.TextColumn(width=150),
                     "Quantity": st.column_config.NumberColumn(format="accounting", width="small"),
                     "Price": st.column_config.NumberColumn(format="$%.2f",),
                     "Amount": st.column_config.NumberColumn(format="$%.2f"),
                     "Market Value": st.column_config.NumberColumn(format="$%.2f"),
                     "Realized P/L": st.column_config.NumberColumn(format="$%.2f"),
                    }
                 )
    if trades.empty:
        CURRENT_HOLDINGS = 0
        CURRENT_PRICE = 0
        CURRENT_VALUE = 0
    else:
        CURRENT_HOLDINGS = trades['Holding'].iloc[-1]
        CURRENT_PRICE = get_basic_quote(trades['Symbol'].iloc[-1]).get('currentPrice', 0)
        CURRENT_VALUE = CURRENT_PRICE * CURRENT_HOLDINGS
    st.subheader(
        f"Currently holding {CURRENT_HOLDINGS:.0f} "
        f"shares @ ${CURRENT_PRICE:,.2f} per share"
    )
    st.subheader(f"Current Market Value: {CURRENT_VALUE:,.2f}")
    st.subheader(f"Realized Gain/Loss: ${trades["Realized P/L"].sum():,.2f}")
