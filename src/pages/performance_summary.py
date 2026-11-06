"""
Plot the daily performance of the specified account compared to a selected stock ticker.
"""
# Import standard libraries
from typing import List
from datetime import date, datetime
from pathlib import Path

# Import 3rd party libraries
import streamlit as st
import numpy as np
import polars as pl
import plotly.graph_objects as go

# Import local modules
from config import SETTINGS
from utility import (
    get_time_machine_component,
    get_status_message_component,
    get_account_selection_component,
    get_logger,
    Periods,
    get_period,
    StatusType as stat,
    get_stock_history,
)
from core import (
    get_account,
    get_accounts,
    get_balance_history,
    get_cash_flows,
    get_first_balance_date,
    get_last_balance_date,
)
from core.performance import (
    simple_daily,
    simple_cumulative,
    twr_daily,
    twr_cumulative,
    mwr_cumulative,
)
from schemas import CalculationMethod, TradeType

# initialize the logger
_logger_name = f"pages.{Path(__file__).stem}"
_logger = get_logger(_logger_name)
# mark entry into the module
_logger.debug("In module %s", _logger_name)

# set local constants
_ACCOUNT_SELECTION_KEY = "performance_summary_account_selection"
_TIME_MACHINE_COMPONENT_KEY = "summary-performance-time-machine"
_METHOD_KEY = "summary-performance-method"
_INCLUDE_DIV_INT_KEY = "summary-performance-include-div-int"
_INCLUDE_FEES_TAX_KEY = "summary-performance-include-fees-tax"

# Account comparison options are visually distinguished from ticker symbols by a
# leading em-dash + space; the option-building / resolution helpers live in
# utility.comparison_options so they can be unit-tested without importing the page.
from utility import (
    EMP_DASH,
    COMPARISON_PREFIX,
    disambiguated_name,
    comparison_options,
    is_account_option,
    account_name_from_option,
    account_id_for_option,
)

# the ticker symbols configured for comparison (accounts are appended at runtime)
_COMPARISON_SYMBOLS: List[str] = list(SETTINGS.defaults.performance_summary_symbols)


def _dispatch_method(balance_series: pl.DataFrame,
                     cash_flow_series: pl.DataFrame,
                     method: str) -> tuple[List[float], List[float]]:
    """
    Compute the cumulative and daily percent change for a balance series using
    the given calculation method (and net external cash flows). The MWR method
    reports the plain day-over-day change for its "daily" figure, matching the
    page's existing behaviour.

    :param balance_series: A ``["date", "value"]`` frame of end-of-period values.
    :param cash_flow_series: A ``["date", "value"]`` frame of net external flows.
    :param method: One of ``CalculationMethod.Types``.
    :returns: A ``(pct_change, dly_pct_change)`` tuple of float lists.
    """
    if method == CalculationMethod.SIMPLE:
        pct = simple_cumulative(balance_series)["value"].to_list()
        dly = simple_daily(balance_series)["value"].to_list()
    elif method == CalculationMethod.TWR:
        pct = twr_cumulative(balance_series, cash_flow_series)["value"].to_list()
        dly = twr_daily(balance_series, cash_flow_series)["value"].to_list()
    else:  # Money-Weighted (IRR)
        pct = mwr_cumulative(balance_series, cash_flow_series)["value"].to_list()
        # the "daily" figure is the plain day-over-day balance change, same as Simple
        dly = simple_daily(balance_series)["value"].to_list()
    return pct, dly


def _align_to_dates(pl_dates, values):
    """
    Back-fill a values array (with possible nulls) aligned to the merged
    calendar: forward-fill from the last seen value, then back-fill any leading
    nulls from the last seen value. Mirrors the legacy ``.ffill().bfill()`` on
    the date-merged balance/Close columns.
    """
    vals = [None if v is None else float(v) for v in values]
    n = len(pl_dates)
    result = np.full(n, np.nan, dtype=float)
    # forward fill
    last = np.nan
    for i in range(n):
        if vals[i] is not None:
            last = vals[i]
        result[i] = last
    # back fill leading nulls from the first valid value
    first = np.nan
    for i in range(n):
        if vals[i] is not None:
            first = vals[i]
            break
    for i in range(n):
        if np.isnan(result[i]):
            result[i] = first
    return result


def _date_df(pl_dates, pl_values):
    """
    Build a two-column ``["date", "value"]`` DataFrame aligned to the merged
    calendar dates (fwd/bwd filled), the shape the performance routines expect.
    """
    return pl.DataFrame({
        "date": pl.Series(pl_dates, dtype=pl.Datetime),
        "value": pl.Series(_align_to_dates(pl_dates, pl_values), dtype=pl.Float64),
    })


def _as_date(d):
    """Normalize a polars date/datetime value to a ``datetime.date``."""
    if isinstance(d, datetime):
        return d.date()
    return d


def _ts(d):
    """Normalize a date/datetime/timestamp to a midnight datetime for comparison."""
    if isinstance(d, datetime):
        return d if d.hour == d.minute == d.second == 0 else d.replace(
            hour=0, minute=0, second=0, microsecond=0)
    if isinstance(d, date):
        return datetime(d.year, d.month, d.day)
    return d


# function to draw a graph comparing the cumulative performance of the selected
# portfolio against a comparison target (a ticker symbol or another account)
def plot_daily_balance(df: pl.DataFrame, compare, account_id):
    """
    Plot the daily balance for a given account over a specified number of days.

    :param df: The dataframe containing balance and comparison data.
    :param compare: The comparison target name (a ticker symbol or an account name).
    :param account_id: The account ID to plot.
    """
    # mark entry into the function
    _logger.debug("Entering function plot_daily_balance with %d entries", len(df))

    # get the account name for the specified account ID
    account_name = get_account(account_id).account_name

    # prepare data for plotting
    dates: List[datetime] = list(df['Date'])
    dly_balance = list(df['balance'])
    dly_pct_change: List[float] = list(df['dly_pct_change'])
    change: List[float] = list(df['pct_change'])
    avg_10: List[float] = list(df['10_day_avg'])
    avg_21: List[float] = list(df['21_day_avg'])
    comparison: List[float] = list(df['comp_change'])
    dly_comp_change: List[float] = list(df['dly_comp_change'])

    # create the plot
    fig: go.Figure = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=np.zeros(len(dates)),
            # y trace is set to zero to avoid affecting the y-axis scale
            # no line, just a placeholder for hover text
            mode='none', showlegend=False,
            # add the daily balance and percent change to the hover text
            customdata=list(zip(dly_balance, dly_pct_change)),
            hovertemplate=
                "<extra>Balance: $%{customdata[0]:,.2f}<br>" +
                "Pct Change: %{customdata[1]:.1%}</extra>",
        ))
    fig.add_trace(go.Scatter(x=dates, y=change,
            mode='lines' , name='Cumulative Change',
            hoverlabel=dict(namelength = -1),
            line=dict(color='orange'),
        ))
    fig.add_trace(go.Scatter(x=dates, y=avg_10,
            mode='lines', name='10-day Avg',
            line=dict(color='purple')
        ))
    fig.add_trace(go.Scatter(x=dates, y=avg_21,
            mode='lines', name='21-day Avg',
            line=dict(color='green')
        ))
    fig.add_trace(go.Scatter(x=dates, y=comparison,
            mode='lines', name=compare,
            line=dict(color='darkgrey'),
        ))
    fig.add_trace(go.Scatter(x=dates, y=dly_comp_change,
            mode='none', name=f'{compare} Pct Change',
            showlegend=False,
        ))

    fig.update_layout(
        title=f'Performance for {account_name}',
        xaxis_title='Date', yaxis_title='Cumulative Percent Change',
        hovermode="x unified",
        clickmode="event",
        dragmode=False,
        modebar=go.layout.Modebar(remove=("zoom","zoomin", "zoomout","pan","select","lasso")),
    )
    fig.update_yaxes(dict(tickformat=".1%"))

    return fig

# get the accounts (also used to offer them as comparison targets below)
accounts = get_accounts()

# get the account selection component
account_selector = get_account_selection_component(
                                        _ACCOUNT_SELECTION_KEY,
                                        label="Account:",
                                        options=accounts,
                                        )

# get the status message component
status_message = get_status_message_component(f"status_{st.context.ip_address}")

# if no account is available, don't continue
if account_selector.selected is None:
    status_message.set_status_message(stat.WARNING, "Please select an account")
    status_message.show_status_messages()
    st.stop()
else:
    selected_account_id = account_selector.selected
    if isinstance(selected_account_id, list):
        # if multiple accounts are selected, just use the first one for the
        # performance summary (the component allows multi-selection but the
        # page only supports a single account)
        selected_account_id = selected_account_id[0]

# The comparison target is a ticker or *another* account; the currently selected
# account is excluded so it can never be compared against itself. Kept at module
# scope (not inside the sidebar block) because the comparison resolution below
# also needs it.
comparison_accounts = [a for a in accounts if a.account_id != selected_account_id]

# get the time machine component
default_period = get_period(SETTINGS.defaults.performance_summary_period)
time_machine = get_time_machine_component(
                                          _TIME_MACHINE_COMPONENT_KEY,
                                          period=default_period,
                                          end_date=get_last_balance_date(selected_account_id),
                                          )
# set the max and min dates based on the selected account's balance history
time_machine.max_date=get_last_balance_date(selected_account_id)
time_machine.min_date=get_first_balance_date(selected_account_id)

# configure the page layout
st.set_page_config(layout="wide")

# page title
st.title(f"Performance Summary for {get_account(selected_account_id).account_name}")

# add input widgets to the sidebar
with st.sidebar:
    # render the account selection component
    account_selector.render()

    # render the time machine component
    time_machine.render()

    # create a selectbox to select the comparison target for the chart. The
    # options are the configured ticker symbols followed by every account except
    # the selected one (each prefixed with an em-dash so it can never be confused
    # with a ticker).
    selected_comparison = st.selectbox(
                            "Compare:",
                            comparison_options(_COMPARISON_SYMBOLS, comparison_accounts),
                            index=0,
                            width=150)

    # select which performance calculation to display
    default_method = SETTINGS.defaults.performance_summary_method
    if not CalculationMethod.is_valid(default_method):
        default_method = CalculationMethod.TWR
    selected_method = st.selectbox(
                            "Calculation Method:",
                            CalculationMethod.Types,
                            index=CalculationMethod.Types.index(default_method),
                            key=_METHOD_KEY)

    # the cash-flow toggles only apply to the TWR and MWR methods
    toggles_disabled = selected_method == CalculationMethod.SIMPLE

    # include dividends and interest as part of the return (default on)
    include_div_int = st.toggle(
                            "Include dividends and interest",
                            value=SETTINGS.defaults.include_dividends_interest,
                            key=_INCLUDE_DIV_INT_KEY,
                            disabled=toggles_disabled)

    # include fees and taxes in the return (default on; they reduce returns)
    include_fees_tax = st.toggle(
                            "Include Fees and Taxes",
                            value=SETTINGS.defaults.include_fees_taxes,
                            key=_INCLUDE_FEES_TAX_KEY,
                            disabled=toggles_disabled)

# if the time machine isn't set, don't continue
if time_machine.period_selected == Periods.NONE:
    status_message.set_status_message(stat.WARNING,
                                      "Select a time period"
                                      )
    status_message.show_status_messages()
    st.stop()

# get the balance history for the selected account
df_balances = get_balance_history(account_id=selected_account_id,
                                  begin_date=time_machine.begin_date,
                                  end_date=time_machine.end_date,
                                  ascending=True
                                  )
# skip if there is no balance data
if df_balances.is_empty():
    status_message.set_status_message(
                                       stat.WARNING,
                                       "No balance data found for the specified period",
                                       )
    status_message.show_status_messages()
    st.stop()

# check the returned dates against the date pickers in the time machine
# adjust the date pickers if necessary to ensure they match the returned data
df_begin_date = _as_date(df_balances["balance_date"].item(0))
df_end_date = _as_date(df_balances["balance_date"].item(-1))
if time_machine.begin_date != df_begin_date or time_machine.end_date != df_end_date:
    time_machine.update_date_pickers(df_begin_date, df_end_date)
    status_message.set_status_message(stat.INFO, "Dates updated to reflect dates on file")

# fetch historical data for the comparison target since the begin date. The
# target is either a ticker symbol (fetched from yfinance) or another account
# (fetched from the database); both are normalised to a ["Date", "Close"] frame.
compare_is_account = is_account_option(selected_comparison)
compare_label = (account_name_from_option(selected_comparison)
                 if compare_is_account else selected_comparison)

if compare_is_account:
    # comparison against another account: use its daily balance history
    compare_account_id = account_id_for_option(selected_comparison, comparison_accounts)
    if compare_account_id is None:
        # the selected option no longer resolves to an account (e.g. it was the
        # account that is now selected as the main target, so it is excluded);
        # render without a comparison rather than querying an unknown account.
        status_message.set_status_message(
            stat.INFO,
            f"{compare_label} is the selected account; no comparison shown.",
        )
        has_comparison = False
        # create an empty frame with the expected schema so the rest of the code can run
        df_comparison = pl.DataFrame(schema={"Date": pl.Date, "Close": pl.Float64})
    # if compare_account_id is None:
    #     # the selected option no longer resolves to an account (e.g. it was the
    #     # account that is now selected as the main target, so it is excluded);
    #     # render without a comparison rather than querying an unknown account.
    #     status_message.set_status_message(
    #         stat.INFO,
    #         f"{compare_label} is the selected account; no comparison shown.",
    #     )
    #     has_comparison = False
    else:
        df_comparison = (
            get_balance_history(account_id=compare_account_id,
                                begin_date=df_begin_date,
                                end_date=df_end_date,
                                ascending=True)
            .rename({"balance_date": "Date", "balance": "Close"})
            .select("Date", "Close")
        )
        df_comparison = df_comparison.with_columns(
            pl.col("Date").cast(pl.Date).alias("Date")
        )
        if df_comparison.is_empty():
            status_message.set_status_message(
                stat.WARNING,
                f"No balance data found for comparison account "
                f"{compare_label} in the specified period",
            )
            has_comparison = False
        else:
                has_comparison = True
else:
    # comparison against a ticker symbol
    df_comparison = get_stock_history(
            selected_comparison,
            start_date=df_begin_date,
            end_date=df_end_date,
            )
    df_comparison = df_comparison.with_columns(
        pl.col("Date").cast(pl.Date).alias("Date")
    )
    has_comparison = not df_comparison.is_empty()
# normalize the balance dates to the same type so the join keys match
df_balances = df_balances.with_columns(
    pl.col("balance_date").cast(pl.Date).alias("balance_date")
)

# merge the balances with the comparison data on the date
merged = df_comparison.join(
    df_balances.rename({"balance_date": "Date"}),
    on="Date", how="left")
# keep only the needed columns in a stable order
merged = merged.select("Date", "balance", "Close")
merged = merged.sort("Date", maintain_order=True)
merged_dates = merged["Date"].to_list()

# the merged frame's balance/Close are already aligned to the calendar by the
# join; back-fill any nulls (calendar days with no source row) ffill/bfill-style
merged_balance = _align_to_dates(merged_dates, merged["balance"].to_list())
merged_close = _align_to_dates(merged_dates, merged["Close"].to_list())

# determine which trade types are netted out of the return based on the toggles.
# deposits/withdrawals and security transfers (ACAT) are always external money
# moving in or out of the account; dividends/interest and fees/taxes are netted
# out only when their respective "include" toggle is off. (Those toggles default
# on, so by default only deposits, withdrawals and transfers are netted -- this
# is what makes the money-weighted return differ from the simple return.)
netted_out_types = [TradeType.DEPOSIT, TradeType.WITHDRAWAL, TradeType.TRANSFER]
if not include_div_int:
    netted_out_types += [TradeType.DIVIDEND, TradeType.INTEREST]
if not include_fees_tax:
    netted_out_types += [TradeType.FEE, TradeType.TAX]

# fetch the net external cash flows for the period (only needed for TWR and MWR)
if selected_method in (CalculationMethod.TWR, CalculationMethod.MWR):
    df_cash_flows = get_cash_flows(
        account_id=selected_account_id,
        begin_date=df_begin_date,
        end_date=df_end_date,
        trade_types=netted_out_types,
    )
    # initialize a zero cash-flow value per merged calendar date
    cf_values = np.zeros(len(merged_dates), dtype=float)
    if not df_cash_flows.is_empty():
        for d, amount in zip(
                df_cash_flows["trade_date"].to_list(),
                df_cash_flows["cash_flow"].to_list()):
            # attribute each flow to the first balance day on/after its trade
            # date so a flow dated off-calendar still nets out of the correct
            # period
            d_mid = _ts(d)
            for i, cal in enumerate(merged_dates):
                if _ts(cal) >= d_mid:
                    cf_values[i] += float(amount)
                    break
else:
    cf_values = np.zeros(len(merged_dates), dtype=float)

# build a balance series aligned to the merged calendar (fwd/bwd filled)
balance_series = _date_df(merged_dates, merged_balance)
# build a cash-flow series aligned to the same calendar
cash_flow_series = pl.DataFrame({
    "date": pl.Series(merged_dates, dtype=pl.Datetime),
    "value": pl.Series(cf_values, dtype=pl.Float64),
})
# build the comparison close series aligned to the merged calendar
close_series = _date_df(merged_dates, merged_close)

# add the portfolio performance for the selected calculation method
pct_change, dly_pct_change = _dispatch_method(
    balance_series, cash_flow_series, selected_method)

# calculate the moving averages of the percentage change
pct_arr = np.asarray(pct_change, dtype=float)
n = len(pct_arr)
avg10 = np.full(n, np.nan, dtype=float)
avg21 = np.full(n, np.nan, dtype=float)
csum = np.cumsum(np.insert(pct_arr, 0, 0.0))
for w, avg in ((10, avg10), (21, avg21)):
    for i in range(w - 1, n):
        avg[i] = (csum[i + 1] - csum[i + 1 - w]) / w

# add the cumulative performance for the comparison target. For an account
# comparison the same calculation method (and cash-flow netting) as the main
# account is applied, so the two curves are directly comparable; for a ticker
# comparison the comparison series has no cash flows, so simple returns are used.
# When the comparison has no data (an empty frame) the comparison series is left
# as NaN so the main account still renders.
if has_comparison and compare_is_account:
    compare_account_id = account_id_for_option(selected_comparison, comparison_accounts)
    if compare_account_id is not None and selected_method in (CalculationMethod.TWR, CalculationMethod.MWR):
        df_comp_cash_flows = get_cash_flows(
            account_id=compare_account_id,
            begin_date=df_begin_date,
            end_date=df_end_date,
            trade_types=netted_out_types,
        )
    else:
        df_comp_cash_flows = pl.DataFrame(
            schema={"trade_date": pl.Date, "cash_flow": pl.Float64})
    # align the comparison account's cash flows to the merged calendar, using the
    # same off-calendar attribution rule as the main account
    comp_cf_values = np.zeros(len(merged_dates), dtype=float)
    if not df_comp_cash_flows.is_empty():
        for d, amount in zip(
                df_comp_cash_flows["trade_date"].to_list(),
                df_comp_cash_flows["cash_flow"].to_list()):
            d_mid = _ts(d)
            for i, cal in enumerate(merged_dates):
                if _ts(cal) >= d_mid:
                    comp_cf_values[i] += float(amount)
                    break
    comp_cash_flow_series = pl.DataFrame({
        "date": pl.Series(merged_dates, dtype=pl.Datetime),
        "value": pl.Series(comp_cf_values, dtype=pl.Float64),
    })
    # the comparison balance series is the (aligned) comparison account balance
    comp_balance_series = close_series
    comp_change, dly_comp_change = _dispatch_method(
        comp_balance_series, comp_cash_flow_series, selected_method)
elif has_comparison:
    # ticker comparison: the comparison series has no cash flows
    comp_change = simple_cumulative(close_series)["value"].to_list()
    dly_comp_change = simple_daily(close_series)["value"].to_list()
else:
    # no comparison data; leave the comparison series empty (NaN)
    comp_change = np.full(len(merged_dates), np.nan, dtype=float).tolist()
    dly_comp_change = np.full(len(merged_dates), np.nan, dtype=float).tolist()

# assemble the merged frame for display and plotting
merged = merged.with_columns([
    pl.Series("balance", merged_balance),
    pl.Series("pct_change", pct_change),
    pl.Series("dly_pct_change", dly_pct_change),
    pl.Series("10_day_avg", avg10),
    pl.Series("21_day_avg", avg21),
    pl.Series("comp_change", comp_change),
    pl.Series("dly_comp_change", dly_comp_change),
])

# display summary subheader
if time_machine.period_selected == Periods.CUS:
    selected_period = f"{df_begin_date} to {df_end_date}" # pylint: disable-msg=C0103
else:
    selected_period = Periods.get_label(time_machine.period_selected)
# label the headline figure according to the selected calculation method
if selected_method == CalculationMethod.MWR:
    perf_label = "Money-Weighted Return"
else:
    perf_label = f"Total Cumulative Performance ({selected_method})"
st.subheader(f"{perf_label} for period "
              f"{selected_period}: {merged['pct_change'].item(-1):.1%}"
              )
if has_comparison:
    st.subheader(f"Comparison ({compare_label}) Cumulative Performance: "
               f"{merged['comp_change'].item(-1):.1%}"
               )

# display statistics for the current day
st.subheader(
    f"Current Day Performance for "
    f"{get_account(selected_account_id).account_name} ({_as_date(merged['Date'].item(-1))}):"
    )
st.write(f"- Balance: ${merged['balance'].item(-1):,.2f}")
st.write(f"- Daily Change: {merged['dly_pct_change'].item(-1):.1%}")
if has_comparison:
    st.write(f"- Comparison ({compare_label})"
               f" - Daily Change: {merged['dly_comp_change'].item(-1):.1%}"
               )

# plot the daily balance for the selected period
st.plotly_chart(plot_daily_balance(merged,
                compare=compare_label,
                account_id=selected_account_id),
                width='stretch'
                )

# show the status messages
status_message.show_status_messages()
