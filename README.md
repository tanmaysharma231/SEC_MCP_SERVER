## SEC MCP Server

Quickstart:

```bash
pip install -r requirements.txt
python server.py
```

Add `mcp.json` to your MCP client configuration (Cursor, Claude Desktop, etc.).

Test tools:

```text
find_company { "query": "AAPL" }
search_filings { "cik": "0000320193", "form_types": ["10-K"], "limit": 1 }
get_financials { "cik": "0000320193", "period": "FY2023" }
get_filing_text { "accession": "0000320193-24-000010" }
get_sections { "accession": "0000320193-24-000010", "sections": ["MDA", "RiskFactors"] }
diff_last_two { "cik_or_ticker": "AAPL", "form": "10-Q", "section": "MDA" }
```


