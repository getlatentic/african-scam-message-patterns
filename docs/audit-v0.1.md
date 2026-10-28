# AfriScam data audit (v0.1)

Audit of the v0.1 data at commit `cdb5167`, organised by the data curation pipeline (Collection → Preprocessing → Validation → Documentation, plus Quality Control). Record fixes that need no decision are applied in v0.1.1 (`corrections/v0.1.1.csv`); everything else is listed for a decision.

Rerun the automatic checks with:

```bash
python3 scripts/validate.py
python3 scripts/find_duplicates.py   # needs Pillow
```

## Summary

| Check | Result |
|---|---|
| Records | 131: KE 60 (10 real, 50 synthetic), NG screenshots 61, NG contributor 10. Matches the paper. |
| Taxonomy | All 68 subtypes used. Labels match `taxonomy_id` in every record. Tactics and requested actions are all in the vocabularies. 2 records have no subtype. |
| Duplicates | 1 pair identical after normalisation (0011/0072, separate sends; both kept). 3 template clusters (15 records) at similarity ≥ 0.8. 3 byte-identical image pairs, 1 visually identical pair. No missing record. |
| Transcription | 68 records checked against their images: 64 match, 2 minor, 1 error, 1 unconfirmed. |
| Redaction | 4 judgement calls in message text; 1 real paybill number in `review_notes`. |
| Release blockers | Unredacted screenshots are public; Na Lie source uncredited; no train/test split; no inter-annotator agreement. |

## 1. Collection

| Slide technique | Status in AfriScam |
|---|---|
| Primary sources | 20 firsthand records through AfriEval (KE 10, NG 10), with contributor code, task ID, source row and timestamp in the NG contributor file. |
| Secondary sources | 61 NG records transcribed from public screenshots (2013–2019), found through Data Science Nigeria's Na Lie collection via HamoyeHQ `g02-sms-spam`. |
| Consent, no personal identifiers | Policy exists (`docs/privacy_and_consent.md`), but see below. |
| Licence noted | Repo is CC BY 4.0 as "AfriEval contributors". The Na Lie material has no stated licence. |

**Blockers**

1. **Unredacted screenshots are public.** The repo is public and contains 67 NG images and 6 KE WhatsApp screenshots, with real sender numbers, paybills and account numbers visible (checked on KE-REAL-0002). The README, data dictionary and paper all say screenshots are not published, and the privacy policy keeps real-world records restricted until review. Deleting the files in a new commit leaves them in git history: rewrite the history (e.g. `git filter-repo`) or move the images to private storage, then rotate the public copy.
2. **Na Lie is not credited.** Neither the repo nor paper §3.1 names Data Science Nigeria or Na Lie; the screenshot records only say `public_screenshot_sms`. Add a `source_name` / `source_url` per record (or per set), credit DSN in the README and paper, and keep these records out of the CC BY release until permission or the licence is confirmed.
3. **CC BY 4.0 cannot carry the paper's use restriction** ("users must agree not to use the data to generate deceptive content"). Use gated access with terms (e.g. Hugging Face gated dataset) or a licence that allows use restrictions.

## 2. Preprocessing

### Cleaning

- REAL-0048 (South African MTN marketing) and REAL-0058 (US marketing opt-in) are not scams and have no `taxonomy_id`, `tactics` or `risk_indicators`. Either move them to a labelled non-scam set or remove them; the paper calls all 131 "scam and fraud messages".
- 11 records in the Nigeria file are from other countries (AU 3, US 2, ZA, SG, PH, IN 1 each, 2 unknown) but carry `AF-SCAM-NG` IDs. Their `review_notes` already say so. Move them to their own file with matching IDs, or document that the NG file means "collected in Nigeria".
- REAL-0050 uses `[recipient reply]`, which its notes document as a marker for the excluded reply. Add a marker such as `[REPLY]` to the placeholder list, or drop it.
- KE-REAL-0010 `review_notes` contains the school's real paybill number. Remove it.

### Normalisation

Correctly kept minimal: message spelling is preserved, which the paper explains. Placeholders are consistent across all 131 records apart from the one above. No encoding artefacts or stray whitespace were found.

### Deduplication

Method (`scripts/find_duplicates.py`): case, spacing and punctuation normalised and hyphen-split words joined ("re- activate" → "reactivate"), for comparison only, then exact match and `difflib` similarity ≥ 0.8 across all three files; images compared by MD5 and an 8×8 difference hash.

- **Exact duplicates:** one pair, REAL-0011 (screenshot) and REAL-0072 (contributor). Their originals have different agent names and numbers, so both are kept as separate sends, as their notes say. Stored text keeps the sender's spelling ("re- activate" vs "reactivate"); only the comparison normalises it.
- **Cross-set duplicate:** REAL-0010 (screenshot) duplicated REAL-0071 (contributor). The screenshot copy was retired and 0071 kept. This is correct, but the README and paper do not mention it. Add it to paper §5.
- **Template clusters**, kept as separate incidents (correct), but each cluster must stay on one side of any split:
  - **"System upgrade, ATM card de-activated, call customer care" (10 records):** REAL-0011, 0012, 0015, 0016, 0018, 0020, 0021, 0038, 0039, 0072.
  - **"BVN validation in compliance with CBN" (3 records):** REAL-0037, 0051, 0054.
  - **"New BVN policy by the CBN" (2 records):** REAL-0036, 0059.
- **Images:** 3 byte-identical pairs and 1 visually identical pair. All are linked to existing records or noted as context (9059355 holds the buyer's own replies for REAL-0035). This matches the paper's "67 image files" account. No screenshot is missing a record.

### Formatting

- **List fields:** every one parses as a JSON array.
- **ID format:** valid throughout.
- **Schemas differ between the three files:**
  - KE has 19 columns.
  - NG screenshots has 17: no `verification_status` or `review_status`.
  - NG contributor has 20: no `screenshot_file`, `verification_status` or `review_status`, and adds four provenance columns.

  The README and paper say every record is `pending_review`, but the NG files have no column for it. Use one schema with empty provenance columns where they don't apply.
- **REAL-0067:** `record_origin` is `real_world` but `source_type` is `synthetic_generated`. Its own note asks which is right.

### Splitting

`scripts/build_release.py` now assigns a fixed 70/15/15 split, grouped by template cluster, within Kenya real, Kenya synthetic and Nigeria real. The split is deterministic for a given seed.

## 3. Validation

### Automatic (`scripts/validate.py`, all 131 records)

| Check | Failures |
|---|---|
| `taxonomy_id` exists | 2 (REAL-0048, 0058: empty) |
| category, scam type and subtype match the taxonomy | 0 |
| tactics in vocabulary (22) | 0 |
| requested actions in fixed list | 0 |
| enums (origin, source type, fraud status) | 0 |
| origin vs source type | 1 (REAL-0067) |
| synthetic never verified | 0 |
| non-standard placeholders | 1 (REAL-0050) |
| unredacted phone, URL or email in message text | 0 (2 hits were dates) |

### Manual (all 68 records with a screenshot, image by image)

**64 match, 2 minor, 1 error, 1 unconfirmed.**

**Errors**
- **NG-REAL-0005:** the image reads "City: <town> (2/2) <town>. State: <state>. Country: Nigeria.", but the transcription had "City: [ADDRESS] (2/2) [ADDRESS]. Country: Nigeria.": the label "State:" was swallowed, and town and state were redacted although the policy only redacts street addresses and venues, and other records keep towns (Lagos, Abuja, Calabar). The address is the scammer's drop address, so it cannot identify the US recipient. Fixed: only the name and street stay redacted.

**Unconfirmed**
- **KE-REAL-0002:** the transcription ends with "Thank you.", but the screenshot ends at "ALLOWED)" because the message bubble is cut off. The Kenya records came in as text, so the line may be in the contributor's submission. A note now asks for that check.

Leading "…" (as in NG-REAL-0044 and 0050) marks a message whose top is cut off, and is used consistently.

**Minor**
- **NG-REAL-0008:** "Dr. <name>" became "[NAME]", which loses the claimed title. Use "Dr. [NAME]".
- **NG-REAL-0044:**
  - Missing line breaks.
  - Two bubbles are merged into one record.
  - The second bubble is cut off at the bottom; note this.
  - A scam-issued reference number is left visible.

**Redaction judgement calls**
- **NG-REAL-0055:** "NGSR", the fake recruiter's name and sender ID, is left visible. Similar fake companies elsewhere are redacted as [ORGANIZATION].
- **NG-REAL-0029:** "e-SME" plus a number is redacted as [ACCOUNT]. [CODE] may fit better.
- **NG-REAL-0057:** a third, separate GCash message is included in the record.
- **NG-REAL-0046:** the bait amount in AUD is left visible. That is consistent with other records, where amounts in the lure are kept.

What each method caught (the slide asks for this):
- **Automatic checks only:** the empty-taxonomy records and the schema and origin conflicts.
- **Manual check only:** the added and swallowed text, the cut-off messages and the redaction choices.

### Error correction and final check

Applied in v0.1.1 through `corrections/v0.1.1.csv`: NG-REAL-0005 (town, state and "State:" label restored; only name and street redacted), NG-REAL-0008 ("Dr. [NAME]"), the NG-REAL-0044 note, and a note on KE-REAL-0002. The paybill number in KE-REAL-0010's notes was removed directly (not listed in the corrections file, so the number is not copied into it); remove it in the workbook too. The KE-REAL-0002 text itself is unchanged until the contributor's submitted text is checked. Mirror these rows in the source workbooks.

## 4. Quality control

| Slide technique (MasakhaNER, AfriVoices-KE) | AfriScam |
|---|---|
| Several annotators per item, agreement (Fleiss' or Cohen's kappa) | Not done. All labels come from one pass plus author review. Paper §7 says so. |
| Disagreement resolution | Not documented. |
| Gold standard (double-verified share) | Not defined. |
| Tiered or senior review | Not documented. |

**Taxonomy issues found:**
- **One template, two subtypes.** The "ATM card de-activated" template is labelled TAX-022 (ATM card verification) when it doesn't say "BVN", and TAX-057 (BVN update) when it does. TAX-022's definition ("asks for the card number, PIN, CVV or a one time code") doesn't fit these messages, which ask the recipient to call a number. Either widen TAX-022's definition or label the whole template TAX-057.
- **Inconsistent `claimed_identity` within the same template:** "Bank customer care" in 0038 and 0039, "Central Bank of Nigeria" in 0018 and 0021.
- **Thin real-world coverage:** 16 subtypes have exactly one real-world record, and 42 subtypes exist only as synthetic examples. Subtype classification on real data is therefore thin.
- **Open taxonomy questions:** the 8 listed in `docs/annotation_guidelines.md` are still open.

**Job scams.** Employment fraud has 7 subtypes (TAX-003 to 008, plus TAX-060), and 27 real-world records use them: 25 from NG and 2 from KE. Every job-like message is labelled under Employment fraud. But the labels are concentrated in one subtype, and the taxonomy is missing some patterns:
- **One subtype dominates.** TAX-004 (false shortlisting) holds 22 of the 27. In 19 of those, the requested action is "Attend in person" at an address. That in-person venue lure is the main Nigerian pattern, and the harm happens on site (a fee demand, pressure to join network marketing). TAX-004's "build trust ahead of a later request" covers it only loosely. Consider a separate subtype for the in-person interview lure.
- **The synthetic example for TAX-004 doesn't fit it.** KE-SYN-0012 says "Complete registration at [LINK]", which matches TAX-003 (job link) better than TAX-004, whose definition rules out a request in the same message.
- **Patterns with no subtype yet:**
  - Fake government recruitment, such as REAL-0009 (Federal Road Safety Commission) and REAL-0034 (a computer-based test).
  - Document or certificate demands that lead to a paid provider (REAL-0008).
  - Application forms or CVs harvested by email (REAL-0033).
  - Common elsewhere but absent here: money-mule or "payment agent" jobs, reshipping, and overpayment cheques.
- **Little real data from Kenya.** Only 2 Kenyan real-world job scams exist. The other 5 Kenyan job records are synthetic.

A small agreement study would close most of this. Suggested design:
- Have both of you label the same 30 real records independently: subtype, tactics, claimed identity.
- Report Cohen's kappa for subtype, and per-tactic agreement.
- Resolve disagreements together and record the decisions as annotation rules.

## 5. Documentation

| Slide technique | Status |
|---|---|
| Metadata and dataset card | README, data dictionary, guidelines, verification protocol and privacy policy exist. A Hugging Face dataset card (datasheet) is not written yet. |
| Storage in repositories | GitHub (public, see blocker 1). Hugging Face link is a placeholder in the paper. |
| Maintenance | CHANGELOG exists; the 0010 retirement and the screenshot removal are not yet logged as release entries. |

Paper fixes:
- **§3.1:** credit Na Lie and Data Science Nigeria.
- **§5:** add the 0010 and 0071 duplicate, the splitting plan, and the validation numbers above.
- **§6:** fix the licence-and-restriction conflict, and match the release plan to what the repo actually publishes.
- **Repo name:** the paper says `african-scam-message`; it is `african-scam-message-patterns`.
- **References:** Wanzare et al. 2026 is listed but never cited in the text.
- **Acknowledgements:** still a placeholder.

## Fix list, in order

1. Take the screenshots out of the public repo and its history.
2. Credit Na Lie and DSN, and settle the licence for the screenshot set.
3. Confirm KE-REAL-0002's last line against the contributor's submitted text. NG-REAL-0005, NG-REAL-0008 and the KE-REAL-0010 notes are fixed in v0.1.1.
4. Resolve REAL-0067's origin, REAL-0048 and 0058 (non-scam), and the 11 non-Nigerian records.
5. Unify the schema across the three files.
6. Decide on TAX-022 vs TAX-057 for the ATM template, and align `claimed_identity`.
7. Define a grouped train/validation/test split.
8. Run a 30-record agreement study.
9. Update paper §3.1, §5 and §6, and write the dataset card.
