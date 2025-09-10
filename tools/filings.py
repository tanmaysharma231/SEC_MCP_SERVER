from typing import List, Optional
from schemas.models import Filing
from adapters.sec_api import fetch_json

FILINGS_TTL = 24 * 3600

def _filing_url(accession: str, cik10: str):
    acc_no_dashes = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{acc_no_dashes}/{accession}.txt"

async def search_filings_impl(cik: str, form_types: List[str], start_date: Optional[str], end_date: Optional[str], limit: int) -> List[Filing]:
    cik10 = str(int(cik)).zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik10}.json"
    data = await fetch_json(url, cache_key=f"subs_{cik10}", cache_ttl=FILINGS_TTL)

    forms = data.get("filings", {}).get("recent", {})
    rows = []
    for i in range(len(forms.get("accessionNumber", []))):
        form = forms["form"][i]
        if form_types and form not in form_types:
            continue
        filed = forms["filingDate"][i]
        acc = forms["accessionNumber"][i]
        if start_date and filed < start_date:
            continue
        if end_date and filed > end_date:
            continue
        rows.append(Filing(
            accession=acc,
            form=form,
            filed=filed,
            url=_filing_url(acc, cik10)
        ))

    rows.sort(key=lambda r: r.filed, reverse=True)
    return rows[:limit]


