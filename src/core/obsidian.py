"""
Routines to query notes from the "Stock Journal" vault in obsidian.
Uses the "Local REST API" plugin in Obsidian.
"""

### standard library imports
import webbrowser
from urllib.parse import urlencode
from io import StringIO

### third-party imports
import httpx
import pandas as pd

### local imports
from config import LOGGER

def _create_obsidian_url(vault: str, filename: str, action: str) -> str:
    """
    Given a filename from the Obsidian vault, generate a URL to access the file
    in the Obsidian app. The URL has the following format and must be encoded properly:
    obsidian://open?vault={vault}&file={filename}
    obsidian://open?vault=Stock%20Journal&file=2025-11-17%2014-32-44

    :param vault: The name of the Obsidian vault.
    :param filename: The name of the file in the Obsidian vault.
    :return: The URL to access the file in Obsidian.
    """
    LOGGER.debug(
        "Creating Obsidian URL for vault: %s, filename: %s, action: %s", vault, filename, action
        )
    base_url = f"obsidian://{action}?"
    query_params = {
        "vault": vault,
        "file": filename
    }
    encoded_params = (urlencode(query_params)).replace('+', '%20')
    full_url = f"{base_url}{encoded_params}"
    LOGGER.debug("Generated Obsidian URL: %s", full_url)
    return full_url


def open_obsidian_file(vault: str, filename: str) -> None:
    """
    Opens the specified file in the Obsidian app using the Local REST API plugin.

    :param vault: The name of the Obsidian vault.
    :param filename: The name of the file in the Obsidian vault.
    """
    LOGGER.debug("Opening Obsidian file: %s in vault: %s", filename, vault)
    api_url = _create_obsidian_url(vault, filename, "open")
    LOGGER.debug("Opening Obsidian URL: %s", api_url)
    webbrowser.open(api_url)


def new_obsidian_file(vault: str, filename: str, content: str|None) -> None:
    """
    Creates the specified file in the Obsidian app using the Local REST API plugin,
    optionally with initial content. The new note will be opened in Obsidian.

    Arguments:
        vault: The name of the Obsidian vault.
        filename: The name of the file to be created in the Obsidian vault.
        content: The initial content to be added to the new file. (Optional)

    Returns:
        None
    """
    LOGGER.debug("Creating new Obsidian file: %s in vault: %s", filename, vault)
    api_url = _create_obsidian_url(vault, filename, "new")
    if content:
        api_url += f"&{urlencode({"content": content}).replace('+', '%20')}"
    LOGGER.debug("Creating Obsidian URL: %s", api_url)
    webbrowser.open(api_url)


def search_obsidian_notes(vault: str, symbol:str) -> pd.DataFrame:
    """
    Get a list of notes from the specified Obsidian vault that have either the "symbol"
    property or a tag matching the input symbol.

    Arguments:
        vault -- The name of the Obsidian vault to query.
        symbol -- The stock symbol to filter notes by.

    Returns:
        A DataFrame containing the notes that match the criteria. The DataFrame includes
        columns for the note filename, symbol, and date entered, and is indexed by the
        date entered.
    """
    LOGGER.debug("Searching Obsidian notes in vault: %s for symbol/tag: %s", vault, symbol)
    # Set the base URL for the Obsidian search function
    url_base = 'http://127.0.0.1:27123/search'
    # Define the DQL query to search for notes with the specified symbol or tag
    dql = (f'TABLE symbol,entered,file.tags WHERE symbol="{symbol}"'
           f'or contains(file.tags, "{symbol}")'
        )
    LOGGER.debug("DQL Query: %s", dql)

    try:
        response = httpx.post(
            url=url_base,
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/vnd.olrapi.dataview.dql+txt',
                'Authorization':
                    'Bearer bffbdddf086ad4c30b6af07fdb575e3ec42da39351f8c6f9f26d3c9a19ca1612'
                },
            content=dql,
        )
    except httpx.RequestError as exc:
        LOGGER.error("An error occurred while requesting %s: ", exc.request.url)
        raise
    LOGGER.debug("Obsidian search API Response: %s", response)
    if response.text == '[]':
        df = pd.DataFrame()  # Return empty DataFrame if no results found
    else:
        df = pd.read_json(StringIO(response.text)) # Convert JSON response to DataFrame

    LOGGER.debug("Raw DataFrame from Obsidian search API: %s", df)
    return df
