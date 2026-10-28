"""Reading and writing the AfriScam CSV files and vocabularies."""

import csv
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_FILES = {
    "ke": ROOT / "data/kenya/af-scam-ke-v0.1.csv",
    "ng_public": ROOT / "data/nigeria/af-scam-ng-screenshots-v0.1.csv",
    "ng_contributor": ROOT / "data/nigeria/af-scam-ng-contributor-R-F8JM-W6U-v0.1.csv",
}

SCREENSHOT_DIRS = {
    "ke": ROOT / "data/kenya/screenshots",
    "ng_public": ROOT / "data/nigeria/Fake Sms Images",
}

LIST_FIELDS = ("tactics", "requested_action", "risk_indicators", "language_tags")

PLACEHOLDERS = {
    "[PHONE]", "[LINK]", "[EMAIL]", "[PAYBILL]", "[ACCOUNT]", "[AMOUNT]",
    "[ORGANIZATION]", "[NAME]", "[ADDRESS]", "[CODE]",
}

REQUESTED_ACTIONS = {
    "Open link", "Pay fee", "Pay deposit", "Pay to account", "Send money",
    "Submit information", "Submit documents", "Call number", "Share code",
    "Invest", "Attend in person", "Dial USSD code", "Reply to message",
    "Reply by email", "Release goods", "Activate service", "Vote", "None stated",
}

ENUMS = {
    "record_origin": {"synthetic", "real_world"},
    "source_type": {
        "synthetic_generated", "firsthand_sms", "firsthand_whatsapp", "firsthand_other",
        "public_screenshot_sms", "public_screenshot_email", "public_screenshot_social_dm",
    },
    "fraud_status": {"suspected_fraud", "verified_fraudulent_request", "unassessed"},
    "verification_status": {"not_applicable", "completed_reported", "not_documented"},
    "review_status": {"pending_review", "reviewed"},
}


def read_csv(path):
    """Return (header, rows) with rows as dicts, preserving column order."""
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def write_csv(path, header, rows):
    """Write rows in the files' own format: minimal quoting, LF line endings."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    Path(path).write_text(buf.getvalue(), encoding="utf-8")


def load_records():
    """Return every record, each tagged with the key of the file it came from."""
    records = []
    for source, path in DATA_FILES.items():
        _, rows = read_csv(path)
        for row in rows:
            row["_source"] = source
            records.append(row)
    return records


def load_taxonomy():
    _, rows = read_csv(ROOT / "taxonomy/scam_taxonomy.csv")
    return {row["taxonomy_id"]: row for row in rows}


def load_tactics():
    _, rows = read_csv(ROOT / "taxonomy/tactics.csv")
    return {row["tactic"] for row in rows}
