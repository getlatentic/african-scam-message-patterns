"""Find duplicate and near-duplicate messages, and duplicate screenshots.

Messages are compared after lower-casing, joining hyphen-split words and
collapsing punctuation and spacing.
Pairs at or above the similarity threshold are joined into template groups,
which must stay on one side of any train/test split.

    python3 scripts/find_duplicates.py [--threshold 0.8]
"""

import argparse
import hashlib
import itertools
import re
from difflib import SequenceMatcher

from PIL import Image

from afriscam_io import SCREENSHOT_DIRS, load_records

DEFAULT_THRESHOLD = 0.8
HASH_SIZE = 8
VISUAL_MATCH_BITS = 6


def normalise(text):
    """Comparison key only; stored text keeps the sender's spelling, which is a scam signal."""
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text.lower())
    text = re.sub(r"[^\w\[\]\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a, b):
    matcher = SequenceMatcher(None, a, b)
    if matcher.real_quick_ratio() < DEFAULT_THRESHOLD or matcher.quick_ratio() < DEFAULT_THRESHOLD:
        return matcher.quick_ratio()
    return matcher.ratio()


def similar_pairs(records, threshold):
    texts = [(r["observation_id"], normalise(r["message_text_redacted"])) for r in records]
    pairs = []
    for (id_a, a), (id_b, b) in itertools.combinations(texts, 2):
        if a and b:
            score = 1.0 if a == b else similarity(a, b)
            if score >= threshold:
                shown = 1.0 if a == b else min(round(score, 2), 0.99)
                pairs.append((id_a, id_b, shown))
    return pairs


def template_groups(records, threshold=DEFAULT_THRESHOLD):
    """Map every observation_id to a group id; similar messages share one."""
    parent = {r["observation_id"]: r["observation_id"] for r in records}

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b, _ in similar_pairs(records, threshold):
        parent[root(a)] = root(b)
    return {oid: root(oid) for oid in parent}


def difference_hash(path):
    pixels = Image.open(path).convert("L").resize((HASH_SIZE + 1, HASH_SIZE)).load()
    bits = 0
    for y in range(HASH_SIZE):
        for x in range(HASH_SIZE):
            bits = (bits << 1) | (pixels[x, y] > pixels[x + 1, y])
    return bits


def image_duplicates():
    images = {}
    for folder in SCREENSHOT_DIRS.values():
        if folder.is_dir():
            for path in sorted(folder.iterdir()):
                images[path] = (hashlib.md5(path.read_bytes()).hexdigest(), difference_hash(path))
    identical, similar = [], []
    for (a, (md5_a, hash_a)), (b, (md5_b, hash_b)) in itertools.combinations(images.items(), 2):
        if md5_a == md5_b:
            identical.append((a.name, b.name))
        elif bin(hash_a ^ hash_b).count("1") <= VISUAL_MATCH_BITS:
            similar.append((a.name, b.name))
    return identical, similar


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    args = parser.parse_args()
    records = load_records()

    pairs = similar_pairs(records, args.threshold)
    exact = [p for p in pairs if p[2] == 1.0]
    print(f"Exact duplicate messages: {len(exact)}")
    for a, b, _ in exact:
        print(f"  {a} = {b}")

    groups = {}
    for oid, group in template_groups(records, args.threshold).items():
        groups.setdefault(group, []).append(oid)
    multi = sorted((sorted(v) for v in groups.values() if len(v) > 1), key=len, reverse=True)
    print(f"Template groups at similarity >= {args.threshold}: {len(multi)}")
    for members in multi:
        print(f"  {len(members)}: {', '.join(members)}")

    identical, similar = image_duplicates()
    print(f"Byte-identical screenshots: {len(identical)}")
    for a, b in identical:
        print(f"  {a} = {b}")
    print(f"Visually identical screenshots: {len(similar)}")
    for a, b in similar:
        print(f"  {a} ~ {b}")


if __name__ == "__main__":
    main()
