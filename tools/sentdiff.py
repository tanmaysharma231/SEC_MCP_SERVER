import re
from rapidfuzz import process, fuzz


def split_sents(t: str):
    return [s.strip() for s in re.split(r"(?<=[\.?\!])\s+", t) if s.strip()]


def sentence_diff(old: str, new: str):
    old_s = split_sents(old)
    new_s = split_sents(new)
    added, removed = [], []
    for s in new_s:
        if not old_s:
            added.append(s)
            continue
        match = process.extractOne(s, old_s, scorer=fuzz.token_set_ratio)
        score = match[1] if match else 0
        if score < 80:
            added.append(s)
    for s in old_s:
        if not new_s:
            removed.append(s)
            continue
        match = process.extractOne(s, new_s, scorer=fuzz.token_set_ratio)
        score = match[1] if match else 0
        if score < 80:
            removed.append(s)
    return added, removed


