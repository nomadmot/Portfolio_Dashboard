"""
Utility component to update selection when new options are added to a
Streamlit multiselect component.
"""
# Import standard libraries
from typing import Any
import logging
from datetime import date

# Import 3rd party libraries
import streamlit as st

# Import local modules
from config import SETTINGS
from core import Periods, get_period_dates

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(SETTINGS.loglevel_application.to_logging_level())

# Dictionary to hold component instances
_COMPONENT_INSTANCES = {}

# Keys for the individual Streamlit widgets in the component
_SELECT_PERIOD_KEY = "time_machine_select_period"
_BEGIN_DATE_PICKER_KEY = "time_machine_begin_date_picker"
_END_DATE_PICKER_KEY = "time_machine_end_date_picker"

# Callback functions for Streamlit widgets
def period_select_callback(key: str, instance):
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
        "In function period_select_callback with key=%s", key)

    # update the period_selected property
    instance.period_selected = st.session_state[key + _SELECT_PERIOD_KEY]

    # calculate the dates for the selected option and update the instance properties
    instance.begin_date, instance.end_date = \
        get_period_dates(st.session_state[key + _SELECT_PERIOD_KEY])

    # # set the date pickers to the new dates
    # st.session_state[key + _BEGIN_DATE_PICKER_KEY] = instance.begin_date
    # st.session_state[key + _END_DATE_PICKER_KEY] = instance.end_date


def begin_date_picker_callback(key: str, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In function begin_date_picker_callback with key=%s", key)

    # update the begin_date property
    instance.begin_date = st.session_state[key + _BEGIN_DATE_PICKER_KEY]
    # update the period_selected widget to "Custom"
    instance.period_selected = Periods.CUS


def end_date_picker_callback(key: str, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In function end_date_picker_callback with key=%s", key)

    # update the begin_date property
    instance.end_date = st.session_state[key + _END_DATE_PICKER_KEY]
    # update the period_selected widget to "Custom"
    instance.period_selected = Periods.CUS


class TimeMachineComponent:
    """
    Implements a composite component to select and mangage time period selection
    """
    # instance variables
    _component_key: str
    _period_selected: Periods
    _begin_date: date
    _end_date: date

    # placeholders for Streamlit widgets
    _select_period = None
    _begin_date_picker = None
    _end_date_picker = None

    # class properties
    @property
    def period_selected(self) -> Periods:
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
        # update the period_selected widget
        st.session_state[self._component_key + _SELECT_PERIOD_KEY] = value

    @property
    def begin_date(self) -> date:
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
        st.session_state[self._component_key + _BEGIN_DATE_PICKER_KEY] = self.begin_date

    @property
    def end_date(self) -> date:
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
        st.session_state[self._component_key + _END_DATE_PICKER_KEY] = self.end_date

    def __init__(self, component_key: str):
        """
        Initializes the TimeMachineComponent instance
        """
        # log entry into the function
        logger.debug("In TimeMachineComponent constructor")

        # NOTE: initial state is illogical
        self._component_key = component_key
        self._period_selected = Periods.ALL
        self._begin_date = date.today()
        self._end_date = date.today()


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
                args=(self._component_key, self),
                key=self._component_key + _SELECT_PERIOD_KEY,
            )
            self._begin_date_picker = st.date_input(
                "Begin Date",
                on_change=begin_date_picker_callback,
                args=(self._component_key, self),
                key=self._component_key + _BEGIN_DATE_PICKER_KEY,
            )
            self._end_date_picker = st.date_input(
                "End Date",
                on_change=end_date_picker_callback,
                args=(self._component_key, self),
                key=self._component_key + _END_DATE_PICKER_KEY,
            )

        # log exit from the function
        logger.debug("Exiting TimeMachineComponent render method")
        return component

def get_time_machine_component(key: str) -> TimeMachineComponent:
    """
    Returns a TimeMachineComponent for the given key. If a component doesn't exist,
    a new one is created.

    Arguments:
        key -- the key for the requested TimeMachineComponent

    Returns:
        A TimeMachineComponent instance
    """
    # log entry into the function
    logger.debug("In get_time_machine_component with key=%s", key)

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        _COMPONENT_INSTANCES[key] = TimeMachineComponent(key)

    # log exit from the function
    logger.debug("Exiting get_time_machine_component with key=%s", key)
    return _COMPONENT_INSTANCES[key]
