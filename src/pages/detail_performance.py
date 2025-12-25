'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from collections import namedtuple

# Import 3rd party modules
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


# create a named tuple for summary data
Summary = namedtuple(
    "Summary",
    [
        #"Date",
        "Symbol",
        "Holding",
        "Realized",
        "Unrealized"
    ]
)
# global variables to hold the summary data
TRADE_SUMMARY = list()
TOTAL_REALIZED = 0.0
TOTAL_UNREALIZED = 0.0


# utility function to analyse trades for a single symbol
def _analyze_trades(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the current status of a trade using the trade data from the input Dataframe

    Arguments:
        trades_df -- input DataFrame containing trade data to be analyzed

    Returns:
        DataFrame with additional columns for analysis
    """
    # mark entry in log
    LOGGER.debug("in _analyze_trades: %s rows to analyze", trades_df.shape)

    # initialize variables
    total_shares = 0.0
    total_cost = 0.0
    market_value = 0.0
    realized_pl = 0.0
    symbol = trades_df.iloc[0].Symbol

    # loop through each row to compute analysis metrics
    for row in trades_df.itertuples():
        LOGGER.debug("analyzing row %s", row)
        # calculate the current quantity for each trade
        total_shares = total_shares + row.Quantity # type: ignore
        trades_df.loc[row.Index, "Holding"] = total_shares
        if total_shares == 0:
            # calculate the total realized profit/loss
            realized_pl = row.Amount - total_cost # type: ignore
            # If current holdings equal 0 the current market value and cost is also 0
            market_value = 0.0
            total_cost = 0.0
        else:
            # realized profit/loss is 0 if holdings are not zero
            realized_pl = 0.0
            # calculate the current market value
            # sign of market value is opposite of trade amount
            market_value = total_shares * row.Price # type: ignore
            # update the total cost
            total_cost = total_cost - row.Amount # type: ignore
        trades_df.loc[row.Index, "Cost"] = total_cost
        trades_df.loc[row.Index, "Realized P/L"] = realized_pl
        trades_df.loc[row.Index, "Market Value"] = market_value

    # update the summary data
    if total_shares != 0:
        # calculate the total unrealized profit/loss
        current_price = get_basic_quote(str(symbol)).get('currentPrice', 0)
    else:
        current_price = 0.0
    unrealized_pl = total_shares * current_price # type: ignore
    global TOTAL_REALIZED, TOTAL_UNREALIZED
    TOTAL_REALIZED += realized_pl
    TOTAL_UNREALIZED += unrealized_pl # type: ignore
    TRADE_SUMMARY.append(Summary(
                        Symbol=symbol,
                        Holding=total_shares,
                        Realized=realized_pl,
                        Unrealized=unrealized_pl,
                    ))

    return trades_df


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

    # add columns for analysis
    trades_df.insert(6, "Cost", 0.0)
    trades_df.insert(7, "Realized P/L", 0.0)
    trades_df.insert(8, "Holding", 0.0)
    trades_df.insert(8, "Market Value", 0.0)

    # group by symbol and analyze trades for each symbol
    indexed = trades_df
    analyzed = list()
    grouped = indexed.groupby("Symbol")
    for s in grouped:
        symbol = s[0]
        analyzed.append(_analyze_trades(grouped.get_group(symbol)))

    # concatenate the analyzed trades for each symbol and return
    return pd.concat(analyzed)


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

    trades = analyze_trades(selected_trades)

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

    # print out the summary information
    st.subheader("Trade Summary Data:")
    st.dataframe(TRADE_SUMMARY,
                 hide_index=True,
                 width=1000,
                 column_config={
                    "Symbol": st.column_config.TextColumn(width=150),
                    "Holding": st.column_config.NumberColumn(format="accounting", width="small"),
                    "Realized": st.column_config.NumberColumn(
                        label="Realized P/L",
                        format="$%.2f",
                    ),
                    "Unrealized": st.column_config.NumberColumn(
                        label="Unrealized P/L",
                        format="$%.2f",
                    ),
                 }
    )
    st.subheader(f"Total Realized Gain/Loss: ${TOTAL_REALIZED:,.2f}")
    st.subheader(f"Total Unrealized Gain/Loss: ${TOTAL_UNREALIZED:,.2f}")
