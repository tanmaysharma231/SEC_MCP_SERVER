import re
from typing import Dict

HEADINGS = [
    ("MDA", r"Item\s+7\.\s*Management['’]s Discussion and Analysis|Item\s+2\.\s*Management"),
    ("RiskFactors", r"Item\s+1A\.\s*Risk Factors"),
    ("Business", r"Item\s+1\.\s*Business"),
    ("Footnotes", r"Notes to (the )?Consolidated Financial Statements"),
]


def extract_sections(text: str) -> Dict[str, dict]:
    found = []
    for key, pat in HEADINGS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            found.append((key, m.start(), m.group(0)))
    found.sort(key=lambda x: x[1])
    results: Dict[str, dict] = {}
    for i, (key, start, heading) in enumerate(found):
        end = found[i + 1][1] if i + 1 < len(found) else len(text)
        results[key] = {"start": start, "end": end, "heading": heading}
    return results


