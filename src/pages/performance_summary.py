"""
Plot the daily performance of the specified account compared to a selected stock ticker.
"""
# Import necessary libraries
from typing import List
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import local modules
from utility import get_time_machine_component
from core import (
    Periods,
    get_account,
    get_balance_history,
)
from core import get_stock_history

# function to calculate the cumulative performance for a given series
def calculate_cumulative_performance(data: pd.Series):
    """
    Calculate the cumulative performance for a given account over a specified number of days.

    :param series: The series over which performance will be calculated.
    """

    # store the initial balance value for efficient calculation
    initial_balance = data.iloc[0]
    # calculate the cumulative percent change
    ret_val = data.rolling(window=1).apply(
            lambda x: (x.iloc[0] - initial_balance) / initial_balance
            )
    # set the first day pct_change to 0
    ret_val.iloc[0] = 0

    #return the dataframe for further processing
    return ret_val


# function to calculate the daily performance for a given series
def calculate_daily_performance(data: pd.Series):
    """
    Calculate the daily performance for a given account over a specified number of days.

    :param series: The series over which performance will be calculated.
    """

    # calculate the cumulative percent change
    ret_val = data.rolling(window=2).apply(
            lambda x: (x.iloc[1] - x.iloc[0]) / x.iloc[0]
            )
    # set the first day pct_change to 0
    ret_val.iloc[0] = 0

    #return the dataframe for further processing
    return ret_val


# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def plot_daily_balance(df: pd.DataFrame, compare, account_id=1):
    """
    Plot the daily balance for a given account over a specified number of days.

    :param df: The dataframe containing balance and comparison data.
    :param compare: The comparison ticker symbol.
    :param account_id: The account ID to plot (default is 1).
    """
    # get the account name for the specified account ID
    account_name = get_account(account_id).name

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
    fig.add_trace(go.Scatter(x=dates, y=dly_pct_change,
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


# configure the page layout
st.set_page_config(layout="wide")

# page title
st.title(f"Performance Summary for {get_account(1).name}")

# add input widgets to the sidebar
with st.sidebar:
    # create a selectbox to select the number of days for the chart
    time_machine = get_time_machine_component("daily_performance_time_machine")
    time_machine.render()
    # create a selectbox to select the comparison symbol for the chart
    selected_comparison = st.selectbox(
                            "Compare:",
                            ["SPY", "QQQ", "FFTY"],
                            index=0,
                            width=150)

# get the balance history for the specified account
df_balances = get_balance_history(account_id=1,
                                  from_date=time_machine.begin_date,
                                  to_date=time_machine.end_date,
                                  ascending=True
                                  )
# skip if there is no balance data
if df_balances.empty:
    st.warning("No balance data found for the specified period.")
    st.stop()

# fetch historical data for the comparison ticker
# since the begin date
df_comparison: pd.DataFrame = get_stock_history(
                selected_comparison,
                start_date=time_machine.begin_date,
                end_date=time_machine.end_date,
            )
# drop the time component from the Date column
df_comparison['Date'] = pd.to_datetime(df_comparison['Date']).dt.date
# merge the balances with the comparison data
merged = pd.merge(df_comparison, df_balances, how='left', left_on="Date", right_on="date")
# fill in any missing balance values
merged['balance'] = merged['balance'].ffill().bfill()

# add the cumulative performance for the daily balances
merged['pct_change'] = calculate_cumulative_performance(merged['balance'])
# add the daily performance for the daily balances
merged['dly_pct_change'] = calculate_daily_performance(merged['balance'])
# calculate the 10-day moving average of the percentage change
merged['10_day_avg'] = merged['pct_change'].rolling(window=10).mean()
# calculate the 21-day moving average of the percentage change
merged['21_day_avg'] = merged['pct_change'].rolling(window=21).mean()
# add the cumulative performance for the comparison ticker
merged['comp_change'] = calculate_cumulative_performance(merged['Close'])
# add the daily performance for the comparison ticker
merged['dly_comp_change'] = calculate_daily_performance(merged['Close'])

# display summary subheader
if time_machine.period_selected == Periods.CUS:
    selected_period = f"{time_machine.begin_date} to {time_machine.end_date}" # pylint: disable-msg=C0103
else:
    selected_period = Periods.get_label(time_machine.period_selected)
st.subheader(f"Total Cumulative Performance for period "
             f"{selected_period}: {merged['pct_change'].iloc[-1]:.1%}"
             )
st.subheader(f"Comparison ({selected_comparison}) Cumulative Performance: "
         f"{merged['comp_change'].iloc[-1]:.1%}"
         )

# display statistics for the current day
st.subheader(f"Current Day Performance for {get_account(1).name} ({merged['Date'].iloc[-1]}):")
st.write(f"- Balance: ${merged['balance'].iloc[-1]:,.2f}")
st.write(f"- Daily Change: {merged['dly_pct_change'].iloc[-1]:.1%}")
st.write(f"- Comparison ({selected_comparison})"
         f" - Daily Change: {merged['dly_comp_change'].iloc[-1]:.1%}"
         )

# plot the daily balance for the selected period
st.plotly_chart(plot_daily_balance(merged,
                compare=selected_comparison,
                account_id=1),
                width='stretch'
                )
