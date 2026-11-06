'''
Generate a portfolio performance page based on selected symbols
and other criteria.
'''
# Import necessary libraries
from typing import NamedTuple
from pathlib import Path

# Import 3rd party modules
import streamlit as st
import polars as pl
from numpy import nan

# Import local modules
from core import (
                  get_accounts,
                  get_security_symbols,
                  get_traded_symbols,
                  get_trades,
                  get_last_trade_date,
                  lookup_associated_symbols,
                  )
from schemas.portfolio import SecurityType
from utility import (
                get_logger,
                get_aumc_instance,
                get_account_selection_component,
                get_time_machine_component,
                get_status_message_component,
                StatusType as stat,
                Periods,
                get_basic_quote,
                get_security_info,
                )

# initialize the logger
_logger_name = f"pages.{Path(__file__).stem}" # pylint: disable=invalid-name
_logger = get_logger(_logger_name)
# mark entry into the module
_logger.debug("In module %s", _logger_name)

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
_TRADE_SUMMARY = []

# the key for the detail performance multiselect and timemachine components
_ACCOUNT_SELECTION_KEY = "detail_performance_account_selection"
_PREVIOUS_ACCOUNTS_KEY = "detail_performance_previous_accounts"
_SYMBOL_MULTISELECT_KEY = "detail_performance_selected_symbols"
_TIME_MACHINE_KEY = "detail_performance_time_machine"

# utility function to analyse trades for a single symbol
def _analyze_trades(trades_df: pl.DataFrame) -> pl.DataFrame:
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
    _logger.debug("in _analyze_trades: %s rows to analyze", trades_df.shape)

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
    symbol = trades_df.item(0, "Symbol")
    security = get_security_info(symbol)

    # convert to a list of dicts once so the hot loop stays cheap
    rows = trades_df.to_dicts()
    n_rows = len(rows)

    # initialize analysis columns
    for col in ["Holding", "Avg Price", "Market Value", "Total Invested",
                "Basis", "Unrealized P/L", "Unrealized P/L %",
                "Realized P/L", "Realized P/L %"]:
        trades_df = trades_df.with_columns(pl.lit(0.0).alias(col))

    # loop through each row to compute analysis metrics
    for i, row in enumerate(rows):
        _logger.debug("analyzing row %s", row)

        # save previous values for transaction analysis
        prev_shares = current_shares
        prev_avg_price = average_price
        prev_cost_basis = prev_shares * prev_avg_price

        # use the trade price as the current price
        row_price: float = row["Price"] # type: ignore
        current_price = row_price

        # calculate the current holdings
        row_shares: float = row["Quantity"] # type: ignore
        current_shares += row_shares

        # get the transaction amount
        row_amount: float = row["Amount"] # type: ignore

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
        trades_df = trades_df.with_columns([
            pl.Series([v] * n_rows, dtype=pl.Float64).alias(col)
            for col, v in zip(
                ["Holding", "Basis", "Avg Price", "Market Value", "Total Invested",
                 "Unrealized P/L", "Unrealized P/L %", "Realized P/L", "Realized P/L %"],
                [current_shares, cost_basis, average_price, market_value,
                 total_invested, unrealized_pl, unrealized_pl_pct,
                 realized_pl, realized_pl_pct])
        ])

    # update the summary data
    # calculate the sum total of realized profit/loss for the summary
    realized_pl = float(trades_df["Realized P/L"].sum())
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

    _TRADE_SUMMARY.append(Summary(
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
def analyze_trades(trades_df: pl.DataFrame) -> pl.DataFrame:
    """
    Analyze the current status of a trade using the trade data from the input Dataframe
    Calls _analyze_trades for each symbol found

    Arguments:
        trades_df -- input DataFrame containing trade data to be analyzed

    Returns:
        DataFrame with additional columns for analysis
    """
    # mark entry in log
    _logger.debug("in analyze_trades: %s rows to analyze", trades_df.shape[0])

    # add columns for analysis
    for col in ["Holding", "Avg Price", "Market Value", "Total Invested",
                "Basis", "Unrealized P/L", "Unrealized P/L %",
                "Realized P/L", "Realized P/L %"]:
        trades_df = trades_df.with_columns(pl.lit(0.0).alias(col))

    # group by symbol and analyze trades for each symbol
    analyzed = []
    for symbol, group in trades_df.group_by("Symbol", maintain_order=True):
        analyzed.append(_analyze_trades(group))

    # concatenate the analyzed trades and return
    return pl.concat(analyzed)


### main page logic

# retrieve or create the multiselect component for selecting symbols
multiselect_symbols = get_aumc_instance(key=_SYMBOL_MULTISELECT_KEY,
                                        label="Select Symbol(s):",
                                        options=[],
                                        accept_new_options=True,
                                        placeholder="Select symbols...",
                                        )

# create a time machine component to select the time period for the analysis
time_machine = get_time_machine_component(_TIME_MACHINE_KEY, Periods.ALL)

# create the account selection component (multiple accounts may be selected)
accounts = get_accounts()
account_selector = get_account_selection_component(
                                        _ACCOUNT_SELECTION_KEY,
                                        label="Select Account(s):",
                                        options=accounts,
                                        allow_multiple=True,
                                        )

# create a StatusMessageComponent to display messages to the user
stat_message = get_status_message_component(f"status_{st.context.ip_address}")

# configure the page layout
st.set_page_config(layout="wide")

# add widgets for user inputs to sidebar
with st.sidebar:
    # render the account selection component
    account_selector.render()

    # render the time machine
    time_machine.render()

    # button to load options into the symbol list
    load_options = st.button("Load Options", width="stretch")

    # if the "symbol" query parameter is provided, pre-fill the multiselect
    query_symbols = st.query_params.get("symbol", None)
    query_symbols = query_symbols.upper().split(',') if query_symbols else None
    default_symbols = multiselect_symbols.selected
    if query_symbols:
        for query_symbol in query_symbols:
            default_symbols.append(query_symbol)

    # render the multiselect component for selecting symbols
    multiselect_symbols.render(default_symbols)

# get the selected account(s) from the account selection component
selected_accounts: list|None  = account_selector.selected
if selected_accounts is None or len(selected_accounts) == 0:
    # the user needs to select an account
    stat_message.set_status_message(stat.INFO, "Please select at least one account")
    # display status messages
    stat_message.show_status_messages()
    st.stop()

# page header
account_names = ", ".join(
    a.account_name for a in accounts if a.account_id in selected_accounts
)
st.title(f"Detail Performance Analysis for {account_names}")
st.markdown(f"*Last Trade Date on file: {get_last_trade_date():%Y-%m-%d}*",)

# get the currently selected symbols from the multiselect component
selected_symbols = multiselect_symbols.selected

# before we move on, update the symbols multiselect component
# for the next iteration
# the symbols offered for selection are those with transactions
# in the selected accounts
available_symbols = get_traded_symbols(selected_accounts, include_options=False)
previous_accounts = st.session_state.get(_PREVIOUS_ACCOUNTS_KEY)
if previous_accounts is None:
    # first run for this session; initialize the symbol options
    multiselect_symbols.set_options(available_symbols)
elif sorted(previous_accounts) != sorted(selected_accounts):
    # the account selection changed; refresh the symbol options
    multiselect_symbols.set_options(available_symbols)
st.session_state[_PREVIOUS_ACCOUNTS_KEY] = list(selected_accounts)

if load_options:
    # add any associated symbols from the database to the selection list
    selected_symbols = lookup_associated_symbols(selected_symbols)
    # re-render the multiselect with updated selected symbols
    multiselect_symbols.update_options(selected_symbols)

    stat_message.set_status_message(stat.INFO, "Options loaded")

# now back to our regularly scheduled program
if len(selected_symbols) == 0:
    # the user needs to select a symbol
    stat_message.set_status_message(stat.INFO, "Please select at least one symbol")
    # display status messages
    stat_message.show_status_messages()
    st.stop()

# get the trades for the selected accounts, symbols, and period
selected_trades = get_trades(
    symbols=selected_symbols,
    account_ids=selected_accounts,
    begin_date=time_machine.begin_date,
    end_date=time_machine.end_date,
    ascending=True,
)

# analyze the trades
if not selected_trades.empty:
    trades = analyze_trades(selected_trades)
else:
    stat_message.set_status_message(stat.WARNING, "No trades found")
    trades = pl.DataFrame()

# update the time machine with the dates found in the response
if not trades.is_empty():
    df_begin_date = trades["Date"].min().date()
    df_end_date = trades["Date"].max().date()
    time_machine.update_date_pickers(df_begin_date, df_end_date)

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
st.dataframe(_TRADE_SUMMARY,
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
if len(_TRADE_SUMMARY) > 0:
    df_trade_summary = pl.DataFrame(_TRADE_SUMMARY)
    grand_total_invested = float(df_trade_summary["Invested"].sum())
    grand_total_basis = float(df_trade_summary["Basis"].sum())
    grand_total_market = float(df_trade_summary["Market"].sum())
    grand_total_realized = float(df_trade_summary["Realized"].sum())
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

# display any status messages
stat_message.show_status_messages()
