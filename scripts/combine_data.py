"""Combine the country data files into one JSONL file.

Each line is one record. Every record has the union of all input columns,
in order of first appearance, plus `source_file`, which names the file the
record came from. Columns a file does not have are empty strings. The list
columns, stored as JSON arrays in the CSVs, become real lists; an empty cell
becomes []. All other text is copied unchanged.

    python3 scripts/combine_data.py
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUTS = [
    "data/kenya/af-scam-ke-v0.1.csv",
    "data/nigeria/af-scam-ng-screenshots-v0.1.csv",
    "data/nigeria/af-scam-ng-contributor-R-F8JM-W6U-v0.1.csv",
]
LIST_COLUMNS = ["tactics", "requested_action", "risk_indicators", "language_tags"]
OUTPUT = "data/afriscam-v0.1.jsonl"


def read_rows(relative_path):
    with open(ROOT / relative_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def parse_list(oid, column, value):
    if not value.strip():
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"{oid}: {column} is not a JSON array")
    return parsed


def combine(inputs):
    columns, rows, seen = [], [], set()
    for path in inputs:
        header, file_rows = read_rows(path)
        columns += [c for c in header if c not in columns]
        for row in file_rows:
            oid = row["observation_id"]
            if oid in seen:
                raise ValueError(f"{oid} appears in more than one file")
            seen.add(oid)
            rows.append((path, row))
    return columns + ["source_file"], rows


def to_record(columns, path, row):
    record = {c: row.get(c, "") for c in columns}
    record["source_file"] = path
    for column in LIST_COLUMNS:
        record[column] = parse_list(row["observation_id"], column, record[column])
    return record


def main():
    try:
        columns, rows = combine(INPUTS)
        records = [to_record(columns, path, row) for path, row in rows]
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Not combined: {e}", file=sys.stderr)
        return 1
    lines = [json.dumps(r, ensure_ascii=False) + "\n" for r in records]
    (ROOT / OUTPUT).write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {len(records)} records and {len(columns)} columns to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
