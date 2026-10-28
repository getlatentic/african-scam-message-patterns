# African Scam Message Patterns

A dataset of scam and fraud messages from African countries, labelled with a shared taxonomy of scam types, persuasion tactics, claimed identities, requested actions and verification status. It supports research, evaluation of scam-detection models, and public awareness work. Work in progress.

## Contents

| Path | Description |
|---|---|
| `data/kenya/af-scam-ke-v0.1.csv` | Kenya observations: 60 records, 10 real-world first, then 50 synthetic |
| `data/nigeria/af-scam-ng-screenshots-v0.1.csv` | Nigeria observations from public screenshots: 61 real-world records (pending review) |
| `data/nigeria/af-scam-ng-contributor-R-F8JM-W6U-v0.1.csv` | Nigeria observations from a contributor: 10 real-world records (pending review) |
| `taxonomy/scam_taxonomy.csv` | Category → scam type → subtype hierarchy (68 subtypes) with working definitions |
| `taxonomy/tactics.csv` | Controlled vocabulary of 22 persuasion tactics |
| `docs/data_dictionary.md` | Field definitions and allowed values |
| `docs/annotation_guidelines.md` | Annotation rules and open taxonomy questions |
| `docs/verification_protocol.md` | How fraud status is established and recorded |
| `docs/privacy_and_consent.md` | Redaction, consent and release rules |
| `examples/` | Usage examples |
| `scripts/` | Validation, duplicate detection, corrections and release build |
| `corrections/` | Record corrections, one file per release, to mirror in the source workbooks |
| `docs/audit-v0.1.md` | Audit of v0.1: taxonomy, duplicates, transcriptions and release readiness |

## Record origin

Each record is either `synthetic` (written to illustrate a taxonomy subtype) or `real_world` (a message contributed by the person who received it). The two are never mixed: synthetic records are never marked verified. Filter on `record_origin` when evaluating models.

Real-world records may have a `screenshot_file` pointing to the original screenshot. Screenshots are unredacted and are not published in this repository.

## Format

- UTF-8 CSV, one row per message.
- `tactics`, `requested_action`, `risk_indicators` and `language_tags` are JSON arrays, e.g. `["authority_claim", "urgency_pressure"]`. An empty cell means not yet labelled.
- `language_tags` use ISO 639-1 codes (`en`, `sw`). Sheng has no ISO code and is tagged `sw`, with a note in `review_notes`.
- Personal and financial details are replaced with placeholders: `[PHONE]`, `[LINK]`, `[EMAIL]`, `[PAYBILL]`, `[ACCOUNT]`, `[AMOUNT]`, `[ORGANIZATION]`, `[NAME]`, `[ADDRESS]`, `[CODE]`.
- Spelling and grammar in message text are kept exactly as received, because errors are themselves scam signals.

## Quick start

```python
import json
import pandas as pd

ke = pd.read_csv("data/kenya/af-scam-ke-v0.1.csv")
for col in ["tactics", "requested_action", "risk_indicators", "language_tags"]:
    ke[col] = ke[col].apply(lambda v: json.loads(v) if isinstance(v, str) else [])

real = ke[ke.record_origin == "real_world"]
print(real.explode("tactics").tactics.value_counts())
```

## Checks and release

```bash
python3 scripts/validate.py                                   # schema, taxonomy, vocabularies, redaction
python3 scripts/find_duplicates.py                            # near-duplicate messages and screenshots (needs Pillow)
python3 scripts/apply_corrections.py corrections/v0.1.1.csv   # apply a corrections file
python3 scripts/build_release.py                              # release/afriscam-v0.1.1.jsonl and its dataset card
```

`validate.py` exits non-zero on schema errors and lists warnings for review. `build_release.py` writes one JSON Lines file with a `subset`, `template_group` and `split` column, plus a Hugging Face dataset card, to `release/` (not committed). Use `--exclude-subset ng_public` to leave out the public screenshot set.

## Status

Version 0.1 is a draft. All records are `pending_review`.

- **Working files:** each CSV is exported from an Excel workbook used for annotation (`AF-SCAM-KE_Standardized_v0.1.xlsx` for Kenya, and the matching `.xlsx` next to each Nigeria CSV). The workbooks also hold verification events and review notes, and are not published.
- **Nigeria duplicates:** one public screenshot record duplicated a contributor's firsthand submission (`AF-SCAM-NG-REAL-0071`). The contribution is kept and the screenshot copy removed; its ID `AF-SCAM-NG-REAL-0010` is retired.
- **Taxonomy:** 12 subtypes (TAX-057 to TAX-068) and one tactic (`religious_appeal`) were added from the Nigeria data, including BVN update phishing, fake bank credit alerts and fake password change alerts.

See [CHANGELOG.md](CHANGELOG.md) for changes.

## License

See [LICENSE](LICENSE).
