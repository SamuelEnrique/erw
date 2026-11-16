#!/usr/bin/env python3
"""Interconnection queue statistics by ISO and entry year (session 348): the table iso_queue_statistics.

Energy Research Warehouse (ERW). For each ISO whose queue the ERW holds and each year a position entered it: how many
positions entered, how many were withdrawn, how many reached operation and how many are still waiting, the MW of each,
the withdrawal rate, and the median and mean years from entry to operation for the positions that reached it. Every
rule is in docs/methods/energy_projects.md, "Queue statistics" (session 348).

The chain prompt names the table queue_statistics; a series table's name has three parts (docs/datastandard.md), so it
is iso_queue_statistics. Its entities begin with the ISO (ercot:queue_2019), so the site holds a licensed grid's rows
as it holds any table decided by grids (site/lib/license.ts).

    python warehouse/derived/queue_statistics.py                              # reads warehouse/output
    python warehouse/derived/queue_statistics.py --inputs runs/archive_restore  # the archive's copies (restore.py)

What counts, in each ISO's own words (the queue connector's STATUS_MAP, warehouse/connectors/iso_queues.py):
- withdrawn: CAISO WITHDRAWN; NYISO, MISO and ISO-NE Withdrawn; SPP WITHDRAWN and TERMINATED. ERCOT's GIS report
  lists active and completed positions only, so ERCOT has no withdrawn count and no withdrawal rate: not held.
- operating: ERCOT, NYISO and ISO-NE Completed; CAISO COMPLETED; MISO Done and LEGACY: Done; SPP IA FULLY
  EXECUTED/COMMERCIAL OPERATION.
  Session 7022: ERCOT's "Completed" was gridstatus's word for a filled "IA Signed" day, a signed agreement; from the
  queue connector's next pull ERCOT is operating only with its day of approval to synchronize (iso_status "Approved for
  Synchronization"), and a signed agreement alone is waiting ("IA Signed"). The pulls before it still count the
  agreements as operating; the statistics follow the queue table as pulled.
- still waiting: every other status of the map (active or suspended): ERCOT and CAISO and NYISO and ISO-NE Active; MISO
  Active, Pending Revision Approval, Pending Transfer; SPP's study stages, IA PENDING, IA FULLY EXECUTED/ON SCHEDULE and
  ON SUSPENSION.
- a position with no status (SPP's affected-system requests, and rows an ISO lists without one) is counted apart,
  status not stated, and is in none of the three.
- the entry year is the year of the ISO's queue date; a position with no queue date is counted apart (no year).
- the wait is the years from the queue date to the in-service date (days / 365.25), for operating positions with both
  dates and an in-service date on or after the queue date. MISO's and ISO-NE's tables hold no in-service date, so they
  have no wait. SPP's date is its "Commercial Operation Date", filled for active and withdrawn positions too: for an
  operating position it may be the date requested rather than achieved, and its rows say so.
- MW is the capacity the queue states (a repowering request may be negative), summed; a position with no MW is counted
  in the positions and not in the MW.
"""

import argparse
import datetime as dt
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "iso_queue_statistics"
ISOS = ["ercot", "caiso", "nyiso", "miso", "spp", "isone"]
LABEL = {"ercot": "ERCOT", "caiso": "CAISO", "nyiso": "NYISO", "miso": "MISO", "spp": "SPP", "isone": "ISO-NE"}
NO_WITHDRAWN = {"ercot"}               # the GIS report lists active and completed positions only
NO_IN_SERVICE = {"miso", "isone"}      # their tables hold no in-service date
REQUESTED_COD = {"spp"}                # the date may be requested rather than achieved
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/energy_projects.md"  # no fragment: a "#" in a row ends it for a reader that skips comments
X_COLS = ["x_iso", "x_entry_year", "x_rule", "x_input_run"]


def stats(q, iso):
    """{variable: (value, unit)} for one ISO's positions of one entry year."""
    s = q["status"].fillna("")
    mw = pd.to_numeric(q["capacity_mw"], errors="coerce")
    out = {}
    groups = {"entered": pd.Series(True, index=s.index), "operating": s == "completed", "waiting": s.isin(["active", "suspended"]),
              "status_not_stated": s == ""}
    if iso not in NO_WITHDRAWN:
        groups["withdrawn"] = s == "withdrawn"
    for k, m in groups.items():
        out[f"positions_{k}"] = (float(m.sum()), "count")
        # session 7015 (done-line request 17): no position is 0 MW, not "not held"; positions without a figure stay unwritten
        out[f"mw_{k}"] = (0.0 if not m.any() else float(mw[m].sum(min_count=1)) if mw[m].notna().any() else None, "MW")
    if "withdrawn" in groups and out["positions_entered"][0]:
        out["withdrawal_rate"] = (out["positions_withdrawn"][0] / out["positions_entered"][0], "ratio")
    if iso not in NO_IN_SERVICE:
        op = q[s == "completed"]
        qd = pd.to_datetime(op["queue_date"], errors="coerce")
        sd = pd.to_datetime(op["actual_in_service_date"], errors="coerce")
        yrs = ((sd - qd).dt.days / 365.25)[qd.notna() & sd.notna() & (sd >= qd)]
        out["wait_positions"] = (float(len(yrs)), "count")
        if len(yrs):
            out["wait_years_median"] = (float(yrs.median()), "year")
            out["wait_years_mean"] = (float(yrs.mean()), "year")
    return {k: v for k, v in out.items() if v[0] is not None}


# Session 7022 (chain 301, done-line request 41): the same figures by technology group beside the rows for all, so the
# explorer can be asked about storage alone. Each queue's own words in fuel_technology are read as parts (a part is
# solar, storage, wind or gas, or something else); a position is solar, storage, wind or gas when every part it names is
# that one; solar_storage when it names solar and storage and nothing else; other when it names anything else or more;
# not_stated when the queue gives no words. The words of each part, from the six queues as pulled on 5 November 2026:
TECH_GROUPS = ["storage", "solar", "solar_storage", "wind", "gas", "other", "not_stated"]
TECH_PART_WORDS = {
    "solar": ("solar", "photovoltaic", "sun"),            # ISO-NE's code SUN; Solar Thermal is solar too
    "storage": ("storage", "battery", "bat", "flywheel"),  # ISO-NE's code BAT; pumped storage and compressed air storage
    "wind": ("wind", "wnd"),                              # ISO-NE's code WND
    "gas": ("gas", "ng", "combined cycle", "combined-cycle", "combustion turbine", "combustion (gas) turbine", "gas turbine",
            "ct", "ctg", "cc", "reciprocating", "dual fuel"),
}
FAMILY_WORDS = {"other", "thermal", "hybrid"}
TECH_RULE = "the queue's fuel_technology read by warehouse/derived/queue_statistics.py technology_group"
# ISO-NE's codes (EIA's energy source codes): the four the groups name, the oils, and the rest (other)
ISONE_CODES = {"SUN": "solar", "BAT": "storage", "WND": "wind", "NG": "gas",
               "DFO": "oil", "KER": "oil", "JF": "oil", "WO": "oil", "RFO": "oil",
               "WAT": "other", "WDS": "other", "LFG": "other", "BIT": "other", "NUC": "other", "FC": "other", "MSW": "other",
               "BLQ": "other", "OTH": "other", "SUB": "other"}


def technology_parts(text):
    """The parts a queue's fuel_technology names, as a set of solar, storage, wind, gas and other (empty: no words)."""
    t = " ".join(str(text or "").replace("=", " ").split()).lower()
    if not t or t in ("nan", "none"):
        return set()
    parts, family = set(), False
    # ISO-NE writes EIA's fuel codes, one word each ("SUN BAT", "DFO NG"): each code is a part; oil codes beside
    # natural gas are its backup fuel (a dual-fuel plant is a gas plant, as NYISO's "Dual Fuel")
    codes = t.upper().split()
    if codes and all(c in ISONE_CODES for c in codes):
        got = {ISONE_CODES[c] for c in codes}
        if "gas" in got and got <= {"gas", "oil"}:
            return {"gas"}
        return {g for g in got if g != "oil"} | ({"other"} if "oil" in got else set())
    # a part is split on the queues' own joiners: "+", "/", a backslash and " - "
    pieces = [p.strip() for chunk in t.replace(chr(92), "/").replace("/", "+").split("+") for p in chunk.split(" - ")]
    for i, piece in enumerate(pieces):
        if not piece:
            continue
        if i == 0 and piece in FAMILY_WORDS:   # SPP's "Hybrid - Solar/Storage", ERCOT's "Other - Battery ...": a family
            family = True                      # word first names no fuel; later ("Hybrid - Thermal/Storage") it is one
            continue
        words = piece.replace("(", " ").replace(")", " ").replace(",", " ").split()
        found = {part for part, keys in TECH_PART_WORDS.items()
                 for k in keys if (" " in k and k in piece) or (" " not in k and k in words)}
        parts |= found or {"other"}
    if not parts and family:        # "Thermal", "Hybrid", "Other - Other": something, not a fuel the groups name
        parts = {"other"}
    # ERCOT writes "<fuel> - <technology>": "Gas - Steam Turbine other than Combined-Cycle" is gas, whatever the rest says
    if t.startswith("gas - "):
        parts = {"gas"}
    return parts


def technology_group(text):
    parts = technology_parts(text)
    if not parts:
        return "not_stated"
    if parts == {"solar", "storage"}:
        return "solar_storage"
    if len(parts) == 1 and next(iter(parts)) in ("solar", "storage", "wind", "gas"):
        return next(iter(parts))
    return "other"


def rule_words(iso, variable):
    if variable.startswith("wait_") and iso in REQUESTED_COD:
        return "SPP's Commercial Operation Date, which may be the date requested rather than achieved"
    if variable.startswith("wait_"):
        return "queue date to in-service date, operating positions with both dates"
    if variable == "withdrawal_rate":
        return "withdrawn positions over positions entered"
    return "the queue connector's status (STATUS_MAP of warehouse/connectors/iso_queues.py)"


def restore_inputs(run=None):
    """Session 7015 (chain 301, done-line request 16): the queues are pulled by the GitHub runner on Mondays and reach the
    data machine only through the archive; on 16 November 2026 this machine's copies were of 19 October and 26 September
    while the archive held the pulls of 5 November, and the statistics stood at 21 October. Each table is rebuilt from the
    bucket into runs/queue_inputs; a table that cannot be rebuilt stops the build (nothing is built from a mix of dates)."""
    import subprocess
    run = run or subprocess.run
    out = os.path.join(ip.ROOT, "runs", "queue_inputs")
    os.makedirs(out, exist_ok=True)
    for iso in ISOS:
        name = f"{iso}_interconnection_queue"
        r = run([sys.executable, os.path.join(ip.ROOT, "warehouse", "archive", "restore.py"), name, "--from-bucket",
                 "--out", os.path.join(out, name + ".csv")], cwd=ip.ROOT)
        if r.returncode != 0:
            raise SystemExit(f"{name}: could not be rebuilt from the archive (restore.py exit {r.returncode}); nothing built")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Interconnection queue statistics by ISO and entry year (session 348)")
    ap.add_argument("--inputs", default=ip.OUT_DIR, help="the folder holding the <iso>_interconnection_queue.csv tables")
    ap.add_argument("--restore", action="store_true",
                    help="session 7015: first rebuild the six queue tables from the archive bucket (the runner's newest pulls) "
                         "into runs/queue_inputs and build from there; this machine's copies are not touched")
    a = ap.parse_args(argv)
    if a.restore:
        a.inputs = restore_inputs()
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = ip.Log(os.path.join(ip.LOG_DIR, f"{NAME}_{run_id}.log"))
    results = []
    try:
        recs, inputs, undated = [], [], {}
        for iso in ISOS:
            path = os.path.join(a.inputs, f"{iso}_interconnection_queue.csv")
            if not os.path.exists(path):
                raise RuntimeError(f"{path} is not on this machine")
            head = [line[2:].strip() for line in open(path, encoding="utf-8") if line.startswith("#")]
            run = next((h for h in head if h.startswith("Rebuilt from the ERW archive")), "")
            retrieved = next((h.split(":", 1)[1].strip() for h in head if h.startswith("Retrieved:")), "")
            stamp = retrieved.split(" ")[0]
            retrieved_iso = (dt.datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").strftime("%Y-%m-%dT%H:%M:%SZ") if len(stamp) == 16 else "")
            # session 367: the header is skipped by its count of lines (session 103's rule): comment="#" would cut a data row
            # at a "#" inside a cell (a project named "Unit #2"), and its later columns with it
            n_head = next(i for i, line in enumerate(open(path, encoding="utf-8")) if not line.startswith("#"))
            d = pd.read_csv(path, skiprows=n_head, low_memory=False, dtype=str)
            inputs.append(f"{iso}_interconnection_queue ({len(d)} rows; retrieved {retrieved.split(' ')[0]}"
                          + (f"; {run.split(';')[0].replace('Rebuilt from the ERW archive by warehouse/archive/restore.py, ', '')}" if run else "") + ")")
            d["year"] = pd.to_datetime(d["queue_date"], errors="coerce").dt.year
            undated[iso] = int(d["year"].isna().sum())
            d = d[d["year"].notna()]
            d["iso"] = iso
            d["tech"] = d["fuel_technology"].map(technology_group) if "fuel_technology" in d else "not_stated"
            for (i, y), q in d.groupby(["iso", "year"]):
                # the rows for all (entity <iso>:queue_<year>), then each technology group present that year (session
                # 7022: entity <iso>:tech_<group>:queue_<year>, outside the pages' reads of <iso>:queue_*)
                sets = [(f"{iso}:queue_{int(y)}", q, "")]
                sets += [(f"{iso}:tech_{g}:queue_{int(y)}", q[q["tech"] == g], g) for g in TECH_GROUPS if (q["tech"] == g).any()]
                for entity, qq, g in sets:
                    for var, (v, unit) in stats(qq, i).items():
                        rule = rule_words(iso, var) + (f"; technology group {g} ({TECH_RULE})" if g else "")
                        recs.append(dict(entity=entity, variable=var, ts_utc=f"{int(y)}-01-01T00:00:00Z",
                                         value=round(v, 6), unit=unit, freq="P1Y", geo="", market=f"{iso}_queue", node="",
                                         source="erw:iso_queue_statistics", source_url=METHOD_URL, retrieved_at=retrieved_iso,
                                         vintage="", x_iso=LABEL[iso], x_entry_year=str(int(y)), x_rule=rule,
                                         x_input_run=run.split(";")[0] if run else "warehouse/output"))
        df = pd.DataFrame(recs)
        if df.duplicated(ip.SERIES_KEY).any():
            raise RuntimeError("an (entity, variable, ts_utc) is given twice")
        cols = ip.SERIES_COLS + X_COLS
        header = [
            "Energy Research Warehouse (ERW): interconnection queue statistics by ISO and entry year (derived, session 348)",
            "Shape: series (docs/datastandard.md v0). entity <iso>:queue_<entry year>; variables positions_ and mw_ entered, withdrawn, "
            "operating, waiting and status_not_stated; withdrawal_rate; wait_positions, wait_years_median, wait_years_mean. Since session "
            "7022 the same by technology group, entity <iso>:tech_<group>:queue_<entry year>, group storage, solar, solar_storage, wind, "
            "gas, other or not_stated (the queue gives no technology), from the queue's fuel_technology; a group with no position in a "
            "year has no row",
            "Rules: docs/methods/energy_projects.md, Queue statistics: each ISO's own status words as warehouse/connectors/iso_queues.py "
            "maps them; the entry year is the year of the queue date; the wait runs from the queue date to the in-service date",
            "Not held: ERCOT's withdrawn positions (its GIS report lists active and completed only), so no ERCOT withdrawal rate; "
            "MISO's and ISO-NE's in-service dates, so no wait for them; SPP's wait reads its Commercial Operation Date, which may be requested, not achieved",
            "Positions with no queue date, counted in no year: " + ", ".join(f"{LABEL[k]} {v}" for k, v in undated.items()),
            "Derived from: " + "; ".join(f"{i}_interconnection_queue" for i in ISOS),
            "Inputs read: " + "; ".join(inputs),
            "Source: erw:iso_queue_statistics ERW derived table, " + METHOD_URL,
            "License: public. A derived table inherits the most restrictive license of its inputs (Decision 23)",
            f"Retrieved: {run_id} (UTC) by warehouse/derived/{NAME}.py",
            f"Run log: warehouse/output/logs/{NAME}_{run_id}.log",
        ]
        ip.write_snapshot(df[cols], NAME, header, log, cols)
        ip.update_sources([dict(source="erw:iso_queue_statistics", publisher="Energy Research Warehouse (ERW), derived",
                                report="Interconnection queue statistics by ISO and entry year (derived, session 348)",
                                report_url=METHOD_URL, document_list=METHOD_URL, license="public", tables=[NAME])])
        print(f"{NAME}: {len(df)} rows, {df['x_iso'].nunique()} ISOs, entry years {df['x_entry_year'].min()} to {df['x_entry_year'].max()}")
        log(f"wrote {len(df)} rows")
        results.append(dict(table=NAME, market="all", status="ok", detail=f"{len(df)} rows"))
    except Exception as exc:
        log(f"FAILED, no output file written: {type(exc).__name__}: {exc}")
        print(f"{NAME} FAILED, no output file written: {type(exc).__name__}: {exc}", file=sys.stderr)
        results.append(dict(table=NAME, market="all", status="failed", detail=str(exc)[:300]))
    ip.write_status(NAME, run_id, results)
    log.close()
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
