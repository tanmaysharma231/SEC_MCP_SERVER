from datetime import datetime, timezone
from typing import Dict
from urllib.parse import urljoin

from ..adapters.sec_api import fetch_json


def zero_pad_cik(cik: str) -> str:
    return str(int(cik)).zfill(10)


def html_to_text(html: str) -> str:
    from selectolax.parser import HTMLParser
    tree = HTMLParser(html)
    return tree.body.text(separator="\n", strip=True) if tree.body else ""


def _accession_to_paths(accession: str) -> Dict[str, str]:
    # accession like 0000320193-24-000010
    acc_nodash = accession.replace("-", "")
    # Need CIK to construct full path. We'll derive via submissions if not supplied.
    return {
        "acc_nodash": acc_nodash,
    }


async def _lookup_meta_from_submissions(accession: str) -> Dict[str, str]:
    # Brute-force via submissions index: the first 10 digits are the CIK
    # Some accessions embed CIK; if not, try all? Instead, query the daily index is heavy.
    # Here we assume accession includes CIK prefix (standard case).
    cik_prefix = accession.split("-")[0]
    cik10 = zero_pad_cik(cik_prefix)
    subs_url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    subs = await fetch_json(subs_url, cache_key=f"subs_{cik10}", cache_ttl=24 * 3600)
    recent = subs.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    filed = recent.get("filingDate", [])
    primary_docs = recent.get("primaryDocument", [])
    for i, acc in enumerate(accs):
        if acc == accession:
            form = forms[i]
            filed_at = datetime.fromisoformat(filed[i])
            filed_at_iso = filed_at.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
            doc = primary_docs[i]
            acc_nodash = accession.replace("-", "")
            base = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{acc_nodash}/"
            return {
                "accession": accession,
                "cik": cik10,
                "form": form,
                "filed_at": filed_at_iso,
                "index_url": urljoin(base, f"{accession}.txt"),
                "doc_url": urljoin(base, doc),
            }
    raise ValueError("Accession not found in submissions")


async def fetch_primary_doc(accession: str, urls: Dict[str, str] | None = None):
    meta = await _lookup_meta_from_submissions(accession)
    # Primary doc may be HTML or text. If .txt, we still return as string.
    from httpx import AsyncClient
    async with AsyncClient(timeout=20.0) as client:
        resp = await client.get(meta["doc_url"], headers={"User-Agent": "sec-mcp/0.1 contact@example.com"})
        resp.raise_for_status()
        html = resp.text
        return html, meta


def accession_to_urls(accession: str) -> Dict[str, str]:
    paths = _accession_to_paths(accession)
    # Will be completed in _lookup_meta_from_submissions
    return paths


