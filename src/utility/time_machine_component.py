"""
Utility component to update selection when new options are added to a
Streamlit multiselect component.
"""
# Import standard libraries
from datetime import date, timedelta
from uuid import uuid4 as uuid

# Import 3rd party libraries
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# Import local modules
from . import Periods, get_period_dates, get_market_days_for_period
from . import market_is_open, calculate_begin_date, count_trading_days
from . import get_logger

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

# Dictionary to hold component instances
_COMPONENT_INSTANCES = {}

# Keys for the individual Streamlit widgets in the component
_SELECT_PERIOD_KEY = "_time_machine_select_period"
_BEGIN_DATE_PICKER_KEY = "_time_machine_begin_date_picker"
_END_DATE_PICKER_KEY = "_time_machine_end_date_picker"
_DECREMENT_BUTTON_KEY = "_time_machine_decrement_button"
_INCREMENT_DAYS_KEY = "_time_machine_increment_days"
_INCREMENT_BUTTON_KEY = "_time_machine_increment_button"

# Callback functions for Streamlit widgets
def _period_select_callback(key: str, instance):
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
    _logger.debug(
        "In function period_select_callback with key=%s", key)

    # update the period_selected property
    instance.period_selected = st.session_state[key]
    _logger.debug("period selected is: %s", instance.period_selected)


def _begin_date_picker_callback(key: str, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    _logger.debug("In function begin_date_picker_callback with key=%s", key)

    # update the begin_date property
    instance.begin_date = st.session_state[key]
    _logger.debug("begin date updated to %s", instance.begin_date)
    # update the period_selected widget to "Custom"
    instance.period_selected = Periods.CUS


def _end_date_picker_callback(key: str, instance):
    """
    responds to the on_change event for the _begin_date_picker date_input
    updates the begin_date property
    also updates the period_selected property to "Custom"

    Arguments:
        value -- the selected begin date from the date_input
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    _logger.debug("In function end_date_picker_callback with key=%s", key)

    # update the end_date property
    instance.end_date = st.session_state[key]
    _logger.debug("end date updated to %s", instance.end_date)
    # update the period_selected widget to "Custom"
    instance.period_selected = Periods.CUS


def _decrement_date_callback(_, instance):
    """
    responds to the on_click event for the decrement button
    decrements the end_date by the specified number of days
    also updates begin_date based on period_selected

    Arguments:
        key -- the key of the decrement button (not used)
        instance -- the TimeMachineComponent instance

    Returns:
        void
    """
    # log entry into the function
    _logger.debug("In function decrement_date_callback")

    # calculate the new end date
    new_end_date = instance.end_date - timedelta(days=instance.increment_days)

    # find the previous trading day if needed
    while not market_is_open(new_end_date):
        new_end_date -= timedelta(days=1)

    # update the end_date property
    instance.end_date = new_end_date
    _logger.debug("end date decremented to %s", instance.end_date)

    # check if period is Custom (CUS) - maintain trading day count
    if instance.period_selected == Periods.CUS:
        # calculate the number of trading days in current period
        trading_days = count_trading_days(instance.begin_date, instance.end_date)

        # recalculate begin_date based on the same number of trading days
        instance.begin_date = calculate_begin_date(instance.end_date, trading_days)
    else:
        # recalculate begin_date to maintain period length
        market_days = get_market_days_for_period(instance.period_selected)
        if market_days is not None:
            # recalculate begin_date based on the new end_date and period
            instance.begin_date = calculate_begin_date(instance.end_date, market_days)
        else:
            # for periods like YTD, YR1, ALL - use get_period_dates
            begin_date, _ = get_period_dates(instance.period_selected, to_date=instance.end_date)
            instance.begin_date = begin_date

def _increment_days_callback(key: str, instance):
    """
    responds to the on_change event for the increment_days number_input
    updates the increment_days property
    
    Arguments:
        key -- the key of the increment_days input field
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    _logger.debug("In function increment_days_callback with key=%s", key)

    # update the increment_days property
    instance.increment_days = st.session_state[key]
    _logger.debug("increment_days updated to %s", instance.increment_days)


def _increment_date_callback(_, instance):
    """
    responds to the on_click event for the increment button
    increments the end_date by the specified number of days
    also updates begin_date based on period_selected

    Arguments:
        key -- the key of the increment button (not used)
        instance -- the TimeMachineComponent instance
    """
    # log entry into the function
    _logger.debug("In function increment_date_callback")

    # check if period is Custom (CUS) - maintain trading day count
    if instance.period_selected == Periods.CUS:
        # calculate the number of trading days in current period
        trading_days = count_trading_days(instance.begin_date, instance.end_date)

        # calculate the new end date
        new_end_date = instance.end_date + timedelta(days=instance.increment_days)

        # find the next trading day if needed
        while not market_is_open(new_end_date):
            new_end_date += timedelta(days=1)

        # update the end_date property
        instance.end_date = new_end_date
        _logger.debug("end date incremented to %s", instance.end_date)

        # recalculate begin_date based on the same number of trading days
        instance.begin_date = calculate_begin_date(instance.end_date, trading_days)
    else:
        # calculate the new end date
        new_end_date = instance.end_date + timedelta(days=instance.increment_days)

        # find the next trading day if needed
        while not market_is_open(new_end_date):
            new_end_date += timedelta(days=1)

        # update the end_date property
        instance.end_date = new_end_date
        _logger.debug("end date incremented to %s", instance.end_date)

        # recalculate begin_date to maintain period length
        market_days = get_market_days_for_period(instance.period_selected)
        if market_days is not None:
            # recalculate begin_date based on the new end_date and period
            instance.begin_date = calculate_begin_date(instance.end_date, market_days)
        else:
            # for periods like YTD, YR1, ALL - use get_period_dates
            begin_date, _ = get_period_dates(instance.period_selected, to_date=instance.end_date)
            instance.begin_date = begin_date

class TimeMachineComponent:
    """
    Implements a composite component to select and mangage time period selection
    """
    # class properties
    @property
    def period_selected(self) -> Periods:
        """
        Returns the value of the currently selected period
        """
        _logger.debug("In period_selected getter for key=%s, returning period_selected=%s",
                        self._component_key, self._period_selected)
        return self._period_selected
    @period_selected.setter
    def period_selected(self, value: Periods):
        """
        Sets the value of the currently selected period
        """
        _logger.debug("In period_selected setter for key=%s, setting period_selected to %s",
                        self._component_key, value)
        self._period_selected = value
        # update the period_selected widget
        st.session_state[self._select_period_key] = value

        # do we need to calculate the period?
        if value != Periods.CUS:
            # calculate the dates for the selected option and update the instance properties
            self.begin_date, self.end_date = get_period_dates(value, self.end_date)

    @property
    def begin_date(self) -> date:
        """
        Returns the value of the begin date
        """
        _logger.debug("In begin_date getter for key=%s, returning begin_date=%s",
                        self._component_key, self._begin_date)
        return self._begin_date
    @begin_date.setter
    def begin_date(self, value: date):
        """
        Sets the value of the begin date
        """
        self._begin_date = value
        _logger.debug("In begin_date setter for key=%s, setting begin_date to %s",
                        self._component_key, value)
        # update the begin date picker to reflect the new date
        st.session_state[self._begin_date_picker_key] = value

    @property
    def end_date(self) -> date:
        """
        Returns the value of the end date
        """
        _logger.debug("In end_date getter for key=%s, returning end_date=%s",
                        self._component_key, self._end_date)
        return self._end_date
    @end_date.setter
    def end_date(self, value: date):
        """
        Sets the value of the end date
        """
        _logger.debug("In end_date setter for key=%s, setting end_date to %s",
                        self._component_key, value)
        self._end_date = value
        # update the end date picker to reflect the new date
        st.session_state[self._end_date_picker_key] = value

    @property
    def increment_days(self) -> int:
        """
        Returns the value of the increment days input field
        """
        _logger.debug("In increment_days getter for key=%s, returning increment_days=%s",
                        self._component_key, st.session_state.get(self._increment_days_key, 1))
        return st.session_state.get(self._increment_days_key, 1)

    @increment_days.setter
    def increment_days(self, value: int):
        """
        Sets the value of the increment days input field
        """
        _logger.debug("In increment_days setter for key=%s, setting increment_days to %s",
                        self._component_key, value)
        # update the instance variable
        st.session_state[self._increment_days_key] = value

    class _TimeMachineComponentLayout():
        """
        Layout the widgets for the time machine component
        """
        def __init__(self, parent: DeltaGenerator):
            """
            Initialize the time machine component layout

            Arguments:
                parent -- The parent container for the time machine component widgets
            """
            with parent:
                self.period_selector = st.empty()
                self.begin_date_picker = st.empty()
                self.end_date_picker = st.empty()
                self.increment_controls = st.container(border=True)

    def __init__(self, component_key: str, period: Periods, end_date: date|None):
        """
        Initializes the TimeMachineComponent instance
        """
        # log entry into the function
        _logger.debug("In TimeMachineComponent constructor with component_key=%s, period=%s",
                     component_key,
                     period)

        # store the component key
        self._component_key = component_key

        # initialize date picker keys
        self._select_period_key = component_key + _SELECT_PERIOD_KEY
        self._begin_date_picker_key = component_key + _BEGIN_DATE_PICKER_KEY
        self._end_date_picker_key = component_key + _END_DATE_PICKER_KEY

        # initialize increment controls keys
        self._decrement_button_key = component_key + _DECREMENT_BUTTON_KEY
        self._increment_days_key = component_key + _INCREMENT_DAYS_KEY
        self._increment_button_key = component_key + _INCREMENT_BUTTON_KEY

        # initialize the period_selected and end_date to the provided value
        # NOTE: this will also calculate the begin date for the selected period
        if end_date is not None:
            self.end_date = end_date
        self.period_selected = period

        # define the time machine component layout
        self._component_layout: TimeMachineComponent._TimeMachineComponentLayout

        # define instance variables to hold Streamlit widgets
        self._period_selector: DeltaGenerator|None
        self._begin_date_picker: DeltaGenerator
        self._end_date_picker: DeltaGenerator


    def update_date_pickers(self, begin_date: date, end_date: date):
        """
        Update the date picker widgets to the specified dates

        Arguments:
            begin_date -- the date for the begin_date_picker
            end_date -- the date for the end_date_picker
        """
        # mark entry into the function
        _logger.debug(
                    "entering function update_date_pickers "
                    "with begin_date %s and end_date %s",
                     begin_date, end_date)

        # delete the old picker widgets, if neccesary
        if self._begin_date_picker_key is not None:
            try:
                del st.session_state[self._begin_date_picker_key]
            except KeyError:
                # don't care if it's already gone
                pass

        if self._end_date_picker_key is not None:
            try:
                del st.session_state[self._end_date_picker_key]
            except KeyError:
                # don't care if it's already gone
                pass

        # calculate the keys for the date_picker widgets
        uniquifier = f"_{str(uuid())}"
        self._begin_date_picker_key = self._component_key + _BEGIN_DATE_PICKER_KEY + uniquifier
        self._end_date_picker_key = self._component_key + _END_DATE_PICKER_KEY + uniquifier

        # render the date picker widgets
        with self._component_layout.begin_date_picker:
            st.date_input(
                        "Begin Date",
                        value=begin_date,
                        on_change=_begin_date_picker_callback,
                        args=(self._begin_date_picker_key, self),
                        key=self._begin_date_picker_key
                    )
        with self._component_layout.end_date_picker:
            st.date_input(
                        "End Date",
                        value=end_date,
                        on_change=_end_date_picker_callback,
                        args=(self._end_date_picker_key, self),
                        key=self._end_date_picker_key
                        )


    def render(self):
        """
        Renders the TimeMachineComponent instance
        """
        # log entry into the function
        _logger.debug("In TimeMachineComponent render method")

        # create the layout box to hold the component
        self._component_layout = TimeMachineComponent._TimeMachineComponentLayout(
                                                                 st.container(border=True)
                                                                 )

        # render the period selector widget
        with self._component_layout.period_selector:
            self._period_selector = st.selectbox(
                "Period",
                options=Periods.get_periods(),
                format_func=Periods.get_label,
                placeholder="Select Period",
                index=Periods.get_periods().index(self.period_selected),
                on_change=_period_select_callback,
                args=(self._select_period_key, self),
                key=self._select_period_key
            )

        # update the date picker widgets with current data
        self.update_date_pickers(self._begin_date, self._end_date)

        # render the increment/decrement controls
        with self._component_layout.increment_controls:
            cols = st.columns([1, 2, 1], gap="small")
            with cols[0]:
                st.button("", icon=":material/arrow_back_ios:",
                        key=self._decrement_button_key,
                        on_click=_decrement_date_callback,
                        args=(self._decrement_button_key, self)
                        )
            with cols[1]:
                with st.container():
                    # with st.container(height=20,vertical_alignment="bottom"):
                    st.slider("",
                            label_visibility="collapsed",
                            min_value=1,
                            max_value=180,
                            value=1,
                            key=self._increment_days_key,
                            on_change=_increment_days_callback,
                            args=(self._increment_days_key, self)
                            )
                    st.html(
                        "<p style='text-align: center; padding: 0px;margin: 0px;'>Days +/-</p>"
                        )
            with cols[2]:
                st.button("", icon=":material/arrow_forward_ios:",
                        key=self._increment_button_key,
                        on_click=_increment_date_callback,
                        args=(self._increment_button_key, self)
                        )

        # log exit from the function
        _logger.debug("Exiting TimeMachineComponent render method")

def get_time_machine_component(
        key: str,
        period: Periods = Periods.NONE,
        end_date: date|None = date.today()) -> TimeMachineComponent:
    """
    Returns a TimeMachineComponent for the given key. If a component doesn't exist,
    a new one is created.

    Arguments:
        key -- the key for the requested TimeMachineComponent

    Returns:
        A TimeMachineComponent instance
    """
    # log entry into the function
    _logger.debug("In get_time_machine_component with key=%s, period=%s, end_date=%s",
                        key, period, end_date)

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        _COMPONENT_INSTANCES[key] = TimeMachineComponent(key, period, end_date)

    # log exit from the function
    _logger.debug("Exiting get_time_machine_component with key=%s", key)
    return _COMPONENT_INSTANCES[key]
