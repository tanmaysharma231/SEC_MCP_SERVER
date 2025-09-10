from typing import Optional
from schemas.models import Company
from adapters.sec_api import fetch_json

# SEC provides a mapping of tickers to CIKs. Cache it for a week.
TICKER_TTL = 7 * 24 * 3600

async def find_company_impl(query: str) -> Company:
    q = query.strip().upper()
    url = "https://www.sec.gov/files/company_tickers.json"
    data = await fetch_json(url, cache_key="company_tickers", cache_ttl=TICKER_TTL)

    # company_tickers.json is a dict of index -> {ticker, cik_str, title}
    by_ticker = {v["ticker"].upper(): v for v in data.values()}
    by_cik = {v["cik_str"]: v for v in data.values()}

    rec = None
    if q in by_ticker:
        rec = by_ticker[q]
    elif q.isdigit() and int(q) in by_cik:
        rec = by_cik[int(q)]
    else:
        # fallback: fuzzy title match
        qn = q.lower()
        for v in data.values():
            if qn in v["title"].lower():
                rec = v
                break

    if not rec:
        raise ValueError("Company not found")

    cik = str(rec["cik_str"]).zfill(10)
    return Company(name=rec["title"], ticker=rec["ticker"], cik=cik)


