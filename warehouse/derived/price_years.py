#!/usr/bin/env python3
"""The price years: each economics page's figure under every window of years held (session 357).

Energy Research Warehouse (ERW) derived table, public: warehouse/output/price_years_by_window.csv. For each tool
(What a battery earns, What a generator earns, What a datacenter pays), grid, price point, configuration the page
offers and window (each calendar year held, the last twelve months, the three-year and seven-year averages of full
years, the whole span held, and the whole span without each stress event of the grid), the revenue or cost per unit
the page's own aggregation gives, the months counted and the span. Shape and windows: docs/methods/price_years.md.

The figures are the pages' own arithmetic, not a copy of it: site/scripts/price-years.mjs imports lib/batterystack.ts,
lib/merchant.ts, lib/seller2.ts and lib/datacenter.ts as the pages do and runs them over what the pages read:

    battery     ERCOT and CAISO: battery_stack_monthly and battery_stack_stress_daily from the live set, with the anon
                key, as app/cost-of-power/battery/read.ts reads them (the live set is loaded by the daily run and can be
                newer than this machine's copy of the tables: on 20 October 2026 it held CAISO's 2 November 2025, which
                this machine's copy left out); SPP, a grid in review: site/data/battery_stack_review.json
    generator   site/data/merchant_snapshot.json (written by warehouse/derived/merchant_revenue.py)
    datacenter  site/data/datacenter/<grid>_<year>.json and index.json (written by warehouse/derived/datacenter_page.py)

The run proves the table against the pages for the default window (the last twelve months): the battery's figure
against the page's own check-key stat (lib/batterystack.ts stat "l12_kw:total") on the same rows, and, with --live,
against a second read of the live set by site/scripts/price-years-live.mjs. Grids: ERCOT, CAISO and SPP. NYISO, ISO-NE and MISO need a license
from 21 October 2026 or are paused (warehouse/metadata/license_status.csv); PJM's prices are licensed.

    python warehouse/derived/price_years.py            # the table (data lock)
    python warehouse/derived/price_years.py --live     # and prove the battery's default against the live set
    python warehouse/derived/price_years.py --out-dir DIR   # a trial, no data lock
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback

from urllib.parse import urlparse

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE = os.path.join(ROOT, "site")
sys.path.insert(0, os.path.join(HERE, "..", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "price_years_by_window"
SOURCE = "erw:price_years"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_years.md"
X_COLS = ["x_tool", "x_grid", "x_config", "x_window", "x_window_kind", "x_left_out", "x_from", "x_to", "x_months", "x_complete"]
COLS = ip.SERIES_COLS + X_COLS
GRIDS = ["ercot", "caiso", "spp"]
GEO = {"ercot": "US-TX", "caiso": "US-CA", "spp": "US-KS,US-NE,US-NM,US-OK,US-TX"}
# the battery's grids: the table and entity each is read from, as /cost-of-power/battery reads them
BATTERY = {
    "ercot": dict(table="battery_stack_monthly", entity="ercot:HB_HUBAVG", node="HB_HUBAVG", live=True),
    "caiso": dict(table="battery_stack_monthly", entity="caiso:TH_SP15_GEN-APND", node="TH_SP15_GEN-APND", live=True),
    "spp": dict(table="battery_stack_review_monthly", entity="spp:SPPNORTH_HUB", node="SPPNORTH_HUB", live=False),
}
STRESS = "battery_stack_stress_daily"
REVIEW = os.path.join(SITE, "data", "battery_stack_review.json")
CENT = 0.005  # the proof's tolerance: half a cent per kW


def live_rows(table, entity, select):
    """Every row of one entity of a live-set table, read with the anon key as the site reads it (lib/supabase.ts:
    the series table, the URL's origin, a thousand rows a page)."""
    url, key = ip.load_key("SUPABASE_URL"), ip.load_key("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY is not set: the battery page's rows cannot be read")
    u = urlparse(url)
    base = f"{u.scheme}://{u.netloc}"
    out = []
    for offset in range(0, 1_000_000, 1000):
        r = requests.get(f"{base}/rest/v1/series", params=dict(select=select, table_name=f"eq.{table}", entity=f"eq.{entity}", order="variable,ts_utc",
                                                               limit=1000, offset=offset), headers=dict(apikey=key, Authorization=f"Bearer {key}"), timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"the live set answered {r.status_code} for {table} {entity}: {r.text[:200]}")
        page = r.json()
        out += page
        if len(page) < 1000:
            return out
    raise RuntimeError(f"{table} {entity}: more than a million rows")


def battery_input():
    """The battery's rows per grid, as the page reads them (app/cost-of-power/battery/read.ts): a ready grid's rows of
    battery_stack_monthly and battery_stack_stress_daily from the live set; a grid in review from the committed
    snapshot site/data/battery_stack_review.json. And each ready grid's stress days by event (the battery page's
    leave-out boxes), for the datacenter's leave-out windows."""
    out, events, read_at = {}, {}, {}
    with open(REVIEW, encoding="utf-8") as f:
        review = json.load(f)
    for grid, b in BATTERY.items():
        if b["live"]:
            rows = [dict(variable=r["variable"], ts_utc=r["ts_utc"], value=float(r["value"])) for r in live_rows(b["table"], b["entity"], "variable,ts_utc,value")]
            s = live_rows(STRESS, b["entity"], "variable,ts_utc,value,event")
            stress = [dict(variable=r["variable"], ts_utc=r["ts_utc"], value=float(r["value"]), event=r["event"] or "") for r in s]
            days = {}
            for r in stress:
                if r["event"]:
                    days.setdefault(r["event"], set()).add(r["ts_utc"][:10])
            events[grid] = {e: sorted(v) for e, v in sorted(days.items())}
            read_at[grid] = f"the live set, {b['table']} and {STRESS}, read {ip.utc_iso(pd.Timestamp.now(tz='UTC'))}"
        else:
            g = review["grids"].get(grid)
            if not g or g["entity"] != b["entity"]:
                raise RuntimeError(f"{REVIEW} holds no grid {grid} at {b['entity']}")
            rows = [dict(variable=v, ts_utc=t, value=float(x)) for v, t, x in g["rows"]]
            stress = []
            read_at[grid] = f"site/data/battery_stack_review.json ({review['table']}, built {review['built']})"
        if not rows:
            raise RuntimeError(f"{b['table']} holds no row of {b['entity']}")
        # the live set writes 2025-11-01T00:00:00+00:00; the page reads the month from the first seven characters, and
        # the table's own convention is the Z form
        for r in rows + stress:
            r["ts_utc"] = r["ts_utc"][:19] + "Z" if r["ts_utc"].endswith("+00:00") else r["ts_utc"]
        out[grid] = dict(entity=b["entity"], node=b["node"], rows=rows, stress=stress)
    return out, events, read_at


def node_bin():
    exe = shutil.which("node")
    if not exe:
        raise RuntimeError("node is not on this machine's path: the pages' own code cannot be run")
    return exe


def compute(log=print):
    battery, events, read_at = battery_input()
    with tempfile.TemporaryDirectory(prefix="erw_price_years_") as tmp:
        src, dst = os.path.join(tmp, "in.json"), os.path.join(tmp, "out.json")
        with open(src, "w", encoding="utf-8") as f:
            json.dump(dict(grids=GRIDS, battery=battery, events=events), f)
        r = subprocess.run([node_bin(), "--import", "./scripts/alias-register.mjs", "scripts/price-years.mjs", src, dst],
                           cwd=SITE, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        if r.returncode != 0:
            raise RuntimeError(f"site/scripts/price-years.mjs exited {r.returncode}: {(r.stderr or r.stdout).strip()[-800:]}")
        log("  " + r.stdout.strip())
        with open(dst, encoding="utf-8") as f:
            res = json.load(f)
    return res, events, read_at


def frame(res, retrieved):
    out = []
    for o in res["rows"]:
        months = (int(o["to"][:4]) - int(o["from"][:4])) * 12 + int(o["to"][5:7]) - int(o["from"][5:7]) + 1
        out.append(dict(
            entity=o["entity"], variable=f"{o['tool']}_{o['config']}_{o['window']}", ts_utc=f"{o['from']}-01T00:00:00Z",
            value=round(float(o["value"]), 6), unit=o["unit"], freq=f"P{months}M", geo=GEO[o["grid"]], market=o["grid"], node=o["node"],
            source=SOURCE, source_url=METHOD_URL, retrieved_at=retrieved, vintage="",
            x_tool=o["tool"], x_grid=o["grid"], x_config=o["config"], x_window=o["window"], x_window_kind=o["kind"],
            x_left_out="+".join(o["leftOut"]) if o["leftOut"] else "none", x_from=o["from"], x_to=o["to"],
            x_months=int(o["months"]), x_complete="true" if o["complete"] else "false"))
    s = pd.DataFrame(out, columns=COLS)
    dup = s.duplicated(["entity", "variable", "ts_utc"]).sum()
    if dup:
        raise RuntimeError(f"{dup} duplicate keys in the table")
    return s.sort_values(["x_tool", "x_grid", "entity", "variable"]).reset_index(drop=True)


def prove(s, res, log=print):
    """The default window against the pages' own figure: every proof the node run returned, to the cent."""
    lines, bad = [], []
    for p in res["proofs"]:
        if p["tool"] == "datacenter":
            ent = s[(s.x_tool == "datacenter") & (s.x_grid == p["grid"]) & (s.node == p["region"]) & (s.x_config == p["config"]) & (s.x_window == "last_12")]
        else:
            ent = s[(s.x_tool == p["tool"]) & (s.x_grid == p["grid"]) & (s.x_config == p["config"]) & (s.x_window == "last_12")]
        v = float(ent["value"].iloc[0]) if len(ent) == 1 else None
        ok = v is not None and p["page"] is not None and abs(v - p["page"]) < CENT
        lines.append(f"{p['tool']} {p['grid']} {p['config']}{(' ' + p['region']) if p.get('region') else ''}: table {v}, page ({p['stat']}) {p['page']}: {'equal' if ok else 'DIFFERENT'}")
        if not ok:
            bad.append(lines[-1])
    for line in lines:
        log("  proof: " + line)
    if bad:
        raise RuntimeError(f"{len(bad)} figures differ from the page's own: {bad[0]}")
    return lines


def prove_live(s, log=print):
    """The battery's default (ERCOT, 4 hours, perfect foresight) against the rows the page reads from the live set,
    through the page's own function (site/scripts/price-years-live.mjs)."""
    r = subprocess.run([node_bin(), "--import", "./scripts/alias-register.mjs", "scripts/price-years-live.mjs"], cwd=SITE,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"site/scripts/price-years-live.mjs exited {r.returncode}: {(r.stderr or r.stdout).strip()[-500:]}")
    live = json.loads(r.stdout.strip().splitlines()[-1])
    out = []
    for k, page in live.items():
        grid, config = k.split("|")
        ent = s[(s.x_tool == "battery") & (s.x_grid == grid) & (s.x_config == config) & (s.x_window == "last_12")]
        v = float(ent["value"].iloc[0]) if len(ent) == 1 else None
        ok = v is not None and page is not None and abs(v - page) < CENT
        out.append(f"battery {grid} {config}: table {v}, the live set through the page's stat {page}: {'equal' if ok else 'DIFFERENT'}")
        log("  live proof: " + out[-1])
        if not ok:
            raise RuntimeError(out[-1])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the price years, each economics page's figure under every window of years held (session 357)")
    ap.add_argument("--out-dir", help="write here instead of warehouse/output (a trial: no data lock)")
    ap.add_argument("--live", action="store_true", help="also prove the battery's default window against the live set's rows")
    a = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    retrieved = ip.utc_iso(pd.Timestamp.now(tz="UTC"))
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        res, events, read_at = compute(log=log)
        s = frame(res, retrieved)
        proofs = prove(s, res, log=log)
        if a.live:
            proofs += prove_live(s, log=log)
        n = s.groupby("x_tool").size().to_dict()
        ev = "; ".join(f"{g}: {', '.join(e)}" for g, e in events.items())
        header = [
            "Energy Research Warehouse (ERW): the price years, each economics page's figure under every window of years held (derived, session 357)",
            "Shape: series (docs/datastandard.md v0), partition column market (the grid). variable <tool>_<config>_<window>, also in x_tool, x_config and x_window; ts_utc the window's "
            "first month (the first day of the local month at 00:00:00Z); freq P<n>M, the calendar months the window spans; value USD/kW-year (battery: total revenue; generator: "
            "revenue, the peaker's margin over fuel and variable O&M) or USD/MWh (datacenter: what the load paid per MWh consumed). x_window_kind year, last_12, avg_3y, avg_7y, "
            "all, all_less; x_left_out the stress events taken out; x_from and x_to the first and last month; x_months the months counted by the page's rule; x_complete false "
            "for a calendar year held in part.",
            "Computed by the pages' own code: site/scripts/price-years.mjs runs lib/batterystack.ts, lib/merchant.ts with lib/seller2.ts, and lib/datacenter.ts over what each page "
            f"reads. Rows: battery {n.get('battery', 0)}, generator {n.get('generator', 0)}, datacenter {n.get('datacenter', 0)}.",
            "Inputs: the battery's rows as its page reads them: " + "; ".join(f"{g} from {w}" for g, w in read_at.items()) + ". "
            f"The generator's snapshot built {res['inputs']['snapshot']}; the datacenter's year files built {res['inputs']['datacenter']}. Stress events (the battery page's "
            f"leave-out boxes, from battery_stack_stress_daily): {ev}; SPP has none. The generator's leave-outs are ERCOT's three, from its snapshot's own daily figures.",
            "Proof of the default window, to the cent: " + " | ".join(proofs),
            f"Retrieved: {run_id} (UTC) by warehouse/derived/price_years.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
            f"Source: {SOURCE} ERW derived table, the price years (docs/methods/price_years.md), {METHOD_URL}",
            "Derived from: battery_stack_monthly; battery_stack_review_monthly; battery_stack_stress_daily; merchant_revenue_monthly; ercot_all_hub_prices_history; "
            "ercot_zone_prices_history; iso_dam_hub_prices; iso_hub_prices_history; iso_rtm_hub_prices",
            "  the battery's through the live set and site/data/battery_stack_review.json; the generator's through site/data/merchant_snapshot.json; the datacenter's "
            "through site/data/datacenter (ERCOT, CAISO and SPP's rows only)",
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23): ERCOT, CAISO (credit the California ISO), SPP. NYISO, ISO-NE "
            "and MISO are left out (license needed from 2026-10-21, or paused); PJM's prices are licensed.",
        ]
        if a.out_dir:
            os.makedirs(a.out_dir, exist_ok=True)
            path = os.path.join(a.out_dir, NAME + ".csv")
            with open(path, "w", encoding="utf-8", newline="") as f:
                for line in header:
                    f.write("# " + line + "\n")
                s.to_csv(f, index=False, lineterminator="\n")
            print(f"{NAME}: trial written to {path}")
        else:
            path = os.path.join(ip.OUT_DIR, NAME + ".csv")
            if os.path.exists(path):
                os.remove(path)  # rebuilt whole from its inputs each run
            ip.write_csv(s, NAME, header, log, cols=COLS)
            ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                                    report="The price years, each economics page's figure under every window of years held (warehouse/derived/price_years.py)",
                                    report_url=METHOD_URL, document_list="", license="public", tables=[NAME])])
        msg = f"{len(s)} rows (battery {n.get('battery', 0)}, generator {n.get('generator', 0)}, datacenter {n.get('datacenter', 0)}); {len(proofs)} proofs equal"
        log(msg)
        print(f"{NAME}: {msg}")
        results.append(dict(table=NAME, market="derived", status="ok", detail=msg))
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"{NAME} FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="derived", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    if not a.out_dir:
        ip.write_status(NAME, run_id, results)
    log.close()
    return 0 if all(r["status"] == "ok" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
