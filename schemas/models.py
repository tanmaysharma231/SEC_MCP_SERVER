from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict

class Company(BaseModel):
    name: str
    ticker: Optional[str] = None
    cik: str
    sic: Optional[str] = None
    industry: Optional[str] = None
    state_incorp: Optional[str] = None
    hq_location: Optional[str] = None

class Filing(BaseModel):
    accession: str
    form: str
    filed: str  # YYYY-MM-DD
    url: str

class FinancialsSnapshot(BaseModel):
    period: str
    income_statement: dict = Field(default_factory=dict)
    balance_sheet: dict = Field(default_factory=dict)
    cash_flow: dict = Field(default_factory=dict)
    derived: dict = Field(default_factory=dict)  # margins, FCF, ratios

class ErrorPayload(BaseModel):
    error_code: str
    hint: Optional[str] = None
    retry_after_ms: Optional[int] = None


# New schemas for agent-ready pull tools
class FilingText(BaseModel):
    accession: str
    cik: str
    form: str
    filed_at: str  # ISO8601 UTC
    source_url: str
    text: str
    spans: Optional[List[Dict[str, int]]] = None

SectionName = Literal["MDA", "RiskFactors", "Business", "Footnotes"]

class SectionSlice(BaseModel):
    name: SectionName
    start: int
    end: int
    heading: Optional[str] = None
    text: str

class FilingSections(BaseModel):
    accession: str
    cik: str
    form: str
    filed_at: str
    source_url: str
    sections: List[SectionSlice]

class SectionDiff(BaseModel):
    accession_a: str
    accession_b: str
    cik: str
    form: str
    section: SectionName
    filed_at_a: str
    filed_at_b: str
    added: List[str]
    removed: List[str]
    summary: Optional[str] = None
    source_urls: List[str]


