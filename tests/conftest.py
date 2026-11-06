"""
Pytest configuration for the test suite.

``test_obsidian.py`` is a manual smoke script (it has no ``def test_*`` functions
and makes live network calls on import), so it is excluded from collection. It
will be reworked separately; until then pytest must not try to import it.
"""
collect_ignore = ["test_obsidian.py"]
