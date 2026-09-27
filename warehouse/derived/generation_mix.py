#!/usr/bin/env python3
"""Generation mix by state, monthly: EIA-923 energy sources grouped for the mix explorer.

Energy Research Warehouse (ERW), session 18 (platform tool 21, the energy mix explorer).
Implements docs/methods/generation_mix.md. Input: eia_state_generation_monthly (EIA,
Form EIA-923, all sectors), written by warehouse/connectors/eia_series.py. Output, through
the merge writer, one derived `series` table:

    state_generation_mix_monthly   freq P1M, MWh, entity eia:<state>, variable net_generation_<group>_mwh

    python warehouse/derived/generation_mix.py

Groups (EIA fueltypeid in brackets): coal (COW), natural_gas (NG), nuclear (NUC), hydro
(HYC), wind (WND), solar (SUN, utility scale), other_renewables (GEO, BIO), oil_and_other
(PET, OOG, HPS, OTH). A group is the sum of the sources EIA publishes for the month; a
source EIA lists without a value (withheld) adds nothing. not_itemized is EIA's all-fuels
total (ALL) minus the sum of the groups, written only when it is not zero to the nearest
MWh: the part of the total EIA does not itemize by source that month. So the groups plus
not_itemized equal EIA's ALL for every state and month, to the MWh. The small-scale solar
estimate (DPV) is not in ALL and not in any group; it stays in the input table.

Locations: the 50 states, DC, Puerto Rico where EIA lists it, and US; EIA's census regions
are left out. A month is written for a location only if EIA publishes ALL for it.
In CI the input is pulled by the same run (warehouse/run_daily.sh) before this script.
"""

import datetime as dt
import os
import re
import sys
import traceback
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "state_generation_mix_monthly"
INPUT = "eia_state_generation_monthly"
METHOD = "docs/methods/generation_mix.md"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/generation_mix.md"
SOURCE = "erw:generation_mix"
GROUPS = {
    "coal": ["COW"], "natural_gas": ["NG"], "nuclear": ["NUC"], "hydro": ["HYC"], "wind": ["WND"],
    "solar": ["SUN"], "other_renewables": ["GEO", "BIO"], "oil_and_other": ["PET", "OOG", "HPS", "OTH"],
}


def exact_sum(values):
    """Sum of the published numbers as decimals, so a total carries no float noise."""
    return sum((Decimal(str(v)) for v in values), Decimal(0))


def build(df, log):
    parts = df["entity"].str.split(":")
    df = df.assign(loc=parts.str[2], fuel=parts.str[3])
    df = df[df["loc"].str.fullmatch(r"[A-Z]{2}")]  # states, DC, PR and US; not census regions
    total = df[df["fuel"] == "ALL"].set_index(["loc", "ts_utc"])["value"]
    rows = []
    src = df.groupby(["loc", "ts_utc"])
    for (loc, ts), g in src:
        if (loc, ts) not in total.index:
            continue  # no EIA total for this location and month: nothing written
        by = dict(zip(g["fuel"], g["value"]))
        itemized = Decimal(0)
        for group, fuels in GROUPS.items():
            have = [by[f] for f in fuels if f in by]
            if not have:
                continue
            v = exact_sum(have)
            itemized += v
            rows.append((loc, f"net_generation_{group}_mwh", ts, v))
        rest = Decimal(str(total[(loc, ts)])) - itemized
        if abs(rest) >= Decimal("0.5"):
            rows.append((loc, "net_generation_not_itemized_mwh", ts, rest))
    out = pd.DataFrame(rows, columns=["loc", "variable", "ts_utc", "value"])
    out["value"] = [float(v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)) for v in out["value"]]
    n_rest = int((out["variable"] == "net_generation_not_itemized_mwh").sum())
    log(f"{len(out)} rows, {out['loc'].nunique()} locations, {out['ts_utc'].nunique()} months; "
        f"{n_rest} location-months with a not_itemized remainder")
    return out


def main():
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"generation_mix_{run_id}.log"))
    try:
        path = os.path.join(ip.OUT_DIR, INPUT + ".csv")
        if not os.path.exists(path):
            raise RuntimeError(f"input table absent: {INPUT} (warehouse/connectors/eia_series.py writes it)")
        df = ip.read_series(path, ip.SERIES_COLS)
        df["value"] = pd.to_numeric(df["value"])
        with open(path, encoding="utf-8") as f:
            retrieved = next((ln for ln in f if ln.startswith("# Retrieved:")), "# Retrieved: unknown")[2:].strip()
        reg = pd.read_csv(os.path.join(ip.METADATA_DIR, "sources.csv"), dtype=str, keep_default_na=False)
        lic = dict(zip(reg["source"], reg["license"]))
        srcs = sorted(set(df["source"]))
        missing = [s for s in srcs if s not in lic]
        if missing:
            raise RuntimeError(f"input sources {missing} are not in the registry; cannot set the license")
        license_ = "internal" if any(lic[s] == "internal" for s in srcs) else "public"
        out = build(df, log)
        geo = out["loc"].map(lambda x: "US" if x == "US" else f"US-{x}")
        s = pd.DataFrame({
            "entity": "eia:" + out["loc"], "variable": out["variable"], "ts_utc": out["ts_utc"],
            "value": out["value"], "unit": "MWh", "freq": "P1M", "geo": geo, "market": "", "node": "",
            "source": SOURCE, "source_url": METHOD_URL, "retrieved_at": ip.utc_iso(pd.Timestamp.now(tz="UTC")),
            "vintage": "",
        }).sort_values(["entity", "variable", "ts_utc"])
        header = [
            "Energy Research Warehouse (ERW): Net generation mix by state, grouped energy sources, monthly, "
            "MWh (derived from EIA Form EIA-923; platform tool 21)",
            "Shape: series (docs/datastandard.md v0). freq P1M: ts_utc is the first of the month, 00:00:00Z. "
            "entity eia:<state> (US for the nation); variable net_generation_<group>_mwh.",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/generation_mix.py",
            f"Run log: warehouse/output/logs/generation_mix_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, generation mix method ({METHOD}), {METHOD_URL}",
            f"Derived from: {INPUT}",
            f"  input sources: {'; '.join(srcs)}; input {retrieved}",
            "Groups: " + "; ".join(f"{g} = {' + '.join(f)}" for g, f in GROUPS.items())
            + ". not_itemized = EIA ALL minus the groups, when not zero to the MWh. Groups plus "
            "not_itemized equal EIA's all-fuels total. Small-scale solar (DPV) is not included.",
            f"License: {license_}. A derived table inherits the most restrictive license of its inputs "
            "(Decision 23).",
        ]
        ip.write_csv(s[ip.SERIES_COLS], NAME, header, log)
        ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                report="Generation mix by state (docs/methods/generation_mix.md)",
                                report_url=METHOD_URL, document_list=METHOD, license=license_,
                                tables=[NAME])])
        status = [dict(table=NAME, market="", status="ok", detail=f"{len(s)} rows")]
    except Exception:
        tb = ip.redact(traceback.format_exc())
        last = tb.strip().splitlines()[-1]
        log(f"FAILED, no output file written:\n{tb}")
        print(f"generation_mix FAILED, no output file written: {last}", file=sys.stderr)
        status = [dict(table=NAME, market="", status="failed", detail=last[:300])]
    ip.write_status("generation_mix", run_id, status)
    log.close()
    print(f"generation_mix run log: {os.path.relpath(log.path, ip.ROOT)}")
    return 1 if status[0]["status"] == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
