from ..schemas.models import FilingText
from .common import accession_to_urls, fetch_primary_doc, html_to_text


async def get_filing_text_impl(accession: str) -> FilingText:
    urls = accession_to_urls(accession)
    html, meta = await fetch_primary_doc(accession, urls)
    text = html_to_text(html)
    return FilingText(
        accession=meta["accession"],
        cik=meta["cik"],
        form=meta["form"],
        filed_at=meta["filed_at"],
        source_url=meta["doc_url"],
        text=text,
        spans=None,
    )


