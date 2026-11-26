"""Window D's data request 43 (the industry audit, finding 3): what SEDS's industrial average price (TEICD) divides by.
From the saved SEDS API answers (warehouse/raw/eia_seds_industrial): each series' own description and unit, and, for a
few states, expenditures over price (the implied denominator) against total consumption (TEICB). No request."""
import glob
import json

v, desc = {}, {}
for f in sorted(glob.glob("warehouse/raw/eia_seds_industrial/*/*")):
    if f.endswith("manifest.csv"):
        continue
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if not isinstance(d, dict) or not isinstance(d.get("response"), dict):
        continue
    for r in d["response"].get("data", []):
        s = r.get("seriesId")
        desc.setdefault(s, (r.get("seriesDescription"), r.get("unit")))
        v[(r.get("stateId"), str(r.get("period")), s)] = r.get("value")
for s in ("TEICB", "TEICV", "TEICD", "ESICB", "ESICV", "ESICD", "NGICV"):
    if s in desc:
        print(s, "|", *desc[s])
for st in ("TX", "LA", "CA", "OH", "US"):
    for y in ("2022", "2023"):
        try:
            B, V, D = (float(v[(st, y, k)]) for k in ("TEICB", "TEICV", "TEICD"))
        except (KeyError, TypeError, ValueError):
            print(st, y, "not all three held")
            continue
        den = V / D * 1000
        print(f"{st} {y}: TEICB {B:,.0f} billion Btu, TEICV {V:,.0f} million USD, TEICD {D}; V/B {V / B * 1000:.2f} USD/MMBtu; "
              f"V/D {den:,.0f} billion Btu = {100 * den / B:.1f} percent of TEICB")
