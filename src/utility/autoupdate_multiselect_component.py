"""
Utility component to update selection when new options are added to a
Streamlit multiselect component.
"""
# Import standard libraries
from typing import Any
import logging
from uuid import uuid4 as uuid

# Import 3rd party libraries
import streamlit as st

# Import local modules
import models.settings as settings

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOGLEVEL_APPLICATION)

# Dictionary to hold component instances
_AUMC_INSTANCES = dict()


def option_multiselect_callback(selected_input, instance):
    """
    on_change callback to update the selected options in the
    AutoUpdateMultiselectComponent instance.
    """
    logger.debug("in option_multiselect_callback, input=%s", selected_input)
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

    @property
    def is_initialized(self):
        """
        (Read-only) Indicates whether the component instance has been initialized.
        """
        return self._isinitialized


    def __init__(self,
                key: str,
                ):
        """
        Initializes the AutoUpdateMultiselectComponent with a unique key.

        Args:
            key (str): Unique key to identify the component instance.
        """
        logger.debug(("Entering AutoUpdateMultiselectComponent.__init__: ",
                      "key=%s"), key)
        self._key = key
        self._widget_id = str()
        self._label = str()
        self._options = list()
        self._default = list()
        self._selected = list()
        self._accept_new_options: bool= False
        self._placeholder: str|None = None
        self._isinitialized = False


    def configure_instance(self,
                            key: str,
                            label: str,
                            options: list[str],
                            default: list[str]|None = None,
                            accept_new_options: bool = False,
                            placeholder: str|None = None,
                            ) -> None:
        """
        Configures a new instance of AutoUpdateMultiselectComponent.

        Args:
            key (str): Unique key to identify the component instance.
            label (str): The label for the multiselect component.
            options (list[str]): The list of options to display.
            default (list[str]): The default selected options.
        """
        logger.debug("Configuring existing AutoUpdateMultiselectComponent instance for key=%s", key)

        self._key = key
        self._label = label
        self._options = options.copy()
        if default is None:
            self._default = list()
        else:
            self._default = default.copy()
        self._accept_new_options = accept_new_options
        self._placeholder = placeholder
        self._isinitialized = True

    def multiselect(self, default: list[str]|None = None) -> Any:
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
        logger.debug("Entering AutoUpdateMultiselectComponent.multiselect")

        # Update default selections
        if default is  None:
            # use previously selected options
            self._default = self._selected
        else:
            # use provided default options
            self._default = default
            self._selected = default

        # Include any new options in the provided defaultthat were not previously selected
        # Add the new options to the allowable options list
        for option in self._default:
            if option not in self._options:
                self._options.append(option)

        # Swap out the current multiselect widget, if necessary
        if self._widget_id in st.session_state:
            st.session_state[self._widget_id].clear()
        self._widget_id = self._key + "_" + str(uuid())

        # Create the multiselect component
        selector = st.multiselect(
            self._label,
            options=self._options,
            default=self._default,
            accept_new_options=self._accept_new_options,
            placeholder=self._placeholder,
            on_change=option_multiselect_callback,
            args=(self._widget_id, self),
            key=self._widget_id
        )

        return selector


def aumc_get_instance(key: str) -> AutoUpdateMultiselectComponent:
    """
    Retrieves an existing instance of AutoUpdateMultiselectComponent
    or creates a new one if it doesn't exist.

    Args:
        key (str): Unique key to identify the component instance.
    Returns:
        AutoUpdateMultiselectComponent: The component instance if it exists, otherwise
        a new, unintialized instance is created and returned.
    """
    if key not in _AUMC_INSTANCES:
        _ = AutoUpdateMultiselectComponent(key=key)
        _AUMC_INSTANCES[key] = _
        return _
    else:
        return _AUMC_INSTANCES[key]
