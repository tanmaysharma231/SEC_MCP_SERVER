from ..schemas.models import SectionDiff, SectionName
from .filings import search_filings_impl
from .sections import get_sections_impl
from .sentdiff import sentence_diff


async def diff_last_two_impl(cik_or_ticker: str, form: str, section: SectionName) -> SectionDiff:
    filings = await search_filings_impl(cik_or_ticker, [form], None, None, limit=2)
    if len(filings) < 2:
        raise ValueError("Not enough filings to diff")
    a, b = filings[1], filings[0]
    sa = await get_sections_impl(a.accession, [section])
    sb = await get_sections_impl(b.accession, [section])
    ta = sa.sections[0].text if sa.sections else ""
    tb = sb.sections[0].text if sb.sections else ""
    added, removed = sentence_diff(ta, tb)
    return SectionDiff(
        accession_a=a.accession,
        accession_b=b.accession,
        cik=b.cik if hasattr(b, "cik") else "",
        form=form,
        section=section,
        filed_at_a=getattr(a, "filed", ""),
        filed_at_b=getattr(b, "filed", ""),
        added=added,
        removed=removed,
        summary=None,
        source_urls=[a.url, b.url],
    )


