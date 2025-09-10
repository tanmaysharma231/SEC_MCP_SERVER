import asyncio
from mcp.server.fastapi import FastAPIServer
from mcp.types import Tool, ToolRequest, TextContent
from schemas.models import ErrorPayload
from tools.company import find_company_impl
from tools.filings import search_filings_impl
from tools.financials import get_financials_impl
from tools.filing_text import get_filing_text_impl
from tools.sections import get_sections_impl
from tools.diff import diff_last_two_impl

server = FastAPIServer("sec-mcp")

@server.tool(
    Tool(
        name="find_company",
        description="Resolve a ticker, company name, or CIK to canonical company metadata"
    )
)
async def find_company(req: ToolRequest):
    try:
        query = req.arguments["query"]
        company = await find_company_impl(query)
        return [TextContent(type="text", text=company.model_dump_json())]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="NOT_FOUND", hint=str(e)).model_dump_json())]

@server.tool(
    Tool(
        name="search_filings",
        description="Search filings for a company"
    )
)
async def search_filings(req: ToolRequest):
    try:
        cik = req.arguments["cik"]
        forms = req.arguments.get("form_types", [])
        start_date = req.arguments.get("start_date")
        end_date = req.arguments.get("end_date")
        limit = int(req.arguments.get("limit", 10))
        filings = await search_filings_impl(cik, forms, start_date, end_date, limit)
        # Return as JSON lines for easier parsing at scale
        text = "\n".join(f.model_dump_json() for f in filings)
        return [TextContent(type="text", text=text)]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="BAD_REQUEST", hint=str(e)).model_dump_json())]

@server.tool(
    Tool(
        name="get_financials",
        description="Return structured XBRL financials snapshot"
    )
)
async def get_financials(req: ToolRequest):
    try:
        cik = req.arguments["cik"]
        period = req.arguments["period"]
        snap = await get_financials_impl(cik, period)
        return [TextContent(type="text", text=snap.model_dump_json())]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="BAD_REQUEST", hint=str(e)).model_dump_json())]

@server.tool(
    Tool(
        name="get_filing_text",
        description="Return raw text and provenance for a filing by accession"
    )
)
async def get_filing_text(req: ToolRequest):
    try:
        accession = req.arguments["accession"]
        ft = await get_filing_text_impl(accession)
        return [TextContent(type="text", text=ft.model_dump_json())]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="BAD_REQUEST", hint=str(e)).model_dump_json())]

@server.tool(
    Tool(
        name="get_sections",
        description="Return selected sections for a 10-K or 10-Q filing"
    )
)
async def get_sections(req: ToolRequest):
    try:
        accession = req.arguments["accession"]
        sections = req.arguments.get("sections")
        fs = await get_sections_impl(accession, sections)
        return [TextContent(type="text", text=fs.model_dump_json())]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="BAD_REQUEST", hint=str(e)).model_dump_json())]

@server.tool(
    Tool(
        name="diff_last_two",
        description="Diff the requested section across the last two filings of a form"
    )
)
async def diff_last_two(req: ToolRequest):
    try:
        cik_or_ticker = req.arguments["cik_or_ticker"]
        form = req.arguments["form"]
        section = req.arguments["section"]
        diff = await diff_last_two_impl(cik_or_ticker, form, section)
        return [TextContent(type="text", text=diff.model_dump_json())]
    except Exception as e:
        return [TextContent(type="text", text=ErrorPayload(error_code="BAD_REQUEST", hint=str(e)).model_dump_json())]

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    server.run()


