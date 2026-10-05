"""Energy Research Warehouse (ERW): the table of known faults in source data (session 103).

  python warehouse/derived/data_faults.py                 # the table known_data_faults (under the data lock)
  python warehouse/derived/data_faults.py --snapshot      # and the site's copy, site/data/data_faults.json
  python warehouse/derived/data_faults.py --out-dir DIR   # a trial: the table under DIR, nothing in warehouse/output

Input: warehouse/faults/faults.yaml, the register a person or a session writes: one entry per fault a publisher's
data holds, with its evidence, its dates, the tables it touches and what the ERW does about it. This script checks
the register and writes it as a table; it computes nothing and requests nothing.

Checks (the build fails on any):
  - every entry has an id (unique), a title, a publisher, a source that is in the source registry, a status of the
    four allowed, evidence, what the ERW does, and where it is recorded;
  - first and last are dates (YYYY-MM-DD) or empty, and first is not after last;
  - every table named is a table of the warehouse (in coverage.csv);
  - no em dash.

Output: known_data_faults, events shape (docs/datastandard.md), one row per fault.
  event_id    data_fault:<id>
  event_date  the first day of the fault where a day is recorded; where none is, the day the register recorded it
              (x_first is then empty and x_dates_note says what is known)
  event_type  data_fault
  parties     the publisher
  entity_ids  the tables it touches, separated by ";"
  status      screened, corrected, worked_around or held_as_published
  x_title, x_first, x_last, x_dates_note, x_publisher_source, x_evidence, x_erw_does, x_open, x_recorded_in
Method: docs/methods/known_data_faults.md.
"""
import argparse
import json
import os
import re
import sys

import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

NAME = "known_data_faults"
SOURCE = "erw:known_data_faults"
METHOD_URL = "https://github.com/SamuelEnrique/erw/blob/main/docs/methods/known_data_faults.md"
REGISTER = os.path.join(ROOT, "warehouse", "faults", "faults.yaml")
SITE_FILE = os.path.join(ROOT, "site", "data", "data_faults.json")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")
SOURCES = os.path.join(ROOT, "warehouse", "metadata", "sources.csv")
EVENT_COLS = ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"]
EXTRA = ["x_title", "x_first", "x_last", "x_dates_note", "x_publisher_source", "x_evidence", "x_erw_does", "x_open", "x_recorded_in",
         "x_resolution", "x_resolution_reason", "retrieved_at"]
STATUSES = ("screened", "corrected", "worked_around", "held_as_published")
STATUS_WORDS = {"screened": "left out by a stated rule", "corrected": "read as it should have been, by a stated rule",
                "worked_around": "another source is read for the period", "held_as_published": "held as the publisher gave it"}
# Session 118: where the ERW's own work on a fault stands. `status` says what the ERW does with the values; this says
# whether that work is done, done and waiting for a person, or not done.
RESOLUTIONS = ("fixed", "held_for_approval", "open")
RESOLUTION_WORDS = {
    "fixed": "no ERW table or page shows or computes a wrong figure from it; where the fault is a gap, the gap is stated and nothing is filled",
    "held_for_approval": "the fix is built and waits for a person, because applying it moves a number on a live page",
    "open": "something is still to do or to rule on, or cannot be done from these data; the reason says which"}
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUIRED = ("id", "title", "publisher", "source", "status", "evidence", "erw_does", "recorded_in", "resolution", "resolution_reason")


def flat(v):
    """One line of text: a folded YAML block comes with line breaks inside it."""
    return " ".join(str(v if v is not None else "").split())


def read_register(path=REGISTER):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if chr(0x2014) in text:
        raise ValueError(f"{path} holds an em dash")
    return yaml.safe_load(text)["faults"]


def check(faults, tables, sources):
    """Every problem of the register, as a list of sentences (empty when it is sound)."""
    bad, seen = [], set()
    for i, f in enumerate(faults):
        fid = flat(f.get("id")) or f"entry {i + 1}"
        for k in REQUIRED:
            if not flat(f.get(k)):
                bad.append(f"{fid}: no {k}")
        if fid in seen:
            bad.append(f"{fid}: the id is used twice")
        seen.add(fid)
        if not re.match(r"^[a-z0-9_]+$", fid):
            bad.append(f"{fid}: an id is lower-case letters, digits and underscores")
        if flat(f.get("status")) not in STATUSES:
            bad.append(f"{fid}: status {f.get('status')!r} is not one of {', '.join(STATUSES)}")
        if flat(f.get("resolution")) not in RESOLUTIONS:
            bad.append(f"{fid}: resolution {f.get('resolution')!r} is not one of {', '.join(RESOLUTIONS)}")
        if flat(f.get("source")) and flat(f.get("source")) not in sources:
            bad.append(f"{fid}: source {f.get('source')!r} is not in the source registry")
        first, last = flat(f.get("first")), flat(f.get("last"))
        for k, v in (("first", first), ("last", last)):
            if v and not (DAY.match(v) and not pd.isna(pd.to_datetime(v, errors="coerce"))):
                bad.append(f"{fid}: {k} {v!r} is not a date YYYY-MM-DD")
        if first and last and first > last:
            bad.append(f"{fid}: first {first} is after last {last}")
        if not first and not flat(f.get("dates_note")):
            bad.append(f"{fid}: no first day and no dates_note saying what is known")
        for t in [t.strip() for t in flat(f.get("tables")).split(";") if t.strip()]:
            if t not in tables:
                bad.append(f"{fid}: {t} is not a table of the warehouse")
    return bad


def rows_of(faults, retrieved, today):
    out = []
    for f in faults:
        first, last = flat(f.get("first")), flat(f.get("last"))
        out.append(dict(
            event_id=f"data_fault:{flat(f['id'])}", event_date=first or today, event_type="data_fault", parties=flat(f["publisher"]),
            entity_ids=";".join(t.strip() for t in flat(f.get("tables")).split(";") if t.strip()), mw="", price="", currency="",
            status=flat(f["status"]), source=SOURCE, source_url=METHOD_URL, x_title=flat(f["title"]), x_first=first, x_last=last,
            x_dates_note=flat(f.get("dates_note")), x_publisher_source=flat(f["source"]), x_evidence=flat(f["evidence"]),
            x_erw_does=flat(f["erw_does"]), x_open=flat(f.get("open")), x_recorded_in=flat(f["recorded_in"]),
            x_resolution=flat(f["resolution"]), x_resolution_reason=flat(f["resolution_reason"]), retrieved_at=retrieved))
    return pd.DataFrame(out, columns=EVENT_COLS + EXTRA)


def site_copy(t, built):
    """What the page reads: the rows, newest first day first, and the counts it states."""
    rows = [dict(id=r["event_id"].split(":", 1)[1], title=r["x_title"], publisher=r["parties"], source=r["x_publisher_source"], first=r["x_first"],
                 last=r["x_last"], dates_note=r["x_dates_note"], status=r["status"], tables=[x for x in r["entity_ids"].split(";") if x],
                 evidence=r["x_evidence"], erw_does=r["x_erw_does"], open=r["x_open"], recorded_in=r["x_recorded_in"],
                 resolution=r["x_resolution"], resolution_reason=r["x_resolution_reason"])
            for r in t.to_dict("records")]
    by_status = {s: int((t["status"] == s).sum()) for s in STATUSES}
    by_resolution = {s: int((t["x_resolution"] == s).sum()) for s in RESOLUTIONS}
    tables = sorted({x for r in rows for x in r["tables"]})
    return {"table": NAME, "built": built, "faults": len(rows), "by_status": by_status, "status_words": STATUS_WORDS,
            "by_resolution": by_resolution, "resolution_words": RESOLUTION_WORDS,
            "tables_touched": len(tables), "with_open": int((t["x_open"] != "").sum()), "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW known data faults: the register as a table")
    ap.add_argument("--out-dir", help="a trial run: the table and its log under this directory; nothing in warehouse/output")
    ap.add_argument("--snapshot", action="store_true", help="also write the site's copy (site/data/data_faults.json)")
    a = ap.parse_args(argv)
    faults = read_register()
    tables = set(pd.read_csv(COVERAGE, dtype=str, keep_default_na=False)["table"])
    sources = set(pd.read_csv(SOURCES, dtype=str, keep_default_na=False)["source"])
    bad = check(faults, tables, sources)
    if bad:
        print("FAILED: the register is not sound; nothing written:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1
    now = pd.Timestamp.now(tz="UTC")
    run_id, retrieved = now.strftime("%Y%m%dT%H%M%SZ"), ip.utc_iso(now)
    t = rows_of(faults, retrieved, now.strftime("%Y-%m-%d"))
    if a.out_dir:
        ip.set_out_dir(a.out_dir)
    log_dir = os.path.join(ip.OUT_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log = ip.Log(os.path.join(log_dir, f"data_faults_{run_id}.log"))
    log(f"data_faults.py: {len(t)} faults from {os.path.relpath(REGISTER, ROOT).replace(os.sep, '/')}")
    target = os.path.join(ip.OUT_DIR, NAME + ".csv")
    if os.path.exists(target):
        ip._require_lock(target, f"rebuilding {NAME}")
        os.remove(target)  # rebuilt whole from the register each run: an entry taken out of the register leaves the table
    counts = ", ".join(f"{int((t['status'] == s).sum())} {s}" for s in STATUSES)
    ip.write_csv(t, NAME, [
        "Energy Research Warehouse (ERW): known faults in source data, one row per fault (session 103)",
        "Shape: events (docs/datastandard.md v0). event_date: the first day of the fault where a day is recorded; where none is, the day the register "
        "recorded it (x_first is then empty and x_dates_note says what is known). parties: the publisher. entity_ids: the ERW tables it touches. "
        "status: screened (left out by a stated rule), corrected (read as it should have been), worked_around (another source is read for the period) "
        "or held_as_published. x_evidence: what was measured, in the words of the session that measured it. x_erw_does, x_open, x_recorded_in. "
        "x_resolution (session 118): fixed, held_for_approval (the fix is built and waits for a person because it moves a number on a live page) "
        "or open, with x_resolution_reason.",
        f"Counts: {len(t)} faults: {counts}. Every figure is one a session measured and recorded; nothing is estimated.",
        f"Retrieved: {run_id} (UTC) by warehouse/derived/data_faults.py", f"Run log: warehouse/output/logs/data_faults_{run_id}.log",
        f"Source: {SOURCE} the ERW's register of faults found in its sources' data (warehouse/faults/faults.yaml), each entry naming where it is recorded",
        "License: public. The ERW's own account of its sources' data; each row names the publisher and the source report.",
    ], log, cols=EVENT_COLS + EXTRA, key=["event_id"], time_col="event_date")
    ip.update_sources([dict(source=SOURCE, publisher="Energy Research Warehouse (ERW), derived",
                            report="Known faults in source data: the register of what each publisher's data holds that is wrong, missing, shifted or impossible (docs/methods/known_data_faults.md)",
                            report_url=METHOD_URL, document_list="docs/methods/known_data_faults.md", license="public", tables=[NAME])])
    if a.snapshot:
        with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(site_copy(t.sort_values(["event_date", "event_id"], ascending=[False, True]), retrieved), f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    log.close()
    print(f"{NAME}: {len(t)} faults ({counts})" + ("; the site's copy written" if a.snapshot else "") + (f" (trial, under {a.out_dir})" if a.out_dir else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
