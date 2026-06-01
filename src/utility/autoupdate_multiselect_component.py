"""
Utility component to update selection when new options are added to a
Streamlit multiselect component.
"""
# Import standard libraries
from uuid import uuid4 as uuid

# Import 3rd party libraries
import streamlit as st

# Import local modules
from . import get_logger

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

# Dictionary to hold component instances
_COMPONENT_INSTANCES = {}


def option_multiselect_callback(selected_input, instance):
    """
    on_change callback to update the selected options in the
    AutoUpdateMultiselectComponent instance.
    """
    _logger.debug("in option_multiselect_callback, input=%s", selected_input)
    # convert all strings to upper case and store in instance
    instance.selected = [s.upper() for s in st.session_state[selected_input].copy()]


class AutoUpdateMultiselectComponent:
    """
    Implements a utility component to update selection when new options
    are added to a Streamlit multiselect component. It maintains a list of
    previously selected options and automatically includes any new options
    """

    @property
    def selected(self):
        """
        Returns the value of the currently selected list from the multi-select
        component
        """
        return self._selected.copy()

    @selected.setter
    def selected(self, value: list[str]):
        self._selected = value


    def __init__(self,
                key: str,
                label: str,
                options: list[str],
                default: list[str]|None = None,
                accept_new_options: bool = False,
                placeholder: str|None = None,
                ):
        """
        Configures a new instance of AutoUpdateMultiselectComponent.

        Args:
            key (str): Unique key to identify the component instance.
            label (str): The label for the multiselect component.
            options (list[str]): The list of options to display.
            default (list[str]): The default selected options.
            accept_new_options (bool): Whether or not to accept user input to add
                new options (default False)
            placeholder (str): Default text to display in the selectbox when not selected
        """
        _logger.debug(
            "Configuring AutoUpdateMultiselectComponent instance: key=%s\n" +
            "label=%s\noptions=%s\ndefault=%s\naccept_new_options=%s\nplaceholder=%s",
            key,
            label,
            options,
            default,
            accept_new_options,
            placeholder,
            )

        #initialize instance variables
        self._key = key
        self._label = label
        self._options = options
        self._default = default
        self._accept_new_options = accept_new_options
        self._placeholder = placeholder

        # initialize widgets
        self.widget_placeholder = st.empty()

        # initialize working variables
        self._selected = []
        self._widget_id = str()

    def render(self, default: list[str]|None = None):
        """
        Renders a Streamlit multiselect component that automatically updates
        its selection when new options are added.

        Args:
            default (list[str]): The default selected options.
                (Defaults to previously used)

        Returns:
            st.multiselect: A Streamlit Multiselect component with auto-updating selection.
        """
        # mark debug entry into the method
        _logger.debug("Entering AutoUpdateMultiselectComponent.render")

        # create an empty widget to eventually hold the selectbox
        self.widget_placeholder = st.empty()

        # Update default selections
        if default is  None:
            # use previously selected options
            self._default = self._selected
        else:
            # use provided default options
            self._default = default
            self._selected = default

        # Create the multiselect component
        self._widget_id = self._key + "_" + str(uuid())
        with self.widget_placeholder:
            st.multiselect(
                self._label,
                options=self._options,
                default=self._default,
                accept_new_options=self._accept_new_options,
                placeholder=self._placeholder,
                on_change=option_multiselect_callback,
                args=(self._widget_id, self),
                key=self._widget_id
            )

    def update_options(self, new_options: list[str]):
        """
        Update the list of options for the multiselect widget

        Arguments:
            new_options -- A list of strings to update the options
        """
        # mark debug entry into the method
        _logger.debug("Entering AutoUpdateMultiselectComponent.update_options with new options: %s",
                     new_options,
                     )
        # Update default selections
        self._default = new_options
        self._selected = new_options

        # Include any new options in the provided default that were not previously selected
        # Add the new options to the allowable options list
        for option in self._default:
            if option not in self._options:
                self._options.append(option)
        # Keep the options sorted alphabetically
        self._options.sort()

        # Swap out the current multiselect widget, if necessary
        if self._widget_id in st.session_state:
            del st.session_state[self._widget_id]
        self._widget_id = self._key + "_" + str(uuid())

        # Create the multiselect component
        with self.widget_placeholder:
            st.multiselect(
                self._label,
                options=self._options,
                default=self._default,
                accept_new_options=self._accept_new_options,
                placeholder=self._placeholder,
                on_change=option_multiselect_callback,
                args=(self._widget_id, self),
                key=self._widget_id
            )


def get_aumc_instance(key: str,
                        label: str,
                        options: list[str],
                        default: list[str]|None = None,
                        accept_new_options: bool = False,
                        placeholder: str|None = None,
                        ) -> AutoUpdateMultiselectComponent:
    """
    Retrieves an existing instance of AutoUpdateMultiselectComponent
    or creates a new one if it doesn't exist.

    Args:
        key (str): Unique key to identify the component instance.
        label (str): The label for the multiselect component.
        options (list[str]): The list of options to display.
        default (list[str]): The default selected options.
        accept_new_options (bool): Whether or not to accept user input to add
            new options (default False)
        placeholder (str): Default text to display in the selectbox when not selected
    """
    # log entry into the function
    _logger.debug(
        "In aumc_get_instance with parameters: key=%s\n" +
        "label=%s\noptions=%s\ndefault=%s\naccept_new_options=%s\nplaceholder=%s",
        key,
        label,
        options,
        default,
        accept_new_options,
        placeholder,
        )

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        _logger.debug("Creating new component")
        _COMPONENT_INSTANCES[key] = AutoUpdateMultiselectComponent(key,
            label,
            options,
            default,
            accept_new_options,
            placeholder,
            )

    # log exit from the function
    _logger.debug("Exiting aumc_get_instance with key=%s", key)
    return _COMPONENT_INSTANCES[key]
