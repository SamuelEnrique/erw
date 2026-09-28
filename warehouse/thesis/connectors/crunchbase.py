"""Crunchbase (licensed; the user's own API key in CRUNCHBASE_API_KEY). Stub: fetch is not written (session 25)."""
from . import LicensedConnector


class Crunchbase(LicensedConnector):
    NAME = "Crunchbase"
    CREDENTIAL_ENV = "CRUNCHBASE_API_KEY"

    def to_landscape(self, rec):
        # fields as Crunchbase's organization entity names them (API v4 properties); to be confirmed when wired
        p = rec.get("properties", rec)
        total = p.get("funding_total") or {}
        return {"name": (p.get("identifier") or {}).get("value", "") if isinstance(p.get("identifier"), dict) else p.get("name", ""),
                "website": (p.get("website") or {}).get("value", "") if isinstance(p.get("website"), dict) else p.get("website", ""),
                "description": p.get("short_description", ""),
                "founders": "; ".join(f.get("value", "") for f in p.get("founder_identifiers", []) or []),
                "stage": p.get("last_funding_type", ""), "raised": str(total.get("value_usd", "")) if isinstance(total, dict) else "",
                "location": "; ".join(x.get("value", "") for x in p.get("location_identifiers", []) or []),
                "signal": "Crunchbase organization"}

    def to_capital(self, rec):
        p = rec.get("properties", rec)
        money = p.get("money_raised") or {}
        return {"date": p.get("announced_on", ""),
                "company": (p.get("funded_organization_identifier") or {}).get("value", ""),
                "kind": p.get("investment_type", ""), "amount": str(money.get("value", "")) if isinstance(money, dict) else "",
                "currency": money.get("currency", "") if isinstance(money, dict) else "",
                "investors": "; ".join(x.get("value", "") for x in p.get("investor_identifiers", []) or [])}
