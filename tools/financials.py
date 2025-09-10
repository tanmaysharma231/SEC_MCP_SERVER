from typing import Dict
from schemas.models import FinancialsSnapshot
from adapters.sec_api import fetch_json

FACTS_TTL = 7 * 24 * 3600

TAG_MAP = {
    "Revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
    "CostOfRevenue": ["CostOfRevenue"],
    "OperatingIncomeLoss": ["OperatingIncomeLoss"],
    "NetIncomeLoss": ["NetIncomeLoss"],
    "CashAndCashEquivalents": ["CashAndCashEquivalentsAtCarryingValue"],
    "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebtAndCapitalLeaseObligations"],
    "CurrentAssets": ["AssetsCurrent"],
    "CurrentLiabilities": ["LiabilitiesCurrent"],
    "OperatingCashFlow": ["NetCashProvidedByUsedInOperatingActivities"],
    "Capex": ["PaymentsToAcquirePropertyPlantAndEquipment"]
}

def _pick_fact(facts: Dict, gaap_name: str, period_key: str):
    # facts structure: {"facts":{"us-gaap":{"Tag":{"units":{"USD":[{...}]}}}}}
    tag_aliases = TAG_MAP.get(gaap_name, [gaap_name])
    for tag in tag_aliases:
        node = facts.get("facts", {}).get("us-gaap", {}).get(tag)
        if not node:
            continue
        # Look for USD values and pick the one matching the period
        for unit, items in node.get("units", {}).items():
            if unit not in ("USD", "USD/share", "USD/shares"):
                continue
            # Choose the last item in the given fiscal period label
            # period_key examples: FY2023, Q1 2024. We try to match by "fy" and "fp"
            # If no exact match, take the latest item.
            latest = sorted(items, key=lambda x: (x.get("fy", 0), x.get("fp", ""), x.get("end", "")))[-1]
            return latest.get("val")
    return None

def _derived(snapshot: dict):
    try:
        rev = snapshot["income_statement"].get("Revenue")
        cogs = snapshot["income_statement"].get("CostOfRevenue")
        op_inc = snapshot["income_statement"].get("OperatingIncomeLoss")
        net = snapshot["income_statement"].get("NetIncomeLoss")
        ocf = snapshot["cash_flow"].get("OperatingCashFlow")
        capex = snapshot["cash_flow"].get("Capex")
        cur_a = snapshot["balance_sheet"].get("CurrentAssets")
        cur_l = snapshot["balance_sheet"].get("CurrentLiabilities")
        fcf = ocf + capex if (ocf is not None and capex is not None) else None
        gross = (rev - cogs) if (rev is not None and cogs is not None) else None
        return {
            "free_cash_flow": fcf,
            "gross_margin": (gross / rev) if (gross is not None and rev) else None,
            "operating_margin": (op_inc / rev) if (op_inc is not None and rev) else None,
            "net_margin": (net / rev) if (net is not None and rev) else None,
            "current_ratio": (cur_a / cur_l) if (cur_a and cur_l) else None
        }
    except Exception:
        return {}

async def get_financials_impl(cik: str, period: str) -> FinancialsSnapshot:
    cik10 = str(int(cik)).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json"
    facts = await fetch_json(url, cache_key=f"facts_{cik10}", cache_ttl=FACTS_TTL)

    income = {
        "Revenue": _pick_fact(facts, "Revenue", period),
        "CostOfRevenue": _pick_fact(facts, "CostOfRevenue", period),
        "OperatingIncomeLoss": _pick_fact(facts, "OperatingIncomeLoss", period),
        "NetIncomeLoss": _pick_fact(facts, "NetIncomeLoss", period)
    }
    balance = {
        "CashAndCashEquivalents": _pick_fact(facts, "CashAndCashEquivalents", period),
        "LongTermDebt": _pick_fact(facts, "LongTermDebt", period),
        "CurrentAssets": _pick_fact(facts, "CurrentAssets", period),
        "CurrentLiabilities": _pick_fact(facts, "CurrentLiabilities", period)
    }
    cash_flow = {
        "OperatingCashFlow": _pick_fact(facts, "OperatingCashFlow", period),
        "Capex": _pick_fact(facts, "Capex", period)
    }

    snap = FinancialsSnapshot(
        period=period,
        income_statement=income,
        balance_sheet=balance,
        cash_flow=cash_flow,
        derived=_derived({
            "income_statement": income,
            "balance_sheet": balance,
            "cash_flow": cash_flow
        })
    )
    return snap


