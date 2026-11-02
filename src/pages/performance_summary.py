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


# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def plot_daily_balance(df: pl.DataFrame, compare, account_id):
    """
    Plot the daily balance for a given account over a specified number of days.

    :param df: The dataframe containing balance and comparison data.
    :param compare: The comparison ticker symbol.
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

# get the account selection component
account_selector = get_account_selection_component(
                                        _ACCOUNT_SELECTION_KEY,
                                        label="Account:",
                                        options=get_accounts(),
                                        )

# get the status message component
status_message = get_status_message_component(f"status_{st.context.ip_address}")

# if no account is available, don't continue
selected_account_id = account_selector.selected
if selected_account_id is None:
    status_message.set_status_message(stat.WARNING, "Please select an account")
    status_message.show_status_messages()
    st.stop()

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

    # create a selectbox to select the comparison symbol for the chart
    selected_comparison = st.selectbox(
                            "Compare:",
                            SETTINGS.defaults.performance_summary_symbols,
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

# fetch historical data for the comparison ticker
# since the begin date
df_comparison = get_stock_history(
                selected_comparison,
                start_date=df_begin_date,
                end_date=df_end_date,
                )
# normalize the comparison Date column to calendar dates so it matches the
# date-only balance dates
df_comparison = df_comparison.with_columns(
    pl.col("Date").cast(pl.Date).alias("Date")
)
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
# the comparison source dates/values (the merged frame is the comparison calendar)
close_values = merged["Close"].to_list()

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
pct_change = None
dly_pct_change = None
if selected_method == CalculationMethod.SIMPLE:
    pct_change = simple_cumulative(balance_series)["value"].to_list()
    dly_pct_change = simple_daily(balance_series)["value"].to_list()
elif selected_method == CalculationMethod.TWR:
    pct_change = twr_cumulative(balance_series, cash_flow_series)["value"].to_list()
    dly_pct_change = twr_daily(balance_series, cash_flow_series)["value"].to_list()
else:  # Money-Weighted (IRR)
    # the main line is the cumulative money-weighted return (total, not
    # annualized); it nets external cash flows out of each day's IRR, so it
    # tracks the simple method on days with no flows and diverges on days
    # that have deposits/withdrawals/dividends/fees.
    pct_change = mwr_cumulative(balance_series, cash_flow_series)["value"].to_list()
    # the "daily" figure (hover text and subheader) is the plain day-over-day
    # balance change, same definition as the Simple method; the day-over-day
    # change of the cumulative would divide by a near-zero total return and
    # stretch the plot scale to thousands of percent
    dly_pct_change = simple_daily(balance_series)["value"].to_list()

# calculate the moving averages of the percentage change
pct_arr = np.asarray(pct_change, dtype=float)
n = len(pct_arr)
avg10 = np.full(n, np.nan, dtype=float)
avg21 = np.full(n, np.nan, dtype=float)
csum = np.cumsum(np.insert(pct_arr, 0, 0.0))
for w, avg in ((10, avg10), (21, avg21)):
    for i in range(w - 1, n):
        avg[i] = (csum[i + 1] - csum[i + 1 - w]) / w

# add the cumulative performance for the comparison ticker (always simple returns)
comp_change = simple_cumulative(close_series)["value"].to_list()
# add the daily performance for the comparison ticker
dly_comp_change = simple_daily(close_series)["value"].to_list()

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
st.subheader(f"Comparison ({selected_comparison}) Cumulative Performance: "
         f"{merged['comp_change'].item(-1):.1%}"
         )

# display statistics for the current day
st.subheader(
    f"Current Day Performance for "
    f"{get_account(selected_account_id).account_name} ({_as_date(merged['Date'].item(-1))}):"
    )
st.write(f"- Balance: ${merged['balance'].item(-1):,.2f}")
st.write(f"- Daily Change: {merged['dly_pct_change'].item(-1):.1%}")
st.write(f"- Comparison ({selected_comparison})"
         f" - Daily Change: {merged['dly_comp_change'].item(-1):.1%}"
         )

# plot the daily balance for the selected period
st.plotly_chart(plot_daily_balance(merged,
                compare=selected_comparison,
                account_id=selected_account_id),
                width='stretch'
                )

# show the status messages
status_message.show_status_messages()
