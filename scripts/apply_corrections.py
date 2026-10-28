"""Apply a corrections file to the data CSVs.

Each row of the corrections file names a record, a field, the text to find and
its replacement. An empty `find` sets a field that must currently be empty.
The source workbooks are not in this repository, so mirror each row there too.

    python3 scripts/apply_corrections.py corrections/v0.1.1.csv
"""

import argparse
import sys

from afriscam_io import DATA_FILES, read_csv, write_csv


class CorrectionError(Exception):
    pass


def corrected_value(current, find, replace):
    """Return the new field value, or None if this correction is already applied."""
    if find == "":
        if current == replace:
            return None
        if current != "":
            raise CorrectionError("field is not empty")
        return replace
    if replace in current:
        return None
    count = current.count(find)
    if count != 1:
        raise CorrectionError(f"text to find occurs {count} times")
    return current.replace(find, replace)


def apply(corrections):
    files = {key: read_csv(path) for key, path in DATA_FILES.items()}
    by_id = {row["observation_id"]: (key, row) for key, (_, rows) in files.items() for row in rows}
    changed, applied, skipped = set(), [], []
    for c in corrections:
        key, row = by_id.get(c["observation_id"], (None, None))
        if row is None:
            raise CorrectionError(f"{c['observation_id']}: no such record")
        if c["field"] not in row:
            raise CorrectionError(f"{c['observation_id']}: no field {c['field']}")
        try:
            new = corrected_value(row[c["field"]], c["find"], c["replace"])
        except CorrectionError as e:
            raise CorrectionError(f"{c['observation_id']}.{c['field']}: {e}") from None
        if new is None:
            skipped.append(c)
            continue
        row[c["field"]] = new
        changed.add(key)
        applied.append(c)
    for key in changed:
        header, rows = files[key]
        write_csv(DATA_FILES[key], header, rows)
    return applied, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("corrections")
    args = parser.parse_args()
    _, corrections = read_csv(args.corrections)
    try:
        applied, skipped = apply(corrections)
    except CorrectionError as e:
        print(f"Not applied: {e}", file=sys.stderr)
        return 1
    for c in applied:
        print(f"applied  {c['observation_id']} {c['field']}")
    for c in skipped:
        print(f"already  {c['observation_id']} {c['field']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
