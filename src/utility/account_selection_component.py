"""
Utility component to select one or more portfolio accounts in a
Streamlit sidebar, displaying account names.
"""
# Import 3rd party libraries
import streamlit as st

# Import local modules
from schemas.portfolio import Account
from . import get_logger

# mark entry into the module
_logger = get_logger(__name__)
_logger.debug("In module %s", __name__)

# Dictionary to hold component instances
_COMPONENT_INSTANCES = {}


class AccountSelectionComponent:
    """
    Implements a utility component for selecting one or more portfolio
    accounts. The widget displays account names and reports selections
    as account IDs. The options list is fixed for the lifetime of the
    application; the selection persists in session state across runs.
    """

    @property
    def selected(self):
        """
        Returns the currently selected account ID(s): a single int (or
        None) for single-selection, or a list of ints for multi-selection.
        """
        if not self._labels:
            return [] if self._allow_multiple else None
        if self._widget_key in st.session_state:
            raw = st.session_state[self._widget_key]
        else:
            # the widget has not rendered yet; fall back to the defaults
            raw = self._default_labels
        if self._allow_multiple:
            return [self._label_to_id[label] for label in raw]
        # the selectbox stores a scalar label; the fallback is a one-item list
        if isinstance(raw, (list, tuple)):
            raw = raw[0] if raw else None
            return self._label_to_id[raw] if raw is not None else None
        return self._label_to_id[raw]

    @property
    def allow_multiple(self) -> bool:
        """Whether multiple accounts may be selected."""
        return self._allow_multiple

    def __init__(self,
                 key: str,
                 label: str,
                 options: list[Account],
                 allow_multiple: bool = False,
                 ):
        """
        Configures a new instance of AccountSelectionComponent.

        Args:
            key (str): Unique key to identify the component instance.
            label (str): The label for the selection widget.
            options (list[Account]): The accounts to offer for selection.
            allow_multiple (bool): Whether or not multiple selections are
                allowed (default False, single-selection only).
        """
        _logger.debug(
            "Configuring AccountSelectionComponent instance: key=%s\n" +
            "label=%s\noptions=%s\nallow_multiple=%s",
            key,
            label,
            options,
            allow_multiple,
            )

        # initialize instance variables
        self._key = key
        self._label = label
        self._allow_multiple = allow_multiple
        self._widget_key = f"{key}_select"

        # build the display labels, disambiguating duplicate names with the ID
        name_counts = {}
        for account in options:
            name_counts[account.account_name] = \
                name_counts.get(account.account_name, 0) + 1

        self._labels = []
        self._label_to_id = {}
        self._id_to_label = {}
        for account in options:
            name = account.account_name
            display = f"{name} ({account.account_id})" \
                if name_counts[name] > 1 else name
            self._labels.append(display)
            self._label_to_id[display] = account.account_id
            self._id_to_label[account.account_id] = display

        # default to account 1 if present, otherwise the first option
        default_id = 1 if 1 in self._id_to_label \
            else (options[0].account_id if options else None)
        self._default_labels = [self._id_to_label[default_id]] \
            if default_id is not None else []
        self._default_index = self._labels.index(self._default_labels[0]) \
            if self._default_labels else 0

    def render(self):
        """
        Renders the account selection widget. Safe to call on every run;
        the selection is preserved in session state across runs.
        """
        # mark debug entry into the method
        _logger.debug("Entering AccountSelectionComponent.render")

        if not self._labels:
            st.caption("No accounts available.")
            return

        if self._allow_multiple:
            st.multiselect(
                self._label,
                options=self._labels,
                default=self._default_labels,
                key=self._widget_key,
                )
        else:
            st.selectbox(
                self._label,
                options=self._labels,
                index=self._default_index,
                key=self._widget_key,
                )


def get_account_selection_component(key: str,
                                    label: str,
                                    options: list[Account],
                                    allow_multiple: bool = False,
                                    ) -> AccountSelectionComponent:
    """
    Retrieves an existing AccountSelectionComponent for the given key or
    creates a new one if it doesn't exist.

    Args:
        key (str): Unique key to identify the component instance.
        label (str): The label for the selection widget.
        options (list[Account]): The accounts to offer for selection.
        allow_multiple (bool): Whether or not multiple selections are
            allowed (default False, single-selection only).
    """
    # log entry into the function
    _logger.debug(
        "In get_account_selection_component with parameters: key=%s\n" +
        "label=%s\noptions=%s\nallow_multiple=%s",
        key,
        label,
        options,
        allow_multiple,
        )

    # check if the component already exists
    if key not in _COMPONENT_INSTANCES:
        # create a new component and store it in the dictionary
        _logger.debug("Creating new component")
        _COMPONENT_INSTANCES[key] = AccountSelectionComponent(
            key,
            label,
            options,
            allow_multiple,
            )

    # log exit from the function
    _logger.debug("Exiting get_account_selection_component with key=%s", key)
    return _COMPONENT_INSTANCES[key]
