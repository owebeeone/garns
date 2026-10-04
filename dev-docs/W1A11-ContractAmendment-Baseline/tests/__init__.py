"""Test suite for the promoted Garns semantic baseline.

Importing the package puts the repository's ``src`` directory and root on
``sys.path`` so the suite runs without an install step:

    uv run --offline --with lark python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]

for entry in (str(BUILD / "src"), str(BUILD)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
