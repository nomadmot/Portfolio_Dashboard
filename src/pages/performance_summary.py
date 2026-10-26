"""
Plot the daily performance of the specified account compared to a selected stock ticker.
"""
# Import standard libraries
from typing import List
from pathlib import Path

# Import 3rd party libraries
import streamlit as st
import numpy as np
import pandas as pd
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


# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def plot_daily_balance(df: pd.DataFrame, compare, account_id):
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
    dates: List[pd.Timestamp] = list(df['Date'])
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
    status_message.set_status_message(stat.WARNING, "No accounts available")
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
if df_balances.empty:
    status_message.set_status_message(
                                     stat.WARNING,
                                     "No balance data found for the specified period",
                                     )
    status_message.show_status_messages()
    st.stop()

# check the returned dates against the date pickers in the time machine
# adjust the date pickers if necessary to ensure they match the returned data
df_begin_date = df_balances['balance_date'].iloc[0]
df_end_date = df_balances['balance_date'].iloc[-1]
if time_machine.begin_date != df_begin_date or time_machine.end_date != df_end_date:
    time_machine.update_date_pickers(df_begin_date, df_end_date)
    status_message.set_status_message(stat.INFO, "Dates updated to reflect dates on file")

# fetch historical data for the comparison ticker
# since the begin date
df_comparison: pd.DataFrame = get_stock_history(
                selected_comparison,
                start_date=df_begin_date,
                end_date=df_end_date,
            )
# drop the time component from the Date column
df_comparison['Date'] = pd.to_datetime(df_comparison['Date']).dt.date
# merge the balances with the comparison data
merged = pd.merge(df_comparison, df_balances, how='left', left_on='Date', right_on='balance_date')
# fill in any missing balance values
merged['balance'] = merged['balance'].ffill().bfill()

# build a date-indexed balance series (MWR needs the dates for day counts)
balance_series = pd.Series(merged['balance'].to_numpy(), index=merged['Date'])

# determine which trade types are netted out of the return based on the toggles.
# deposits/withdrawals are always external; dividends/interest and fees/taxes are
# netted out only when their respective toggle is switched off.
netted_out_types = [TradeType.DEPOSIT, TradeType.WITHDRAWAL]
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
    cash_flow_series = pd.Series(0.0, index=balance_series.index)
    if not df_cash_flows.empty:
        cf_by_date = df_cash_flows.set_index('trade_date')['cash_flow']
        # attribute each flow to the first balance day on/after its trade date so
        # a flow dated off-calendar still nets out of the correct period
        for trade_date, amount in cf_by_date.items():
            pos = balance_series.index.searchsorted(trade_date)
            if pos < len(balance_series.index):
                cash_flow_series.iloc[pos] += amount
else:
    cash_flow_series = pd.Series(0.0, index=balance_series.index)

# add the portfolio performance for the selected calculation method
if selected_method == CalculationMethod.SIMPLE:
    merged['pct_change'] = simple_cumulative(balance_series).to_numpy()
    merged['dly_pct_change'] = simple_daily(balance_series).to_numpy()
elif selected_method == CalculationMethod.TWR:
    merged['pct_change'] = twr_cumulative(balance_series, cash_flow_series).to_numpy()
    merged['dly_pct_change'] = twr_daily(balance_series, cash_flow_series).to_numpy()
else:  # Money-Weighted (IRR)
    merged['pct_change'] = mwr_cumulative(balance_series, cash_flow_series).to_numpy()
    # the "daily" figure (hover text and subheader) is the plain day-over-day
    # balance change, same definition as the Simple method; the day-over-day
    # change of the cumulative would divide by a near-zero total return and
    # stretch the plot scale to thousands of percent
    merged['dly_pct_change'] = simple_daily(balance_series).to_numpy()

# calculate the 10-day moving average of the percentage change
merged['10_day_avg'] = merged['pct_change'].rolling(window=10).mean()
# calculate the 21-day moving average of the percentage change
merged['21_day_avg'] = merged['pct_change'].rolling(window=21).mean()
# add the cumulative performance for the comparison ticker (always simple returns)
merged['comp_change'] = simple_cumulative(merged['Close'])
# add the daily performance for the comparison ticker
merged['dly_comp_change'] = simple_daily(merged['Close'])

# display summary subheader
if time_machine.period_selected == Periods.CUS:
    selected_period = f"{df_begin_date} to {df_end_date}" # pylint: disable-msg=C0103
else:
    selected_period = Periods.get_label(time_machine.period_selected)
# label the headline figure according to the selected calculation method
if selected_method == CalculationMethod.MWR:
    perf_label = "Money-Weighted Return (IRR, cumulative)"
else:
    perf_label = f"Total Cumulative Performance ({selected_method})"
st.subheader(f"{perf_label} for period "
             f"{selected_period}: {merged['pct_change'].iloc[-1]:.1%}"
             )
st.subheader(f"Comparison ({selected_comparison}) Cumulative Performance: "
         f"{merged['comp_change'].iloc[-1]:.1%}"
         )

# display statistics for the current day
st.subheader(
    f"Current Day Performance for "
    f"{get_account(selected_account_id).account_name} ({merged['Date'].iloc[-1]}):"
    )
st.write(f"- Balance: ${merged['balance'].iloc[-1]:,.2f}")
st.write(f"- Daily Change: {merged['dly_pct_change'].iloc[-1]:.1%}")
st.write(f"- Comparison ({selected_comparison})"
         f" - Daily Change: {merged['dly_comp_change'].iloc[-1]:.1%}"
         )

# plot the daily balance for the selected period
st.plotly_chart(plot_daily_balance(merged,
                compare=selected_comparison,
                account_id=selected_account_id),
                width='stretch'
                )

# show the status messages
status_message.show_status_messages()
