'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from typing import NamedTuple
import logging

# Import 3rd party modules
import streamlit as st
import pandas as pd
from numpy import nan

# Import local modules
from config import SETTINGS
from core import (get_security_symbols,
                  get_trades,
                  get_last_trade_date,
                  lookup_associated_symbols,
                  get_basic_quote,
                  get_security_info,
)
from models.portfolio import SecurityType
from utility import aumc_get_instance, get_time_machine_component

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())

# create a named tuple for summary data
class Summary(NamedTuple):
    """
    Create a NamedTuple class to contain summary and total information for trades

    Arguments:
        NamedTuple -- derived class
    """
    Symbol: str
    Invested: float
    Realized: float
    RealizedPct: float
    Holding: float
    Price: float
    Market: float
    Basis: float
    Unrealized: float
    UnrealizedPct: float

# global variables to hold the summary data
TRADE_SUMMARY = list()

# the key for the detail performance multiselect component
SYMBOL_MULTISELECT_KEY = "detail_performance_selected_symbols"

# utility function to analyse trades for a single symbol
def _analyze_trades(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the current status of a trade using the trade data from the input Dataframe
    Expects only one symbol... function analyze_trades groups tha dataframe and calls
    thsi function for each group

    Arguments:
        trades_df -- input DataFrame containing trade data to be analyzed

    Returns:
        DataFrame with additional columns for analysis
    """
    # mark entry in log
    logger.debug("in _analyze_trades: %s rows to analyze", trades_df.shape)

    # initialize variables
    current_shares: float = 0.0
    current_price: float = 0.0
    average_price: float = 0.0
    market_value: float = 0.0
    total_invested: float = 0.0
    cost_basis: float = 0.0
    market_value: float = 0.0
    realized_pl: float = 0.0
    realized_pl_pct: float = 0.0
    unrealized_pl: float = 0.0
    unrealized_pl_pct: float = 0.0
    prev_shares: float = 0.0
    prev_avg_price: float = 0.0
    prev_cost_basis: float = 0.0
    symbol = trades_df.iloc[0].Symbol
    security = get_security_info(symbol)

    # loop through each row to compute analysis metrics
    for row in trades_df.itertuples():
        logger.debug("analyzing row %s", row)

        # save previous values for transaction analysis
        prev_shares = current_shares
        prev_avg_price = average_price
        prev_cost_basis = prev_shares * prev_avg_price

        # use the trade price as the current price
        row_price: float = row.Price # type: ignore
        current_price = row_price

        # calculate the current holdings
        row_shares: float = row.Quantity # type: ignore
        current_shares += row_shares

        # get the transaction amount
        row_amount: float = row.Amount # type: ignore

        # calculate the total cost and realized profit/loss
        if prev_shares < 0:
            # is short position
            if row_shares > 0:
                # covering a short position
                cost_basis = cost_basis * (
                                current_shares / prev_shares
                                )
                # calculate realized profit/loss
                realized_pl = row_amount + prev_cost_basis - cost_basis
                realized_pl_pct = \
                    realized_pl / (prev_cost_basis - cost_basis)
            else:
                # adding to a short position
                total_invested -= row_amount
                cost_basis += row_amount
                # realized profit/loss is meaningless
                realized_pl = nan
                realized_pl_pct = nan
        elif prev_shares > 0:
            # is long position
            if row_shares < 0:
                # sale of shares
                cost_basis = cost_basis * (
                                current_shares / prev_shares
                                )
                # calculate realized profit/loss
                cost_of_shares = -row_shares * prev_avg_price
                realized_pl = row_amount - cost_of_shares
                realized_pl_pct = \
                    realized_pl / cost_of_shares if cost_of_shares != 0 else nan
            else:
                # adding to a long position
                total_invested -= row_amount
                cost_basis -= row_amount
                # realized profit/loss is meaningless
                realized_pl = nan
                realized_pl_pct = nan
        else:
            # new position
            if current_shares > 0.0:
                # is new long position
                total_invested -= row_amount
                cost_basis = -row_amount
            else:
                # is new short position
                total_invested = -row_amount
                cost_basis = row_amount
            # realized profit/loss is meaningless for a new position
            realized_pl = nan
            realized_pl_pct = nan

        # calculate the average price
        average_price = \
            cost_basis / current_shares if current_shares != 0 else nan

        # calculate the current market value
        market_value = current_shares * current_price
        # multiply value by 100 for options
        if security.security_type == SecurityType.OPTION:
            market_value = market_value * 100

        # calculate the unrealized profit/loss and percent
        if current_shares > 0.0:
            # use previous cost basis for long position percent
            unrealized_pl = market_value - cost_basis
            unrealized_pl_pct = \
                unrealized_pl / prev_cost_basis if prev_cost_basis > 0.0 else nan
        elif current_shares < 0.0:
            # use current cost basis for short position percent
            unrealized_pl = market_value + cost_basis
            unrealized_pl_pct = \
                unrealized_pl / cost_basis if cost_basis > 0.0 else nan
        else:
            unrealized_pl = nan
            unrealized_pl_pct = nan

        # update the detail dataframe with results of the analysis
        trades_df.loc[row.Index, "Holding"] = current_shares
        trades_df.loc[row.Index, "Basis"] = cost_basis
        trades_df.loc[row.Index, "Avg Price"] = average_price
        trades_df.loc[row.Index, "Market Value"] = market_value
        trades_df.loc[row.Index, "Total Invested"] = total_invested
        trades_df.loc[row.Index, "Unrealized P/L"] = unrealized_pl
        trades_df.loc[row.Index, "Unrealized P/L %"] = unrealized_pl_pct
        trades_df.loc[row.Index, "Realized P/L"] = realized_pl
        trades_df.loc[row.Index, "Realized P/L %"] = realized_pl_pct

    # update the summary data
    # calculate the sum total of realized profit/loss for the summary
    realized_pl = trades_df["Realized P/L"].sum()
    # calculate the realized p/l percent for the summary
    if total_invested > 0.0:
        # is long position
        realized_pl_pct = realized_pl / (total_invested - cost_basis)
    elif total_invested < 0.0:
        # is short position
        realized_pl_pct = -realized_pl / (total_invested + cost_basis)
    else:
        realized_pl_pct = nan
    # calculate amounts for current holdings
    if current_shares != 0.0:
        # get the current price
        current_price = \
            get_basic_quote(str(symbol)).get('currentPrice', nan)
        # calculate the current market value for the summary
        market_value = current_shares * current_price
        if current_shares > 0.0:
            # is long position
            # calculate the unrealized p/l for the summary
            unrealized_pl = market_value - cost_basis
            # calculate the unrealized p/l for the summary
            unrealized_pl_pct = unrealized_pl / cost_basis
        else:
            # is short position
            # calculate the unrealized p/l for the summary
            unrealized_pl = market_value + cost_basis
            # calculate the unrealized p/l for the summary
            unrealized_pl_pct = unrealized_pl / cost_basis
    else:
        current_price = nan
        market_value = nan
        unrealized_pl = nan
        unrealized_pl_pct = nan

    TRADE_SUMMARY.append(Summary(
                Symbol=symbol,
                Invested=total_invested,
                Realized=realized_pl,
                RealizedPct=realized_pl_pct,
                Holding=current_shares,
                Price=current_price,
                Market=market_value,
                Basis=cost_basis,
                Unrealized=unrealized_pl,
                UnrealizedPct=unrealized_pl_pct,
                ))

    return trades_df


# function to analyze trades
def analyze_trades(trades_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze the current status of a trade using the trade data from the input Dataframe
    Calls _analyze_trades for each symbol found

    Arguments:
        trades_df -- input DataFrame containing trade data to be analyzed

    Returns:
        DataFrame with additional columns for analysis
    """
    # mark entry in log
    logger.debug("in analyze_trades: %s rows to analyze", trades_df.shape[0])

    # add columns for analysis
    trades_df.insert(6, "Holding", 0.0)
    trades_df.insert(7, "Avg Price", 0.0)
    trades_df.insert(8, "Market Value", 0.0)
    trades_df.insert(9, "Total Invested", 0.0)
    trades_df.insert(10, "Basis", 0.0)
    trades_df.insert(11, "Unrealized P/L", 0.0)
    trades_df.insert(12, "Unrealized P/L %", 0.0)
    trades_df.insert(13, "Realized P/L", 0.0)
    trades_df.insert(14, "Realized P/L %", 0.0)

    # group by symbol and analyze trades for each symbol
    indexed = trades_df
    analyzed = list()
    grouped = indexed.groupby("Symbol")
    for s in grouped:
        symbol = s[0]
        analyzed.append(_analyze_trades(grouped.get_group(symbol)))

    # concatenate the analyzed trades and return
    return pd.concat(analyzed)


### main page logic

# retrieve or create the multiselect component for selecting symbols
multiselect_symbols = aumc_get_instance(SYMBOL_MULTISELECT_KEY)
if not multiselect_symbols.is_initialized:
    multiselect_symbols.configure_instance(
                        key=SYMBOL_MULTISELECT_KEY,
                        label="Select Symbol(s):",
                        options=get_security_symbols(include_options=False),
                        accept_new_options=False,
                        placeholder="Select or type to add symbols...",
                        )

# configure the page layout
st.set_page_config(layout="wide")

# page header
st.title("Detail Performance Analysis")
st.markdown(f"*Last Trade Date on file: {get_last_trade_date():%Y-%m-%d}*",)

# add widgets for user inputs to sidebar
with st.sidebar:
    # create a selectbox to select the number of days for the chart
    selected_period = get_time_machine_component("detail_performance_time_machine")
    selected_period.render()

    # button to load options into the symbol list
    load_options = st.button("Load Options", width="stretch")

    # placeholder for multiselect symbols for performance analysis
    selected_symbols_placeholder = st.empty()
    # multiselect symbols for perormance analysis
    # if the "symbol" query parameter is provided, pre-fill the multiselect
    query_symbol = st.query_params.get("symbol", None)
    with selected_symbols_placeholder:
        multiselect_symbols.multiselect(query_symbol.upper().split(',') if query_symbol else None)


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
        period=selected_period.period_selected,
        ascending=True,
    )

    # analyze the trades
    if not selected_trades.empty:
        trades = analyze_trades(selected_trades)
    else:
        trades = pd.DataFrame()

    # display the trade details
    st.dataframe(trades,
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn(width=150),
                    "Quantity": st.column_config.NumberColumn(format="accounting", width="small"),
                    "Price": st.column_config.NumberColumn(format="$%.2f",),
                    "Amount": st.column_config.NumberColumn(format="$%.2f"),
                    "Holding": st.column_config.NumberColumn(format="accounting"),
                    "Avg Price": st.column_config.NumberColumn(format="$%.2f",),
                    "Market Value": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Invested": st.column_config.NumberColumn(format="$%.2f"),
                    "Basis": st.column_config.NumberColumn(format="$%.2f"),
                    "Unrealized P/L": st.column_config.NumberColumn(format="$%.2f"),
                    "Unrealized P/L %": st.column_config.NumberColumn(format="percent"),
                    "Realized P/L": st.column_config.NumberColumn(format="$%.2f"),
                    "Realized P/L %": st.column_config.NumberColumn(format="percent"),
                    }
                )

    # print out the summary information
    st.subheader("Trade Summary:")
    st.dataframe(TRADE_SUMMARY,
                hide_index=True,
                column_config={
                    "Symbol": st.column_config.TextColumn(width=150),
                    "Invested": st.column_config.NumberColumn(
                        label="Total Invested",
                        format="$%.2f",
                    ),
                    "Realized": st.column_config.NumberColumn(
                        label="Realized P/L",
                        format="$%.2f",
                    ),
                    "RealizedPct": st.column_config.NumberColumn(
                        label="Realized P/L %",
                        format="percent",
                    ),
                    "Holding": st.column_config.NumberColumn(format="accounting", width="small"),
                    "Price": st.column_config.NumberColumn(
                        label="Current Price",
                        format="$%.2f",
                    ),
                    "Market": st.column_config.NumberColumn(
                        label="Market Value",
                        format="$%.2f",
                    ),
                    "Basis": st.column_config.NumberColumn(
                        label="Cost Basis",
                        format="$%.2f",
                    ),
                    "Unrealized": st.column_config.NumberColumn(
                        label="Unrealized P/L",
                        format="$%.2f",
                    ),
                    "UnrealizedPct": st.column_config.NumberColumn(
                        label="Unrealized P/L %",
                        format="percent",
                    ),
                }
    )

    # calculate the grand totals
    if len(TRADE_SUMMARY) > 0:
        df_trade_summary = pd.DataFrame(TRADE_SUMMARY)
        grand_total_invested = df_trade_summary["Invested"].sum()
        grand_total_basis = df_trade_summary["Basis"].sum()
        grand_total_market = df_trade_summary["Market"].sum()
        grand_total_realized = df_trade_summary["Realized"].sum()
        grand_total_unrealized = grand_total_market - grand_total_basis
        total_realized_pct = grand_total_realized / (grand_total_invested - grand_total_basis)
        total_unrealized_pct = \
            grand_total_unrealized / grand_total_basis if grand_total_basis != 0.0 else nan
        st.subheader(f"Total Invested: ${grand_total_invested:,.2f}")
        st.subheader("Total Realized Profit/Loss: $" +
                    f"{grand_total_realized:,.2f} ({total_realized_pct:.1%})")
        st.subheader(f"Total Current Market: ${grand_total_market:,.2f}")
        st.subheader(f"Total Current Basis: ${grand_total_basis:,.2f}")
        st.subheader("Total Unrealized Profit/Loss: $" +
                    f"{grand_total_unrealized:,.2f} ({total_unrealized_pct:.1%})")
