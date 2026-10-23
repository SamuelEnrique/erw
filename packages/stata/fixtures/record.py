#!/usr/bin/env python3
"""Session 1003 (chain 070): ten real answers of the live set, recorded as the Stata package's fixtures.

Energy Research Warehouse (ERW), docs/methods/packages.md. Each call is made once through the Python package
(erw.fetch with the live set as the session's backend); every address it requested is kept, and the same addresses are asked again for CSV
(Accept: text/csv), which is what the Stata and R packages read. Written: calls.json (each call's options, the
addresses, the rows the Python package returned, its version line) and one CSV a call (the pages joined, one header).
The anon key and the address come from the environment (ERW_LIVE_URL and ERW_LIVE_KEY, or SUPABASE_URL and
SUPABASE_ANON_KEY); neither is written. The project's address in each recorded address is replaced by <ERW_LIVE_URL>.

    python packages/stata/fixtures/record.py
"""

import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "package" / "src"))

import erw  # noqa: E402
from erw import live as L  # noqa: E402

CALLS = [
    {"table": "eia_fuel_spot_prices", "entity": ["eia:henry_hub"], "start": "2025-01-01", "end": "2026-01-01"},
    {"table": "eia_fuel_spot_prices", "entity": ["eia:wti_cushing", "eia:brent"], "start": "2026-09-01", "end": "2026-10-01"},
    {"table": "carbon_intensity_monthly", "entity": ["eia930:CISO"], "variable": ["intensity_demand"]},
    {"table": "ercot_peak_premium_annual", "entity": ["HB_HUBAVG"]},
    {"table": "caiso_grid_emergencies", "start": "2022-09-01", "end": "2022-09-15"},
    {"table": "eia860m_retired_generators"},
    {"table": "eia930_all_demand", "entity": ["eia930:ERCO"], "variable": ["demand_mw"], "start": "2026-10-18", "end": "2026-10-19"},
    {"table": "state_generation_mix_monthly", "entity": ["eia:TX"], "start": "2026-01-01"},
    {"table": "iso_curtailment_monthly", "start": "2026-01-01"},
    {"table": "carbon_intensity_daily", "entity": ["eia930:ERCO"], "start": "2026-10-01", "end": "2026-10-08"},
]


def main() -> int:
    erw.requests(reset=True)
    b = erw.LiveBackend()
    seen = []
    inner = b._get

    def recording(table, params):
        seen.append(L.live_url(b.url, table, params))
        return inner(table, params)

    b._get = recording
    erw.set_backend(b)
    b._catalogue()   # once, before the calls: the catalogue's address is not a call's
    out = []
    for i, c in enumerate(CALLS, 1):
        seen.clear()
        kw = {k: v for k, v in c.items() if k != "table"}
        df = erw.fetch(c["table"], **kw)   # the session's backend: this live set, its requests recorded
        urls = [u for u in seen if "/rest/v1/headers?" not in u]
        pages = []
        for u in urls:
            req = urllib.request.Request(u, headers={"apikey": b.key, "Authorization": f"Bearer {b.key}",
                                                     "Accept": "text/csv"})
            erw.api.counter.add("live")
            with urllib.request.urlopen(req, timeout=120) as r:
                pages.append(r.read().decode("utf-8"))
        head, body = None, []
        for p in pages:
            lines = p.splitlines()
            if lines:
                head = head or lines[0]
                body += lines[1:]
        name = f"{i:02d}_{c['table']}.csv"
        (HERE / name).write_text("\n".join([head or ""] + body) + "\n", encoding="utf-8", newline="\n")
        out.append({"n": i, "call": c, "addresses": [u.replace(b.url, "<ERW_LIVE_URL>") for u in urls],
                    "python_rows": len(df), "csv_rows": len(body), "file": name,
                    "version_line": df.attrs["erw"]["version_line"]})
        print(f"{name}: {len(df)} rows (Python), {len(body)} rows (CSV), {len(urls)} address(es)")
    (HERE / "calls.json").write_text(json.dumps({"recorded_by": "session 1003", "calls": out,
                                                 "requests": erw.requests()}, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
    print("requests:", erw.requests())
    return 0


if __name__ == "__main__":
    sys.exit(main())
