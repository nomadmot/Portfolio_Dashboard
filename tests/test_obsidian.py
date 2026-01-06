'''
exercise functions from core.obsidian module
'''
# import standard libraries
import sys
import logging
from datetime import datetime as dt

# adjust path for app imports from src directory
sys.path.append("src")

# import application modules
#pylint: disable=wrong-import-position
from core import(
    open_obsidian_file,
    new_obsidian_file,
    get_obsidian_file,
    search_obsidian_notes,
)
from config import LOGGER

# configure a standard logger for the test script
logging.basicConfig(
	level=logging.DEBUG,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
	)
LOGGER = logging.getLogger("test_obsidian")
LOGGER.info("Starting Obsidian module test script at %s", dt.now().isoformat())

# constants
VAULT_NAME = "Stock Journal"
TEMPLATE_NAME = "templates/stock note.md"
FILE_NAME = "TEST.md"
CONTENT = """---
symbol: TEST
---
This is a test note created by the Obsidian module test script.
"""


# search for Obsidian notes related to a specific stock symbol
print("Searching for Obsidian notes related to 'GDX':")
print(search_obsidian_notes("GDX"))

#get the content of a specific Obsidian file
template = get_obsidian_file(TEMPLATE_NAME)
print("Retrieved template content:")
print(template)

# create a new file in Obsidian using the retrieved template content
new_obsidian_file(VAULT_NAME, FILE_NAME, template)

# open an existing file in Obsidian
open_obsidian_file(VAULT_NAME, FILE_NAME)
