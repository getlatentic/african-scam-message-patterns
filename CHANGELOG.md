# Changelog

All notable changes to this dataset are documented here.

## [Unreleased]

### Added
- `scripts/validate.py`, `scripts/find_duplicates.py`, `scripts/apply_corrections.py` and `scripts/build_release.py`.
- Single-file release build with `subset`, `template_group` and a fixed 70/15/15 `split` grouped by template.
- Audit of v0.1 in `docs/audit-v0.1.md`.

### Fixed
- Corrections in `corrections/v0.1.1.csv`, checked against the screenshots:
  - NG-REAL-0005: restored the "State:" label that was absorbed into a placeholder.
  - NG-REAL-0008: kept the claimed title, "Dr. [NAME]".
  - NG-REAL-0011 and NG-REAL-0072: notes now say the texts differ in one word.
  - NG-REAL-0044: noted that two bubbles are joined and the second is cut off.
  - KE-REAL-0002: noted that the screenshot does not show the closing "Thank you.".
- KE-REAL-0010: removed a real paybill number from the review notes (applied directly, not listed in the corrections file).
- Recorded the v0.1 de-duplication: AF-SCAM-NG-REAL-0010, a screenshot copy of contributor record AF-SCAM-NG-REAL-0071, is retired.

### Changed
- Standardised placeholders to `[PHONE]`, `[LINK]`, `[PAYBILL]`, `[ACCOUNT]`, `[AMOUNT]`, `[ORGANIZATION]`, `[NAME]`, `[CODE]`.
- `tactics` now use the codes in `taxonomy/tactics.csv`; `requested_action` uses a fixed list; `risk_indicators` are `; `-separated with typos fixed.
- Cleared `language_tags` on all records for fresh labelling.
- Redacted personal names in REAL-0005 and REAL-0006 and a password in REAL-0006.
- REAL-0006 `fraud_status` changed to `suspected_fraud`; the reported check supports suspicion, not verification.
- REAL-0004 reassigned from TAX-003 to TAX-008 (payment requested after a job offer).
- REAL-0007: removed `sympathy_appeal` tactic, which the text does not support.
- SYN-0017 rewritten; it was an exact duplicate of SYN-0002.
- REAL-0009 flagged as a possible duplicate of REAL-0003.
- Records sorted: synthetic first, then real-world.
- Removed the `annotation_rule` column from the taxonomy; it is now RULE-010.
- Removed `observed_variants` from `tactics.csv`.

## [0.1.0] - 2026-10-22

### Added
- Kenya dataset `af-scam-ke-v0.1.csv` with 59 records (50 synthetic, 9 real-world), exported from `AF-SCAM-KE_Standardized_v0.1.xlsx`.
- Scam taxonomy with 56 subtypes (`TAX-001` to `TAX-056`).
- Tactics vocabulary with 21 tactics.
- Empty Nigeria dataset with the shared schema.
- Data dictionary, annotation guidelines, verification protocol and privacy policy.

### Known issues
- `language_tags` is empty pending labelling.
- Open taxonomy questions are listed in `docs/annotation_guidelines.md`.
