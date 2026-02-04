"""
Utility component to update selection when new options are added to a
Streamlit multiselect component.
"""
# Import standard libraries
from typing import Any
import logging
from datetime import date
from uuid import uuid4 as uuid

# Import 3rd party libraries
import streamlit as st

# Import local modules
from config import SETTINGS
from core import Periods, get_period_dates

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())


def period_select_callback(selected: Periods, instance):
    """
    responds to the on_change event for the _select_period selectbox
    calculates the dates for th selected option and updates the
    begin_date and end_dateproperties

    Arguments:
        selected_input -- the Period selection from the selectbox
        instance -- the TimeMachineComponent instance

    Returns:
        void
    """
    # log entry into the function
    logger.debug(
        "In function period_select_callback with selected_input=%s", selected)

    # calculate the dates for the selected option and update the instance properties
    instance.begin_date, instance.end_date = \
        get_period_dates(selected)


def begin_date_picker_callback(value: date, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In function begin_date_picker_callback with value=%s", value)

    # update the begin_date property
    instance.begin_date = value
    # update the period_selected property to "Custom"
    instance.period_selected = Periods.CUS


def end_date_picker_callback(value: date, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In function end_date_picker_callback with value=%s", value)

    # update the begin_date property
    instance.end_date = value
    # update the period_selected property to "Custom"
    instance.period_selected = Periods.CUS


class TimeMachineComponent:
    """
    Implements a composite component to select and mangage time period selection
    """
    # instance variables
    _period_selected: Periods|None
    _begin_date: date|None
    _end_date: date|None

    # placeholders for Streamlit widgets
    _select_period = None
    _begin_date_picker = None
    _end_date_picker = None

    # class properties
    @property
    def period_selected(self):
        """
        Returns the value of the currently selected period
        """
        return self._period_selected
    @period_selected.setter
    def period_selected(self, value: Periods):
        """
        Sets the value of the currently selected period
        """
        self._period_selected = value
        # update the selectbox to reflect the new selection
        self._select_period = value

    @property
    def begin_date(self):
        """
        Returns the value of the begin date
        """
        return self._begin_date
    @begin_date.setter
    def begin_date(self, value: date):
        """
        Sets the value of the begin date
        """
        self._begin_date = value
        # update the begin date picker to reflect the new date
        self._begin_date_picker = value

    @property
    def end_date(self):
        """
        Returns the value of the end date
        """
        return self._end_date
    @end_date.setter
    def end_date(self, value: date):
        """
        Sets the value of the end date
        """
        self._end_date = value
        # update the end date picker to reflect the new date
        self._end_date_picker = value

    def __init__(self):
        """
        Initializes the TimeMachineComponent instance
        """
        # log entry into the function
        logger.debug("In TimeMachineComponent constructor")

        self._period_selected = None
        self._begin_date = None
        self._end_date = None


    def render(self)-> Any:
        """
        Renders the TimeMachineComponent instance
        """
        # log entry into the function
        logger.debug("In TimeMachineComponent render method")

        # create a box to hold the component
        component = st.container(border=True)
        # render the Streamlit widgets for the component
        with component:
            # create the Streamlit widgets for the component
            self._select_period = st.selectbox(
                "Period",
                options=Periods.get_periods(),
                format_func=Periods.get_label,
                index=None,
                placeholder="Select Period",
                on_change=period_select_callback,
                args=(self._select_period, self),
            )
            self._begin_date_picker = st.date_input(
                "Begin Date",
                on_change=begin_date_picker_callback,
                args=(self._begin_date_picker, self),
            )
            self._end_date_picker = st.date_input(
                "End Date",
                on_change=end_date_picker_callback,
                args=(self._end_date_picker, self),
            )

        # log exit from the function
        logger.debug("Exiting TimeMachineComponent render method")
        return component
