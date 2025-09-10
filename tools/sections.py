from typing import List, Optional

from ..schemas.models import FilingSections, SectionSlice, SectionName
from .filing_text import get_filing_text_impl
from .sectioner import extract_sections


async def get_sections_impl(accession: str, sections: Optional[List[SectionName]]) -> FilingSections:
    ft = await get_filing_text_impl(accession)
    all_sections = extract_sections(ft.text)
    wanted = set(sections) if sections else set(all_sections.keys())
    slices = []
    for name, s in all_sections.items():
        if name in wanted:
            slices.append(
                SectionSlice(
                    name=name, start=s["start"], end=s["end"], heading=s.get("heading"), text=ft.text[s["start"] : s["end"]]
                )
            )
    return FilingSections(
        accession=ft.accession, cik=ft.cik, form=ft.form, filed_at=ft.filed_at, source_url=ft.source_url, sections=slices
    )


