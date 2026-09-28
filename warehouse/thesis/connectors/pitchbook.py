"""PitchBook (licensed; the user's own API key in PITCHBOOK_API_KEY). Stub: fetch is not written (session 25)."""
from . import LicensedConnector


class PitchBook(LicensedConnector):
    NAME = "PitchBook"
    CREDENTIAL_ENV = "PITCHBOOK_API_KEY"

    def to_landscape(self, rec):
        # fields as PitchBook's company profile names them; to be confirmed against a live response when wired
        return {"name": rec.get("companyName", ""), "website": rec.get("website", ""),
                "description": rec.get("description", ""), "founders": "; ".join(rec.get("founders", []) or []),
                "stage": rec.get("businessStatus", "") or rec.get("lastFinancingDealType", ""),
                "raised": str(rec.get("totalRaised", {}).get("amount", "")) if isinstance(rec.get("totalRaised"), dict) else "",
                "location": rec.get("hqLocation", ""), "signal": "PitchBook profile"}

    def to_capital(self, rec):
        return {"date": rec.get("dealDate", ""), "company": rec.get("companyName", ""), "kind": rec.get("dealType", ""),
                "amount": str(rec.get("dealSize", {}).get("amount", "")) if isinstance(rec.get("dealSize"), dict) else "",
                "currency": (rec.get("dealSize") or {}).get("currency", "") if isinstance(rec.get("dealSize"), dict) else "",
                "investors": "; ".join(rec.get("investors", []) or [])}
