#!/usr/bin/env python3
"""Fail when Twinkle helper scripts contain a hard-coded API key."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGETS = (
    ROOT / "scan_all_datasets.py",
    ROOT / "search_datasets.py",
    ROOT / "search_missing_categories.py",
)
HARDCODED_KEY = re.compile(r"KEY\s*=\s*['\"]" + "".join(("s", "k", "-")))

for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    assert "TWINKLE_API_KEY" in text, f"{path.name}: TWINKLE_API_KEY is not used"
    assert not HARDCODED_KEY.search(text), f"{path.name}: hard-coded API key found"

print("Twinkle credential check passed.")
