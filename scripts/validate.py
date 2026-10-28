"""Check every record against the data dictionary, taxonomy and vocabularies.

Errors break the schema and fail the run. Warnings need a reviewer's decision.

    python3 scripts/validate.py
"""

import json
import re
import sys
from collections import defaultdict

from afriscam_io import (
    ENUMS, LIST_FIELDS, PLACEHOLDERS, REQUESTED_ACTIONS, SCREENSHOT_DIRS,
    load_records, load_tactics, load_taxonomy,
)

ID_PATTERN = re.compile(r"AF-SCAM-(KE|NG)-(SYN|REAL)-\d{4}")
LANGUAGE_CODES = {"en", "sw", "pcm", "tl", "yo", "ig", "ha"}
LEAK_PATTERNS = {
    "phone number": re.compile(r"(?<![\w\[/-])\+?\d[\d -]{7,}\d(?![\w/-])"),
    "link": re.compile(r"(?i)\b(?:https?://|www\.)\S+"),
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
}
NOTE_NUMBER = re.compile(r"\b\d{5,}\b")
DATE = re.compile(r"\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}(?: \d{1,2}(?::\d{2})?)?\b")


def screenshot_numbers():
    """Digit runs in screenshot file names; notes cite these, and they identify no one."""
    numbers = set()
    for folder in SCREENSHOT_DIRS.values():
        if folder.is_dir():
            for path in folder.iterdir():
                numbers.update(NOTE_NUMBER.findall(re.sub(r"\D", " ", path.name)))
    return numbers


class Findings:
    def __init__(self):
        self.errors = defaultdict(list)
        self.warnings = defaultdict(list)

    def error(self, check, record, detail=""):
        self.errors[check].append(f"{record['observation_id']} {detail}".strip())

    def warn(self, check, record, detail=""):
        self.warnings[check].append(f"{record['observation_id']} {detail}".strip())


def check_identity(record, findings):
    oid = record["observation_id"]
    if not ID_PATTERN.fullmatch(oid):
        findings.error("observation_id format", record)
    if ("-SYN-" in oid) != (record["record_origin"] == "synthetic"):
        findings.error("ID does not match record_origin", record, record["record_origin"])
    if (record["record_origin"] == "synthetic") != (record["source_type"] == "synthetic_generated"):
        findings.warn("record_origin and source_type disagree", record,
                      f"{record['record_origin']} / {record['source_type']}")


def check_enums(record, findings):
    for field, allowed in ENUMS.items():
        if field in record and record[field] not in allowed:
            findings.error(f"{field} not an allowed value", record, repr(record[field]))
    if record["record_origin"] == "synthetic" and record["fraud_status"] == "verified_fraudulent_request":
        findings.error("synthetic record marked verified", record)


def check_taxonomy(record, taxonomy, findings):
    entry = taxonomy.get(record["taxonomy_id"])
    if entry is None:
        findings.warn("no taxonomy_id", record, repr(record["taxonomy_id"]))
        return
    for field in ("category", "scam_type", "subtype"):
        if record[field].strip() != entry[field].strip():
            findings.error(f"{field} does not match taxonomy", record, repr(record[field]))


def parse_list(record, field, findings):
    value = record.get(field, "")
    if not value:
        findings.warn(f"{field} empty", record)
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        findings.error(f"{field} is not valid JSON", record)
        return []
    if not isinstance(parsed, list):
        findings.error(f"{field} is not a JSON array", record)
        return []
    return parsed


def check_lists(record, tactics, findings):
    values = {field: parse_list(record, field, findings) for field in LIST_FIELDS}
    for tactic in values["tactics"]:
        if tactic not in tactics:
            findings.error("tactic not in taxonomy/tactics.csv", record, tactic)
    for action in values["requested_action"]:
        if action not in REQUESTED_ACTIONS:
            findings.error("requested_action not in the fixed list", record, action)
    for code in values["language_tags"]:
        if code not in LANGUAGE_CODES:
            findings.warn("unexpected language tag", record, code)


def check_redaction(record, image_numbers, findings):
    text = record["message_text_redacted"]
    for token in re.findall(r"\[[^\]]*\]", text):
        if token not in PLACEHOLDERS:
            findings.warn("non-standard placeholder", record, token)
    undated = DATE.sub(" ", text)
    for kind, pattern in LEAK_PATTERNS.items():
        if pattern.search(undated):
            findings.warn(f"possible unredacted {kind} in message", record, "(value not shown)")
    note_numbers = set(NOTE_NUMBER.findall(re.sub(r"\D", " ", record.get("review_notes", ""))))
    if note_numbers - image_numbers:
        findings.warn("long number in review_notes", record, "(value not shown)")


def validate(records):
    taxonomy, tactics, image_numbers = load_taxonomy(), load_tactics(), screenshot_numbers()
    findings = Findings()
    seen = set()
    for record in records:
        if record["observation_id"] in seen:
            findings.error("duplicate observation_id", record)
        seen.add(record["observation_id"])
        check_identity(record, findings)
        check_enums(record, findings)
        check_taxonomy(record, taxonomy, findings)
        check_lists(record, tactics, findings)
        check_redaction(record, image_numbers, findings)
    return findings


def print_section(title, groups):
    print(f"\n{title}: {sum(len(v) for v in groups.values())}")
    for check, items in sorted(groups.items()):
        print(f"  {check} ({len(items)})")
        for item in items:
            print(f"    {item}")


def main():
    records = load_records()
    findings = validate(records)
    print(f"Checked {len(records)} records.")
    print_section("Errors", findings.errors)
    print_section("Warnings", findings.warnings)
    return 1 if findings.errors else 0


if __name__ == "__main__":
    sys.exit(main())
