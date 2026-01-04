'''
exercise functions from core.obsidian module
'''
# import standard libraries
import sys

# adjust path for app imports from src directory
sys.path.append("src")

# import application modules
from core.obsidian import open_obsidian_file, new_obsidian_file, search_obsidian_notes

# constants
VAULT_NAME = "Stock Journal"
FILE_NAME = "2025-11-17 14-32-44"

# open an existing file in Obsidian
open_obsidian_file(VAULT_NAME, FILE_NAME)

# search for Obsidian notes related to a specific stock symbol
print(search_obsidian_notes(VAULT_NAME, "GDX"))
