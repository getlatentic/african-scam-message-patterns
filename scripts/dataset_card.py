"""Write the Hugging Face dataset card for a release."""

from collections import Counter

SUBSET_DESCRIPTIONS = {
    "ke_real": "Kenya, real-world messages contributed firsthand through AfriEval",
    "ke_synthetic": "Kenya, synthetic messages written to illustrate one taxonomy subtype each",
    "ng_public": "Nigeria, transcribed from publicly circulated screenshots (2013–2019)",
    "ng_contributor": "Nigeria, real-world messages contributed firsthand through AfriEval",
}

FRONT_MATTER = """---
pretty_name: AfriScam
license: cc-by-4.0
language:
- en
- sw
- pcm
task_categories:
- text-classification
tags:
- scam-detection
- fraud
- sms
- code-switching
- african-languages
size_categories:
- n<1K
configs:
- config_name: default
  data_files: {data_file}
---
"""

BODY = """
# AfriScam

Scam and fraud messages from Kenya and Nigeria, in English, Swahili, Sheng and Nigerian Pidgin, labelled with a shared taxonomy of scam types, persuasion tactics, claimed identities, requested actions and an evidence-based fraud status. Version {version}. Every record is `pending_review`.

## Contents

One file, `{data_file}`, one JSON object per line. Filter on `subset` or `split`.

| Subset | Records | Description |
|---|---|---|
{subset_rows}

| Split | Records |
|---|---|
{split_rows}
{excluded_note}
## Fields

The fields are defined in the repository's `docs/data_dictionary.md`. The release adds:

- `subset`: one of the subsets above.
- `template_group`: records whose redacted text is at least 80% similar share a group. Most are separate sends of one scam template.
- `split`: `train`, `validation` or `test`. Kenya real, Kenya synthetic and Nigeria real are each split 70/15/15 by template group, so no group crosses splits.

`tactics`, `requested_action`, `risk_indicators` and `language_tags` are JSON arrays. Fields that do not apply to a subset are empty strings (for example `contributor_code` outside `ng_contributor`).

## Sources

- **Firsthand contributions** (`ke_real`, `ng_contributor`) were collected through the AfriEval platform with the recipient's informed consent. Contributors may withdraw a record at any time.
- **Public screenshots** (`ng_public`) were found through Data Science Nigeria's Na Lie collection [confirm the attribution and licence with Data Science Nigeria before publishing]. Only redacted transcriptions are released, not the images, whose rights rest with their original publishers.
- **Synthetic messages** (`ke_synthetic`) were written by the authors. They are never marked verified.

## Redaction

Personal and financial details are replaced with `[PHONE]`, `[LINK]`, `[EMAIL]`, `[PAYBILL]`, `[ACCOUNT]`, `[AMOUNT]`, `[ORGANIZATION]`, `[NAME]`, `[ADDRESS]` and `[CODE]`. Institutions a scam claims to be (the CBN, banks, mobile networks) are kept. Spelling and grammar are kept as received, because errors are scam signals.

## Intended use and limits

Intended for scam-detection research and evaluation: scam versus non-scam, subtype classification and tactic tagging. Report results separately for real-world and synthetic records, and per country.

- The dataset is small, and its real-world part is dominated by Nigerian BVN and fake-interview campaigns from 2013–2019 and Kenyan scams from 2025.
- Some records in the Nigeria file come from other countries; see `country`.
- Inter-annotator agreement has not been measured.
- Do not use the data to write or improve deceptive messages. [CC BY 4.0 cannot enforce this; decide whether to gate access with terms.]

## Citation

[Add the AfriScam paper citation on publication.]
"""


def table_rows(counts, descriptions=None):
    lines = []
    for key, n in counts.items():
        extra = f" | {descriptions[key]}" if descriptions else ""
        lines.append(f"| `{key}` | {n}{extra} |")
    return "\n".join(lines)


def write_card(path, data_file, version, records, excluded):
    subsets = Counter(r["subset"] for r in records)
    splits = Counter(r["split"] for r in records)
    excluded_note = ""
    if excluded:
        names = ", ".join(f"`{s}`" for s in sorted(excluded))
        excluded_note = f"\nExcluded from this build: {names}.\n"
    text = FRONT_MATTER.format(data_file=data_file) + BODY.format(
        version=version,
        data_file=data_file,
        subset_rows=table_rows(subsets, SUBSET_DESCRIPTIONS),
        split_rows=table_rows({s: splits[s] for s in ("train", "validation", "test")}),
        excluded_note=excluded_note,
    )
    path.write_text(text, encoding="utf-8")
