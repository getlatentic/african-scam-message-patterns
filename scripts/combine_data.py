"""Combine the country data files into one CSV.

Columns are the union of all input columns, in order of first appearance,
plus `source_file`, which names the file each record came from. Columns a
file does not have are left empty. Record text is copied unchanged.

    python3 scripts/combine_data.py
"""

import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUTS = [
    "data/kenya/af-scam-ke-v0.1.csv",
    "data/nigeria/af-scam-ng-screenshots-v0.1.csv",
    "data/nigeria/af-scam-ng-contributor-R-F8JM-W6U-v0.1.csv",
]
OUTPUT = "data/af-scam-combined-v0.1.csv"


def read_rows(relative_path):
    with open(ROOT / relative_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def combine(inputs):
    columns, records, seen = [], [], set()
    for path in inputs:
        header, rows = read_rows(path)
        columns += [c for c in header if c not in columns]
        for row in rows:
            oid = row["observation_id"]
            if oid in seen:
                raise ValueError(f"{oid} appears in more than one file")
            seen.add(oid)
            records.append({**row, "source_file": path})
    return columns + ["source_file"], records


def write_rows(relative_path, columns, records):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, restval="", lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    (ROOT / relative_path).write_text(buf.getvalue(), encoding="utf-8")


def main():
    try:
        columns, records = combine(INPUTS)
    except ValueError as e:
        print(f"Not combined: {e}", file=sys.stderr)
        return 1
    write_rows(OUTPUT, columns, records)
    print(f"Wrote {len(records)} records and {len(columns)} columns to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
