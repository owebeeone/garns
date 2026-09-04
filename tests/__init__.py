"""Test suite for the B2 implementation of Garns v9-5.

Importing the package puts ``build/B2/src`` (the implementation) and
``build/B2`` (this package's parent) on ``sys.path`` so the suite runs from the
build root without an install step:

    uv run --offline --with lark python -m unittest discover -s tests -t .
"""

from __future__ import annotations

import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]

for entry in (str(BUILD / "src"), str(BUILD)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
