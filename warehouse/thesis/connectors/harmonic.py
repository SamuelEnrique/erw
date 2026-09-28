"""Harmonic (licensed; the user's own API key in HARMONIC_API_KEY). Stub: fetch is not written (session 25)."""
from . import LicensedConnector


class Harmonic(LicensedConnector):
    NAME = "Harmonic"
    CREDENTIAL_ENV = "HARMONIC_API_KEY"

    def to_landscape(self, rec):
        # fields as Harmonic's company record names them; to be confirmed against a live response when wired
        funding = rec.get("funding") or {}
        return {"name": rec.get("name", ""), "website": (rec.get("website") or {}).get("url", "") if isinstance(rec.get("website"), dict) else rec.get("website", ""),
                "description": rec.get("description", ""), "founders": "; ".join(p.get("name", "") for p in rec.get("people", []) or []),
                "stage": rec.get("stage", ""), "raised": str(funding.get("funding_total", "")),
                "location": (rec.get("location") or {}).get("city", "") if isinstance(rec.get("location"), dict) else "",
                "signal": "Harmonic record"}

    def to_capital(self, rec):
        return {"date": rec.get("announcement_date", ""), "company": rec.get("company_name", ""),
                "kind": rec.get("funding_round_type", ""), "amount": str(rec.get("funding_amount", "")),
                "currency": rec.get("funding_currency", ""), "investors": "; ".join(rec.get("investors", []) or [])}
