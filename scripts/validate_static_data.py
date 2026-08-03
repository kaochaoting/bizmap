#!/usr/bin/env python3
"""Validate every data file reachable from static/data/index.json."""

import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "static" / "data"
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"
PAGES_MAX_BYTES = 25 * 1024 * 1024


def load_json(relative_path):
    path = DATA_DIR / relative_path
    if not path.is_file():
        raise AssertionError(f"Missing data file: {relative_path}")

    with path.open("rb") as file:
        if file.read(len(LFS_HEADER)) == LFS_HEADER:
            raise AssertionError(f"Unresolved Git LFS pointer: {relative_path}")

    with path.open(encoding="utf-8") as file:
        return json.load(file)


for path in DATA_DIR.rglob("*.json"):
    relative_path = path.relative_to(DATA_DIR)
    assert path.stat().st_size <= PAGES_MAX_BYTES, f"File exceeds Cloudflare Pages 25 MiB limit: {relative_path}"
    with path.open("rb") as file:
        assert file.read(len(LFS_HEADER)) != LFS_HEADER, f"Unresolved Git LFS pointer: {relative_path}"


index = load_json("index.json")
assert index["total"] == sum(index["category_counts"].values()), "Index totals do not match"

validated = {"index.json"}
for entries in index["files"].values():
    for entry in entries:
        relative_path = entry["file"]
        data = load_json(relative_path)
        validated.add(relative_path)

        child_businesses = 0
        for child in data.get("files", []):
            child_path = f"{relative_path.removesuffix('.json')}/{child}"
            child_data = load_json(child_path)
            child_businesses += len(child_data.get("businesses", []))
            validated.add(child_path)

        if data.get("files"):
            assert child_businesses == data["count"], f"Child counts do not match: {relative_path}"
        elif "businesses" in data:
            assert len(data["businesses"]) == data["count"], f"Business count does not match: {relative_path}"

print(f"Validated {len(validated)} static data files.")
