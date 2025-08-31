"""
Update the daily balance for a specified account and day.
Plot the daily performance of the account.
"""
# Import necessary libraries
from typing import List
from datetime import timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import local modules
from data import (
    get_account,
    get_balance_history,
    get_stock_history,
    Periods
)

# function to draw a graph comparing cumulative performance for the selected portfolio and SPY
def plot_daily_balance(period, compare = "SPY", account_id=1):
    """
    Plot the daily balance for a given account over a specified number of days.

    :param days: The number of days to plot.
    :param account_id: The account ID to plot (default is 1).
    """
    # get the account name for the specified account ID
    account_name = get_account(account_id).name

    # get the balance history for the specified account
    df_balances = get_balance_history(account_id, period)
    # get the begin and end dates from the df_balances dataframe
    begin_date = df_balances.loc[0, 'date']
    end_date = \
        df_balances.loc[len(df_balances)-1, 'date'] + timedelta(days=1)

    # calculate the cumulative percent change
    df_balances['pct_change'] = \
        df_balances['balance'].rolling(window=2).apply(
            lambda x: (x.iloc[1] - x.iloc[0]) / x.iloc[0]
        ).cumsum()
    # set the first day pct_change to 0
    df_balances.loc[0, 'pct_change'] = 0

    # calculate the 10-day moving average of the percentage change
    df_balances['10_day_avg'] = \
        df_balances['pct_change'].rolling(window=10).mean()
    # calculate the 21-day moving average of the percentage change
    df_balances['21_day_avg'] = \
        df_balances['pct_change'].rolling(window=21).mean()

    # fetch historical SPY data since the begin date
    spy_data: pd.DataFrame = get_stock_history(
                    compare,
                    start_date=begin_date,
                    end_date=end_date)

    # calculate the cumulative percent change for SPY
    spy_data['pct_change'] = \
        spy_data['Close'].rolling(window=2).apply(
            lambda x: (x.iloc[1] - x.iloc[0]) / x.iloc[0]
        ).cumsum()
    # set the first day pct_change to 0
    spy_data.loc[0, 'pct_change'] = 0

    # prepare data for plotting
    dates: List[pd.Timestamp] = list(df_balances['date'])
    change: List[float] = list(df_balances['pct_change'])
    avg_10: List[float] = list(df_balances['10_day_avg'])
    avg_21: List[float] = list(df_balances['21_day_avg'])
    spy: List[float] = list(spy_data['pct_change'])
    spy_dt: List[pd.Timestamp] = list(spy_data['Date'])

    # create the plot
    fig: go.Figure = go.Figure(data=go.Scatter(x=dates, y=change,
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
    fig.add_trace(go.Scatter(x=spy_dt, y=spy,
            mode='lines', name=compare,
            line=dict(color='darkgrey')
        ))

    fig.update_layout(
        title=f'Performance for {account_name} over period of {period}',
        xaxis_title='Date', yaxis_title='Cumulative Percent Change',
        hovermode="x"
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
                            Periods.get_display_periods(),
                            index=1,
                            width=300)
    # create a selectbox to select the comparison symbol for the chart
    selected_comparison = st.selectbox(
                            "Compare:",
                            ["SPY", "QQQ"],
                            index=0,
                            width=100)

st.plotly_chart(plot_daily_balance(selected_period,
                                   selected_comparison,
                                   account_id=1),
                use_container_width=True
                )
