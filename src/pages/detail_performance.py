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
from config import LOGGER, SYMBOL_MULTISELECT_KEY
from core import (get_security_symbols,
                  get_trades,
                  get_last_trade_date,
                  lookup_associated_symbols,
                  get_basic_quote,
                  get_security_info,
                  Periods,
)
from models.portfolio import SecurityType
from utility import aumc_get_instance


# create a named tuple for summary data
Summary = namedtuple(
    "Summary",
    [
        "Symbol",
        "Price",
        "Holding",
        "Market",
        "Cost",
        "Unrealized",
        "Realized",
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
    current_shares = 0.0
    current_price = 0.0
    market_value = 0.0
    total_cost = 0.0
    market_value = 0.0
    realized_pl = 0.0
    unrealized_pl = 0.0
    symbol = trades_df.iloc[0].Symbol
    security = get_security_info(symbol)

    # loop through each row to compute analysis metrics
    for row in trades_df.itertuples():
        LOGGER.debug("analyzing row %s", row)
        # calculate the total  cost and realized profit/loss
        if current_shares < 0: # type: ignore
            # is short position
            if row.Quantity > 0: # type: ignore
                # closing a short position
                realized_pl = row.Amount + (
                    total_cost * row.Quantity / current_shares  # type: ignore
                    )
                total_cost = total_cost * (
                    current_shares + row.Quantity  # type: ignore
                    ) / current_shares
            else:
                # adding to a short position
                total_cost -= row.Amount  # type: ignore
                # realized profit/loss is 0
                realized_pl = 0.0
        elif current_shares > 0: # type: ignore
            # is long position
            if row.Quantity < 0: # type: ignore
                # closing a long position
                realized_pl = row.Amount + (
                    total_cost * row.Quantity / current_shares  # type: ignore
                    )
                total_cost = total_cost * (
                    current_shares + row.Quantity  # type: ignore
                    ) / current_shares
            else:
                # adding to a long position
                total_cost -= row.Amount  # type: ignore
                # realized profit/loss is 0
                realized_pl = 0.0
        else:
            # new position
            realized_pl = 0.0
            total_cost = -row.Amount  # type: ignore
        # calculate the current quantity
        # NOTE: tracking number of optioncontracts for display
        current_shares += row.Quantity # type: ignore
        trades_df.loc[row.Index, "Holding"] = current_shares
        # get the stock prices as of the trade date if the trade price is 0
        if row.Price == 0.0:  # type: ignore
            current_price = get_basic_quote(str(symbol)).get('currentPrice', 0)
        else:
            # otherwise use the trade price
            current_price = row.Price  # type: ignore
        # calculate the current market value
        # multiply quantity by 100 for options
        if security.security_type == SecurityType.OPTION:
            market_value = current_shares * current_price * 100  # type: ignore
        else:
            market_value = current_shares * current_price  # type: ignore
        # calculate the unrealized profit/loss
        unrealized_pl = market_value - total_cost # type: ignore
        trades_df.loc[row.Index, "Cost"] = total_cost
        trades_df.loc[row.Index, "Realized P/L"] = realized_pl
        trades_df.loc[row.Index, "Market Value"] = market_value
        trades_df.loc[row.Index, "Unrealized P/L"] = unrealized_pl

    # update the summary data
    # if current holdings is not zero, calculate the market value andunrealized profit/loss
    # and unrealized profit/loss based on the current stock price
    # otherwise, unrealized profit/loss is zero
    if current_shares == 0:
        unrealized_pl = 0.0
        market_value = 0.0
        current_price = 0.0
    else:
        # get the current stock price
        current_price = get_basic_quote(str(symbol)).get('currentPrice', 0)
        # multiply quantity by 100 for options
        if security.security_type == SecurityType.OPTION:
            market_value = current_shares * current_price * 100  # type: ignore
            unrealized_pl = market_value - total_cost  # type: ignore
        else:
            market_value = current_shares * current_price  # type: ignore
            unrealized_pl = market_value - total_cost  # type: ignore
    # calculate the sum total of realized profit/loss
    realized_pl = trades_df["Realized P/L"].sum()

    global TOTAL_REALIZED, TOTAL_UNREALIZED
    TOTAL_REALIZED += realized_pl
    TOTAL_UNREALIZED += unrealized_pl # type: ignore
    TRADE_SUMMARY.append(Summary(
                        Symbol=symbol,
                        Price=current_price,
                        Holding=current_shares,
                        Market=market_value,
                        Cost=total_cost,
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
    trades_df.insert(6, "Holding", 0.0)
    trades_df.insert(7, "Market Value", 0.0)
    trades_df.insert(8, "Cost", 0.0)
    trades_df.insert(9, "Unrealized P/L", 0.0)
    trades_df.insert(10, "Realized P/L", 0.0)

    # group by symbol and analyze trades for each symbol
    indexed = trades_df
    analyzed = list()
    grouped = indexed.groupby("Symbol")
    for s in grouped:
        symbol = s[0]
        analyzed.append(_analyze_trades(grouped.get_group(symbol)))

    # concatenate the analyzed trades for each symbol and return
    return pd.concat(analyzed)


# main page logic
# retrieve or create the multiselect component for selecting symbols
multiselect_symbols = aumc_get_instance(SYMBOL_MULTISELECT_KEY)
if not multiselect_symbols.is_initialized:
    multiselect_symbols.configure_instance(
                        key=SYMBOL_MULTISELECT_KEY,
                        label="Select Symbol(s):",
                        options=get_security_symbols(include_options=False),
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
            #begin date, end date, and options button in the first row
            with st.container(horizontal=True,
                              horizontal_alignment="left",
                              vertical_alignment="bottom",
                              ):
                layout_selected_period = st.empty()
                #layout_end_date = st.empty()
                layout_load_options = st.empty()
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

with layout_load_options:
    # button to load options into the symbol list
    load_options = st.button("Load Options")

# create a multiselect widget to select symbols for performance analysis
with layout_select_symbols:
    # placeholder for multiselect symbols for performance analysis
    selected_symbols_placeholder = st.empty()
    # multiselect symbols for perormance analysis
    with selected_symbols_placeholder:
        multiselect_symbols.multiselect()


# get the selected symbols from the multiselect component
selected_symbols = multiselect_symbols.selected
if len(selected_symbols) > 0:
    if load_options:
        # add any associated symbols from the database to the selectiob list
        selected_symbols = lookup_associated_symbols(selected_symbols)
        # re-render the multiselect with updated selected symbols
        selected_symbols_placeholder.empty()
        with selected_symbols_placeholder:
            multiselect_symbols.multiselect(selected_symbols)

    # get the trades for the selected symbols and period
    selected_trades = get_trades(
        symbols=selected_symbols,
        period=selected_period,
        ascending=True,
    )

    # analyze the trades
    trades = analyze_trades(selected_trades)

    # display the trade details
    st.dataframe(trades,
                hide_index=True,
                width=1000,
                column_config={
                    "Symbol": st.column_config.TextColumn(width=150),
                    "Quantity": st.column_config.NumberColumn(format="accounting", width="small"),
                    "Price": st.column_config.NumberColumn(format="$%.2f",),
                    "Amount": st.column_config.NumberColumn(format="$%.2f"),
                    "Cost": st.column_config.NumberColumn(format="$%.2f"),
                    "Market Value": st.column_config.NumberColumn(format="$%.2f"),
                    "Unrealized P/L": st.column_config.NumberColumn(format="$%.2f"),
                    "Realized P/L": st.column_config.NumberColumn(format="$%.2f"),
                    }
                )

    # print out the summary information
    st.subheader("Trade Summary:")
    st.dataframe(TRADE_SUMMARY,
                hide_index=True,
                width=1000,
                column_config={
                    "Symbol": st.column_config.TextColumn(width=150),
                    "Price": st.column_config.NumberColumn(
                        label="Current Price",
                        format="$%.2f",
                    ),
                    "Holding": st.column_config.NumberColumn(format="accounting", width="small"),
                    "Market": st.column_config.NumberColumn(
                        label="Market Value",
                        format="$%.2f",
                    ),
                    "Cost": st.column_config.NumberColumn(format="$%.2f"),
                    "Unrealized": st.column_config.NumberColumn(
                        label="Unrealized P/L",
                        format="$%.2f",
                    ),
                    "Realized": st.column_config.NumberColumn(
                        label="Realized P/L",
                        format="$%.2f",
                    ),
                }
    )
    st.subheader(f"Total Realized Gain/Loss: ${TOTAL_REALIZED:,.2f}")
    st.subheader(f"Total Unrealized Gain/Loss: ${TOTAL_UNREALIZED:,.2f}")
