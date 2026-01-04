'''
exercise functions from core.obsidian module
'''
# import standard libraries
import sys
from datetime import datetime as dt

# adjust path for app imports from src directory
sys.path.append("src")

# import application modules
#pylint: disable=wrong-import-position
from config import LOGGER
from core.obsidian import open_obsidian_file, new_obsidian_file, search_obsidian_notes

LOGGER.info("Starting Obsidian module test script at %s", dt.now().isoformat())
# constants
VAULT_NAME = "Stock Journal"
FILE_NAME = "TEST"
CONTENT = """---
symbol: GDX
phase: TEST
entered: "{{date}} {{time}}"
---

***Symbol:***  `INPUT[text:symbol]`

***Phase:***  `INPUT[inlineSelect(
	option(Pre-Trade),
	option(Post-Trade),
	option(Note)
	):phase]`

***Entered:***  `VIEW[{entered}]`
***Earnings Date:***

### Chart:


### Strategy:


### Fundamental Analysis:


### Technical Analysis:


### Psychology:


### Notes:
"""

# create a new file in Obsidian
new_obsidian_file(VAULT_NAME, FILE_NAME, CONTENT)

# open an existing file in Obsidian
open_obsidian_file(VAULT_NAME, FILE_NAME)

# search for Obsidian notes related to a specific stock symbol
print(search_obsidian_notes(VAULT_NAME, "GDX"))
