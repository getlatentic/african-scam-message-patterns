"""Build the single release file and its dataset card.

Merges the three country files into one schema, adds a `subset`, a
`template_group` and a `split` column, and writes JSON Lines plus a dataset
card to `release/`. Validation must pass first.

    python3 scripts/build_release.py [--exclude-subset ng_public] [--seed 2026]
"""

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict

from afriscam_io import DATA_FILES, LIST_FIELDS, ROOT, load_records, read_csv
from dataset_card import write_card
from find_duplicates import template_groups
from validate import validate

VERSION = "0.1.1"
SPLIT_SHARES = {"train": 0.7, "validation": 0.15, "test": 0.15}
SUBSETS = ("ke_real", "ke_synthetic", "ng_public", "ng_contributor")
ADDED_COLUMNS = ("subset", "template_group", "split")


def subset_of(record):
    if record["_source"] == "ke":
        return "ke_synthetic" if record["record_origin"] == "synthetic" else "ke_real"
    return record["_source"]


def unified_columns():
    columns = []
    for path in DATA_FILES.values():
        header, _ = read_csv(path)
        columns += [c for c in header if c not in columns]
    return columns + list(ADDED_COLUMNS)


def stratum_of(record):
    """Balance splits within Kenya real, Kenya synthetic and Nigeria real."""
    return "ng" if record["subset"].startswith("ng_") else record["subset"]


def assign_splits(records, seed):
    """Split by template group, so near-identical messages never straddle splits."""
    groups = defaultdict(list)
    for r in records:
        groups[r["template_group"]].append(r)
    by_stratum = defaultdict(dict)
    for group, members in groups.items():
        by_stratum[min(stratum_of(r) for r in members)][group] = members
    digest = lambda g: hashlib.sha256(f"{seed}:{g}".encode()).hexdigest()
    for stratum_groups in by_stratum.values():
        total = sum(len(m) for m in stratum_groups.values())
        filled = Counter()
        for group in sorted(stratum_groups, key=lambda g: (-len(stratum_groups[g]), digest(g))):
            split = max(SPLIT_SHARES, key=lambda s: SPLIT_SHARES[s] * total - filled[s])
            for r in stratum_groups[group]:
                r["split"] = split
            filled[split] += len(stratum_groups[group])


def release_row(record, columns):
    row = {column: record.get(column, "") for column in columns}
    for column in LIST_FIELDS:
        row[column] = json.loads(row[column]) if row[column] else []
    return row


def build(excluded, seed):
    records = load_records()
    findings = validate(records)
    if findings.errors:
        raise SystemExit("Validation errors; run scripts/validate.py and fix them first.")
    groups = template_groups(records)
    for r in records:
        r["subset"] = subset_of(r)
        r["template_group"] = groups[r["observation_id"]]
    records = [r for r in records if r["subset"] not in excluded]
    assign_splits(records, seed)
    records.sort(key=lambda r: (SUBSETS.index(r["subset"]), r["observation_id"]))

    out_dir = ROOT / "release"
    out_dir.mkdir(exist_ok=True)
    data_file = out_dir / f"afriscam-v{VERSION}.jsonl"
    columns = unified_columns()
    with open(data_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(release_row(r, columns), ensure_ascii=False) + "\n")
    write_card(out_dir / "README.md", data_file.name, VERSION, records, excluded)
    return data_file, records


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exclude-subset", action="append", default=[], choices=SUBSETS)
    parser.add_argument("--seed", default="2026")
    args = parser.parse_args()
    data_file, records = build(set(args.exclude_subset), args.seed)
    counts = Counter((r["subset"], r["split"]) for r in records)
    print(f"Wrote {len(records)} records to {data_file.relative_to(ROOT)}")
    for subset in SUBSETS:
        row = {s: counts[(subset, s)] for s in SPLIT_SHARES}
        if any(row.values()):
            print(f"  {subset:15} " + "  ".join(f"{s} {n}" for s, n in row.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
