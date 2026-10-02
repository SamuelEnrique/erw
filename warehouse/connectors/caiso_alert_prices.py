#!/usr/bin/env python3
"""CAISO day-ahead hub prices on alert and emergency days (session 60, approved pull b, the Flex Alert scorecard).

Energy Research Warehouse (ERW) connector. Writes one series table, history (not in the Supabase live set):

    warehouse/output/caiso_dam_alert_day_hub_prices.csv   lmp_dam, USD/MWh, hourly, TH_SP15_GEN-APND and TH_NP15_GEN-APND

for the local (Pacific) days the scorecard needs (warehouse/derived/flex_alert_scorecard.py --days): every day since
2018-07 with a CAISO notice in caiso_grid_emergencies (any type, any region), and the model's comparison days, the
hottest tenth of non-alert days it holds out to measure its error. The days are scattered, so the table is not a
window: its header lists how many days it holds.

    python warehouse/connectors/caiso_alert_prices.py

The pull is iso_prices.py's CAISO pull (OASIS PRC_LMP, market DAM, via gridstatus, raw responses saved under
warehouse/raw/caiso_alert_prices/), one day at a time, one request at a time (CAISO's server is slow and resets under
parallel load), each day written as soon as it is complete (both hubs, all hours), so an interrupted pull resumes at the
first day the table does not hold and never starts again. A day CAISO does not complete is recorded and not written.
Ceiling 60,000 rows: the pull stops before a day would pass it. OASIS serves about 39 months of history: days before that
are recorded in the header as not served and are not requested (session 60: 34 of the 38 alert days are older). License: CAISO's Privacy and Terms of Use (credit the
California ISO), as for the live hub tables.
"""

import datetime as dt
import os
import subprocess
import sys
import traceback

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import iso_prices as ip  # noqa: E402

NAME = "caiso_dam_alert_day_hub_prices"
HUBS = ["TH_NP15_GEN-APND", "TH_SP15_GEN-APND"]
CEILING = 60_000
TZ = "America/Los_Angeles"
OASIS_MONTHS = 39  # the history OASIS serves (CAISO: OASIS keeps 39 months)


def wanted_days():
    r = subprocess.run([sys.executable, os.path.join(ip.ROOT, "warehouse", "derived", "flex_alert_scorecard.py"), "--days"],
                       capture_output=True, text=True, cwd=ip.ROOT)
    if r.returncode != 0:
        raise RuntimeError(f"flex_alert_scorecard.py --days: {r.stderr.strip()[-300:]}")
    return [d.strip() for d in r.stdout.splitlines() if d.strip()]


def held_days():
    path = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if not os.path.exists(path):
        return set(), 0
    s = ip.read_series(path)
    t = pd.to_datetime(s["ts_utc"], utc=True).dt.tz_convert(TZ).dt.strftime("%Y-%m-%d")
    return set(t), len(s)


def spec():
    """The DAM spec of iso_prices.pull_caiso, with the node list narrowed to the two hubs (captured, not run)."""
    got = {}
    ip.CAISO_HUBS = HUBS  # pull_caiso reads its node list at call time
    orig = ip.run_iso
    ip.run_iso = lambda ctx, specs: got.update(ctx=ctx, specs=specs) or 0
    try:
        ctx = dict(iso="caiso", reports={})
        ip.pull_caiso(ctx)
    finally:
        ip.run_iso = orig
    s = next(x for x in got["specs"] if x["name"] == "DAM")
    return got["ctx"], dict(s, nodes=HUBS)


def header(run_id, days, n_rows, gaps, reports):
    return [
        "Energy Research Warehouse (ERW): CAISO day-ahead LMPs at the SP15 and NP15 hubs on alert and emergency days and the Flex "
        "Alert scorecard's comparison days (session 60)",
        "Shape: series (docs/datastandard.md v0), partition column market (caiso_dam). lmp_dam, USD/MWh, hourly; ts_utc the interval "
        "start, UTC. Days: the Pacific days warehouse/derived/flex_alert_scorecard.py --days lists (every CAISO notice day since "
        "2018-07, and the held-out hottest tenth of non-alert days); scattered days, not a window.",
        f"Holds {days} days, {n_rows:,} rows, of the {CEILING:,}-row ceiling (approved pull b). Days CAISO left incomplete, not written: "
        + ("; ".join(gaps) if gaps else "none") + ".",
        f"Retrieved: {run_id} (UTC) by warehouse/connectors/caiso_alert_prices.py; earlier days by earlier runs (resumed)",
        f"Run log: warehouse/output/logs/caiso_alert_prices_{run_id}.log",
        "Raw files: warehouse/raw/caiso_alert_prices/<run>/ (not in git)",
    ] + [f"Source: {sid} {name}, {page}" for sid, (name, page) in reports.items() if sid == "caiso:PRC_LMP"] + [
        "License: public. CAISO's Privacy and Terms of Use (https://www.caiso.com/privacy-terms-of-use): credit the California ISO.",
    ]


def main():
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"caiso_alert_prices_{run_id}.log"))
    ip.RAW.open("caiso_alert_prices", run_id)
    results, gaps = [], []
    try:
        days = wanted_days()
        have, n_rows = held_days()
        # session 60: OASIS serves about 39 months of history. A request for 2022-09-06 answered "No data returned for the
        # specified selection" (ERR_CODE 1000) under report versions 1 and 12, while 2023-07-25 answered with prices; so
        # a day before the window is recorded as not served and not requested.
        cutoff = (pd.Timestamp.now(tz=TZ).normalize() - pd.DateOffset(months=OASIS_MONTHS)).strftime("%Y-%m-%d")
        old = [d for d in days if d < cutoff and d not in have]
        if old:
            gaps.append(f"{len(old)} days before {cutoff}, outside OASIS's {OASIS_MONTHS}-month history ({old[0]} to {old[-1]}): not served, not requested")
            log(f"{len(old)} wanted days are before {cutoff}, outside OASIS's history: not requested")
        todo = [d for d in days if d not in have and d >= cutoff]
        log(f"ERW caiso_alert_prices run {run_id}: {len(days)} days wanted, {len(have & set(days))} held, {len(todo)} to pull; "
            f"{n_rows:,} rows held, ceiling {CEILING:,}")
        ctx, sp = spec()
        geo = ip.ISOS["caiso"][3]
        written = 0
        for i, day in enumerate(todo, 1):
            per_day = 24 * len(HUBS) + 2 * len(HUBS)  # a 25-hour day at most
            if n_rows + per_day > CEILING:
                log(f"STOP before {day}: {n_rows:,} rows held, one more day would pass the {CEILING:,} ceiling")
                gaps.append(f"{day} (ceiling)")
                break
            d = pd.Timestamp(day)
            d0, d1 = d.tz_localize(TZ), (d + pd.Timedelta(days=1)).tz_localize(TZ)
            try:
                rows, _ = ip.pull_days([d], sp["fetch"], HUBS, sp["source"], sp["page"], log, what="DAM", data_url=ctx.get("data_url"))
                rows = rows[(rows["interval_start"] >= d0) & (rows["interval_start"] < d1)]
                rows = ip.latest_per_key(rows, log)
                ip.check_interval_length(rows, 60, log)
                ip.check_complete(rows, HUBS, d0, d1, "1h", log)
            except Exception as exc:
                reason = " ".join(str(exc).split())[:200]
                gaps.append(f"{day} ({reason})")
                log(f"  GAP {day}: not written ({reason})")
                continue
            s = ip.to_series(rows, "caiso", sp["variable"], sp["freq"], sp["market"], geo)
            n_rows += len(s)
            ip.write_csv(s, NAME, header(run_id, len(have) + written + 1, n_rows, gaps, ctx["reports"]), log)
            written += 1
            log(f"  {day}: {len(s)} rows ({i} of {len(todo)}); {n_rows:,} held")
        have, n_rows = held_days()
        path = os.path.join(ip.OUT_DIR, NAME + ".csv")
        if n_rows:  # the header once more, with every gap of this run (the data lines unchanged)
            ip._require_lock(path, f"writing {NAME}")
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
            keep = [ln for ln in lines if ln.startswith("# File holds")]
            body = [ln for ln in lines if not ln.startswith("#")]
            with open(path + ".tmp", "w", encoding="utf-8", newline="") as f:
                f.writelines([f"# {h}\n" for h in header(run_id, len(have), n_rows, gaps, ctx["reports"])] + keep + body)
            os.replace(path + ".tmp", path)
        ip.update_sources([dict(source="caiso:PRC_LMP", publisher=ip.ISO_PUBLISHERS.get("caiso", "California ISO"),
                                report=ctx["reports"]["caiso:PRC_LMP"][0], report_url=ctx["reports"]["caiso:PRC_LMP"][1],
                                document_list="", tables=[NAME])])
        missing = [d for d in days if d not in have]
        msg = f"{written} days written this run; {len(have)} held, {n_rows:,} rows; {len(missing)} wanted days not held"
        results.append(dict(table=NAME, market="caiso_dam", status="ok" if not missing else "gap", detail=msg))
        log(msg)
        print(f"caiso_alert_prices: {msg}")
    except Exception:
        tb = ip.redact(traceback.format_exc())
        log(f"FAILED:\n{tb}")
        print(f"caiso_alert_prices FAILED: {tb.strip().splitlines()[-1]}", file=sys.stderr)
        results.append(dict(table=NAME, market="caiso_dam", status="failed", detail=tb.strip().splitlines()[-1][:300]))
    ip.write_status("caiso_alert_prices", run_id, results)
    log.close()
    return 0 if all(r["status"] != "failed" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
