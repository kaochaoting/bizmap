#!/usr/bin/env python3
"""Split one oversized business JSON into a small manifest and safe-sized parts."""

import argparse
import json
import math
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "static" / "data"
TARGET_BYTES = 18 * 1024 * 1024
PAGES_MAX_BYTES = 25 * 1024 * 1024


def write_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path relative to static/data")
    args = parser.parse_args()

    source = (DATA_DIR / args.file).resolve()
    if DATA_DIR.resolve() not in source.parents or not source.is_file():
        raise SystemExit("File must exist under static/data")

    data = json.loads(source.read_text(encoding="utf-8"))
    businesses = data.get("businesses")
    if not isinstance(businesses, list) or not businesses:
        raise SystemExit("Expected a non-empty businesses array")

    part_dir = source.with_suffix("")
    if part_dir.exists() and any(part_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty directory: {part_dir}")
    part_dir.mkdir(parents=True, exist_ok=True)

    part_count = max(2, math.ceil(source.stat().st_size / TARGET_BYTES))
    chunk_size = math.ceil(len(businesses) / part_count)
    part_names = []

    for index, start in enumerate(range(0, len(businesses), chunk_size), 1):
        chunk = businesses[start:start + chunk_size]
        part_name = f"part{index}.json"
        part = {**data, "count": len(chunk), "businesses": chunk}
        write_json(part_dir / part_name, part)
        if (part_dir / part_name).stat().st_size > PAGES_MAX_BYTES:
            raise SystemExit(f"Generated part still exceeds 25 MiB: {part_name}")
        part_names.append(part_name)

    manifest = {key: value for key, value in data.items() if key != "businesses"}
    manifest.update({"count": len(businesses), "files": part_names, "businesses": []})
    write_json(source, manifest)
    print(f"Split {args.file}: {len(businesses)} businesses into {len(part_names)} parts")


if __name__ == "__main__":
    main()
