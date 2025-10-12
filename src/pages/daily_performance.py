"""
Update the daily balance for a specified account and day.
Plot the daily performance of the account.
"""
# Import necessary libraries
from typing import List
from datetime import date, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import local modules
from core import (
    Periods,
    get_account,
    get_balance_history,
)
from services import get_stock_history

# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def calculate_daily_balance(period, account_id=1):
    """
    calculate the daily balance for a given account over a specified number of days.

    :param days: The period over which performance will be calculated.
    :param account_id: The account ID to plot (default is 1).
    """

    # get the balance history for the specified account
    df_balances = get_balance_history(account_id=account_id,
                                      period=period,
                                      ascending=True
                                      )

    # calculate the cumulative percent change
    df_balances['pct_change'] = \
        df_balances['balance'].rolling(window=1).apply(
            lambda x: (x.iloc[0] - df_balances['balance'][0]) / df_balances['balance'][0]
        )
    # set the first day pct_change to 0
    df_balances.loc[0, 'pct_change'] = 0

    # calculate the 10-day moving average of the percentage change
    df_balances['10_day_avg'] = \
        df_balances['pct_change'].rolling(window=10).mean()
    # calculate the 21-day moving average of the percentage change
    df_balances['21_day_avg'] = \
        df_balances['pct_change'].rolling(window=21).mean()

    #return the dataframe for further processing
    return df_balances


# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def plot_daily_balance(period, balances, compare = "SPY", account_id=1):
    """
    Plot the daily balance for a given account over a specified number of days.

    :param period: The period to be displayed in the plot.
    :param balances: The dataframe containing balance history and calculated fields.
    :param compare: The ticker symbol to compare against (default is "SPY").
    :param account_id: The account ID to plot (default is 1).
    """
    # get the account name for the specified account ID
    account_name = get_account(account_id).name

    # get the begin and end dates from the balances dataframe
    dates = pd.to_datetime(balances['date']).astype('datetime64[ns]').tolist()
    begin_date: date = dates[0]
    end_date: date = dates[len(dates)-1] + timedelta(days=1)

    # fetch historical data for the comparison ticker
    # since the begin date
    comp_data: pd.DataFrame = get_stock_history(
                    compare,
                    start_date=begin_date,
                    end_date=end_date)

    # calculate the cumulative percent change for the chosen comparison ticker
    comp_data['pct_change'] = \
        comp_data['Close'].rolling(window=1).apply(
            lambda x: (x.iloc[0] - comp_data['Close'][0]) / comp_data['Close'][0]
        )
    # set the first day pct_change to 0
    comp_data.loc[0, 'pct_change'] = 0

    # prepare data for plotting
    dates: List[pd.Timestamp] = list(balances['date'])
    change: List[float] = list(balances['pct_change'])
    avg_10: List[float] = list(balances['10_day_avg'])
    avg_21: List[float] = list(balances['21_day_avg'])
    comp_performance: List[float] = list(comp_data['pct_change'])
    comp_date: List[pd.Timestamp] = list(comp_data['Date'])

    # create the plot
    fig: go.Figure = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=change,
            mode='lines' , name='Pct Change',
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
    fig.add_trace(go.Scatter(x=comp_date, y=comp_performance,
            mode='lines', name=compare,
            line=dict(color='darkgrey'),
            # add the daily balance at the end of the hover text
            customdata=balances[['balance']],
            hovertemplate='%{y}<br>Balance: $%{customdata[0]:.2f}',
        ))

    fig.update_layout(
        title=f'Performance for {account_name} over period of {Periods.get_label(period)}',
        xaxis_title='Date', yaxis_title='Cumulative Percent Change',
        hovermode="x unified"
    )
    fig.update_yaxes(dict(tickformat=".1%"))

    return fig


# configure the page layout
st.set_page_config(layout="wide")

# page subheader
st.subheader("Daily Performance Chart")

# create a horizontal layout for the selectboxes
with st.container(horizontal=True,
                  horizontal_alignment="center",
                  border=True,
                  width=450):
    # create a selectbox to select the number of days for the chart
    selected_period = st.selectbox(
                            "Select Period:",
                            Periods.get_periods(),
                            format_func=Periods.get_label,
                            index=1,
                            width=300)
    # create a selectbox to select the comparison symbol for the chart
    selected_comparison = st.selectbox(
                            "Compare:",
                            ["SPY", "QQQ"],
                            index=0,
                            width=100)

# calculate the daily balance for the selected period
work_balances = calculate_daily_balance(selected_period,
                                      account_id=1)

# plot the daily balance for the selected period
st.plotly_chart(plot_daily_balance(selected_period,
                                   work_balances,
                                   selected_comparison,
                                   account_id=1),
                use_container_width=True
                )

# page subheader
st.subheader(f"Total Cumulative Performance for period: {work_balances['pct_change'].iloc[-1]:.1%}")
