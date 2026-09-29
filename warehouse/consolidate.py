#!/usr/bin/env python3
"""Consolidated tables: one table per family, the partition in a column (session 29).

Energy Research Warehouse (ERW). Ben Domingue's review (docs/feedback/ben-2026-09-28.md, item 5):
one table per ERCOT year, per EIA-930 balancing authority and per ISO put the ERW at 113 tables
in four days, against Redivis's cap of 1,000 per dataset. Session 29 folds each family whose
members share their columns and differ only by a value in the table name into one table, with
that value in a column (docs/migrations/2026-09-29-consolidation.md). The map, old table to new
table and partition, is warehouse/metadata/table_migrations.csv; it is the one place that says it.

The connectors are unchanged: they still read and write the members (ercot_dam_hub_prices,
eia930_ciso_demand, ...), which are working files between the two steps of the daily run:

    python warehouse/consolidate.py split     # after the restore: members from the consolidated tables
    python warehouse/consolidate.py build     # after the last connector: consolidated tables from the members
    python warehouse/consolidate.py build --family iso_trader_daily
    python warehouse/consolidate.py check     # every consolidated table against its members (counts, columns)

build writes each consolidated table from its members in warehouse/output (a member not there is
carried from the consolidated table as it was), checks that its rows are the sum of its members'
and that a member's existing partition column holds its value on every row, and moves the members
to warehouse/output/members/, where nothing downstream (validator, coverage, archive, Supabase,
Redivis) looks. split writes the members back from the consolidated table, each with its own
provenance header, which the consolidated header keeps verbatim ("Member <table>: ..." lines).
A member file newer than its consolidated table (a run stopped between the steps) is left alone.

Tables are streamed a member or a chunk at a time, never a whole large family in one frame (the
ERCOT history is about three million rows). Exit 1 if any family fails; a failed family's members
stay in warehouse/output, so the validator and the uploader see them and nothing is lost.
"""

import argparse
import csv
import io
import json
import os
import re
import shutil
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "warehouse", "output")
STAGE = os.path.join(OUT, "members")
MAP = os.path.join(ROOT, "warehouse", "metadata", "table_migrations.csv")
SPLIT_RECORD = os.path.join(STAGE, "_split.json")  # the members split wrote: size and mtime, so build skips unchanged
CHUNK = 250_000

TITLES = {
    "iso_trader_daily": "the trader view, daily metrics per hub, every ISO (derived; platform tool 24)",
    "eia930_all_demand": "EIA-930 hourly demand and day-ahead demand forecast, every balancing authority",
    "eia930_all_generation": "EIA-930 hourly net generation, total and by energy source, every balancing authority",
    "iso_dam_hub_prices": "day-ahead hub prices, CAISO, ERCOT, MISO and SPP",
    "iso_rtm_hub_prices": "real-time hub prices, CAISO, ERCOT, MISO and SPP",
    "ercot_all_hub_prices_history": "ERCOT trading hub prices, day-ahead and real-time, one row per interval "
                                    "of each operating year from 2015 (the yearly history)",
}


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- the map

def read_map():
    """{new: [(old, {column: value}), ...]} in the map's order."""
    fam = {}
    with open(MAP, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            part = dict(kv.split("=", 1) for kv in r["partition"].split(";") if kv)
            fam.setdefault(r["new_table"], []).append((r["old_table"], part))
    return fam


def added_columns(members):
    """Partition columns a family adds (not in its members): the same for every member."""
    return [c for c in members[0][1] if c != "market"]


def migrations():
    """{old: (new, partition)} for every migrated table (the erw package and restore read this too)."""
    return {old: (new, part) for new, ms in read_map().items() for old, part in ms}


# ---------------------------------------------------------------- files

def split_file(path):
    """(header lines without '# ', number of comment lines, column names)."""
    header = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                header.append(line.rstrip("\r\n")[2:] if line.startswith("# ") else line.rstrip("\r\n")[1:])
                continue
            cols = next(csv.reader([line]))
            return header, len(header), cols
    raise ValueError(f"{path}: no column row")


def read_member(path, n):
    return pd.read_csv(path, skiprows=n, dtype=str, keep_default_na=False, na_values=[])


def member_blocks(header):
    """{member: its header lines} from a consolidated header's 'Member <table>: ' lines."""
    out = {}
    for h in header:
        m = re.match(r"^Member ([a-z0-9_]+): (.*)$", h)
        if m:
            out.setdefault(m.group(1), []).append(m.group(2))
    return out


def compose_header(new, members, headers, rows, cols):
    """The consolidated table's header: its own lines, then every member's header verbatim."""
    migrated = migrations()
    part_cols = list(members[0][1])
    runs = []
    for old, _ in members:
        for h in headers.get(old, []):
            m = re.search(r"Retrieved: (\d{8}T\d{6}Z)", h)
            if m:
                runs.append((m.group(1), old))
                break
    newest, newest_member = max(runs) if runs else ("", None)
    run_log = next((h for h in headers.get(newest_member, []) if h.startswith("Run log:")), None)
    sources, seen = [], set()
    for old, _ in members:
        block = headers.get(old, [])
        for i, h in enumerate(block):
            if h.startswith("Source:") and h not in seen:
                seen.add(h)
                sources.append(h)
                j = i + 1
                while j < len(block) and block[j].startswith("  "):
                    sources.append(block[j])
                    j += 1
    derived = []
    for old, _ in members:
        for h in headers.get(old, []):
            if h.startswith("Derived from:"):
                for t in h.split(":", 1)[1].split(";"):
                    t = migrated.get(t.strip(), (t.strip(),))[0]
                    if t and t not in derived:
                        derived.append(t)
    licenses = {m.group(1) for old, _ in members for h in headers.get(old, [])
                for m in [re.match(r"License: (public|internal)[.\s]", h + " ")] if m}
    lines = [f"Energy Research Warehouse (ERW): {TITLES.get(new, new)}",
             "Shape: series (docs/datastandard.md v0), a consolidated table (session 29): the "
             f"{len(members)} tables it replaced are its rows, told apart by the partition column"
             f"{'s' if len(part_cols) > 1 else ''} {', '.join(part_cols)} "
             "(docs/migrations/2026-09-29-consolidation.md; the map is warehouse/metadata/table_migrations.csv). "
             "ts_utc is interval start, UTC.",
             f"Retrieved: {newest} (UTC), the newest retrieval of its members ({newest_member}); each member's own "
             "header follows below, and per row, source, source_url and retrieved_at say where it came from."
             if newest else "Retrieved: see each member's header below"]
    if run_log:
        lines.append(run_log)
    lines += sources
    if derived:
        lines.append("Derived from: " + "; ".join(derived))
    if len(licenses) == 1:
        lines.append(f"License: {licenses.pop()}. Every member declares it.")
    lines.append(f"File holds {rows} rows, the sum of its members' rows. Columns: {', '.join(cols)}. "
                 "Written by warehouse/consolidate.py build from the members the connectors write.")
    for old, part in members:
        lines.append(f"Member {old}: " + "; ".join(f"{k}={v}" for k, v in part.items())
                     + " (its rows; its own provenance header follows)")
        lines += [f"Member {old}: {h}" for h in headers.get(old, [])]
    return lines


def write_header(f, lines):
    for h in lines:
        f.write(f"# {h}\n")


# ---------------------------------------------------------------- build

def build_family(new, members, src=None):
    """Write one consolidated table from its members in src (warehouse/output, or the members rebuilt from the
    archive by `migrate`). Returns (rows, {member: rows}) or None if no member is there."""
    src = src or OUT
    here = [old for old, _ in members if os.path.exists(os.path.join(src, old + ".csv"))]
    if not here:
        log(f"{new}: no member in warehouse/output; left as it is")
        return None
    cons = os.path.join(OUT, new + ".csv")
    prev = split_file(cons) if os.path.exists(cons) else None
    absent = [old for old, _ in members if old not in here]
    if absent and prev is None:
        raise RuntimeError(f"members {absent} are not in warehouse/output and there is no {new}.csv to carry "
                           "them from; not built (restore the consolidated table first)")
    rec = _split_record()
    if prev is not None and not absent and src == OUT and all(rec.get(old) == _stamp(os.path.join(OUT, old + ".csv"))
                                                              for old in here):
        # every member is as split wrote it from this table: nothing to rebuild (the ERCOT history, most days)
        os.makedirs(STAGE, exist_ok=True)
        for old in here:
            os.replace(os.path.join(OUT, old + ".csv"), os.path.join(STAGE, old + ".csv"))
        log(f"{new}: unchanged since the split ({len(here)} members as split wrote them); not rewritten")
        return None
    add = added_columns(members)
    headers, base = {}, None
    for old in here:
        h, _, cols = split_file(os.path.join(src, old + ".csv"))
        headers[old] = h
        if base is None:
            base = cols
        elif cols != base:
            raise RuntimeError(f"{old}: columns {cols} differ from {here[0]}'s {base}; not built")
    if prev is not None:
        blocks = member_blocks(prev[0])
        for old in absent:
            headers[old] = [h for h in blocks.get(old, []) if not h.endswith("(its rows; its own provenance header follows)")]
        if prev[2] != base + add:
            raise RuntimeError(f"{new}.csv has columns {prev[2]}, the members give {base + add}; not built")
    cols = base + add
    counts = {}
    tmp = cons + ".tmp"
    body = tmp + ".body"
    with open(body, "w", encoding="utf-8", newline="") as out:
        out.write(",".join(cols) + "\n")
        for old, part in members:
            if old in here:
                _, n, _ = split_file(os.path.join(src, old + ".csv"))
                frames = [read_member(os.path.join(src, old + ".csv"), n)]
            else:  # carried from the consolidated table as it was
                frames = (c[_matches(c, part)].drop(columns=[]) for c in
                          pd.read_csv(cons, skiprows=prev[1], dtype=str, keep_default_na=False, na_values=[],
                                      chunksize=CHUNK))
            k = 0
            for df in frames:
                if old in here:
                    if "market" in part and len(df) and set(df["market"]) != {part["market"]}:
                        raise RuntimeError(f"{old}: market column holds {sorted(set(df['market']))[:5]}, "
                                           f"the map says {part['market']}; not built")
                    for c in add:
                        df[c] = part[c]
                df[cols].to_csv(out, index=False, header=False, lineterminator="\n")
                k += len(df)
            counts[old] = k
    total = sum(counts.values())
    with open(tmp, "w", encoding="utf-8", newline="") as out:
        write_header(out, compose_header(new, members, headers, total, cols))
        with open(body, encoding="utf-8") as b:
            shutil.copyfileobj(b, out, 1 << 20)
    os.remove(body)
    # reconcile before replacing anything: rows written == rows read, per member
    got = sum(1 for _ in _data_lines(tmp))
    if got != total:
        os.remove(tmp)
        raise RuntimeError(f"{new}: wrote {got:,} rows, read {total:,}; not replaced")
    os.replace(tmp, cons)
    os.makedirs(STAGE, exist_ok=True)
    for old in here:  # the working copies leave warehouse/output (from src, or from warehouse/output after a migrate)
        p = os.path.join(OUT, old + ".csv")
        if os.path.exists(p):
            os.replace(p, os.path.join(STAGE, old + ".csv"))
    log(f"built {new}: {total:,} rows = " + " + ".join(f"{old} {counts[old]:,}" for old, _ in members)
        + (f" (carried from the table as it was: {', '.join(absent)})" if absent else ""))
    return total, counts


def _stamp(path):
    st = os.stat(path)
    return [st.st_size, st.st_mtime_ns]


def _split_record():
    if os.path.exists(SPLIT_RECORD):
        with open(SPLIT_RECORD, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _matches(df, part):
    keep = pd.Series(True, index=df.index)
    for c, v in part.items():
        keep &= df[c] == v
    return keep


def _data_lines(path):
    """The data lines of a CSV (quoted newlines respected), after its comment lines and column row."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        rd = csv.reader(lines)
        next(rd)
        yield from rd


# ---------------------------------------------------------------- split

def split_family(new, members):
    """Write the members of one consolidated table back to warehouse/output. Returns {member: rows} or None."""
    cons = os.path.join(OUT, new + ".csv")
    if not os.path.exists(cons):
        log(f"{new}: not in warehouse/output; no members written")
        return None
    header, n, cols = split_file(cons)
    blocks = member_blocks(header)
    add = added_columns(members)
    base = [c for c in cols if c not in add]
    t_cons = os.path.getmtime(cons)
    todo, kept = [], []
    for old, part in members:
        p = os.path.join(OUT, old + ".csv")
        if os.path.exists(p) and os.path.getmtime(p) > t_cons:
            kept.append(old)  # newer than the consolidated table: a run stopped between split and build
        else:
            todo.append((old, part))
    files, counts = {}, {old: 0 for old, _ in todo}
    try:
        for old, _ in todo:
            f = open(os.path.join(OUT, old + ".csv.tmp"), "w", encoding="utf-8", newline="")
            write_header(f, [h for h in blocks.get(old, [])
                             if not h.endswith("(its rows; its own provenance header follows)")])
            f.write(",".join(base) + "\n")
            files[old] = f
        for df in pd.read_csv(cons, skiprows=n, dtype=str, keep_default_na=False, na_values=[], chunksize=CHUNK):
            for old, part in todo:
                sel = df[_matches(df, part)]
                if len(sel):
                    sel[base].to_csv(files[old], index=False, header=False, lineterminator="\n")
                    counts[old] += len(sel)
    finally:
        for f in files.values():
            f.close()
    rec = _split_record()
    for old, _ in todo:
        tmp = os.path.join(OUT, old + ".csv.tmp")
        if counts[old] == 0:
            os.remove(tmp)
            continue
        os.replace(tmp, os.path.join(OUT, old + ".csv"))
        rec[old] = _stamp(os.path.join(OUT, old + ".csv"))
    os.makedirs(STAGE, exist_ok=True)
    with open(SPLIT_RECORD, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=0, sort_keys=True)
    log(f"split {new}: " + ", ".join(f"{old} {counts[old]:,}" for old, _ in todo)
        + (f"; kept (newer than {new}.csv): {', '.join(kept)}" if kept else ""))
    return counts


# ---------------------------------------------------------------- check

def check_family(new, members):
    """Counts per partition value of a consolidated table, against its members in warehouse/output/members/."""
    cons = os.path.join(OUT, new + ".csv")
    if not os.path.exists(cons):
        return [f"{new}: not in warehouse/output"]
    header, n, cols = split_file(cons)
    per = {old: 0 for old, _ in members}
    for df in pd.read_csv(cons, skiprows=n, dtype=str, keep_default_na=False, na_values=[], chunksize=CHUNK):
        for old, part in members:
            per[old] += int(_matches(df, part).sum())
    msgs = []
    total = sum(per.values())
    rows = sum(1 for _ in _data_lines(cons))
    if total != rows:
        msgs.append(f"{new}: {rows:,} rows, of which {total:,} belong to a member")
    for old, _ in members:
        p = next((q for q in (os.path.join(STAGE, old + ".csv"), os.path.join(OUT, old + ".csv")) if os.path.exists(q)), None)
        if p is None:
            continue
        m = sum(1 for _ in _data_lines(p))
        if m != per[old]:
            msgs.append(f"{new}: {old} has {per[old]:,} rows here, {m:,} in {os.path.relpath(p, ROOT)}")
    log(f"{'MISMATCH' if msgs else 'ok      '} {new}: {rows:,} rows, " + ", ".join(f"{o} {c:,}" for o, c in per.items()))
    return msgs


# ---------------------------------------------------------------- migrate (session 29, once)

def migrate_family(new, members, work):
    """Session 29 Part C: build a consolidated table from the ARCHIVE, not from warehouse/output: each member is
    rebuilt from its archived lines (warehouse/archive/restore.py), checked against its working copy in
    warehouse/output (values as the archive compares them, retrieved_at left out) and the row count its last
    archive run recorded, and only then consolidated. Returns the build's (rows, counts)."""
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "archive"))
    import restore
    os.makedirs(work, exist_ok=True)
    for old, _ in members:
        header, df, expected = restore.rebuild(old)
        msgs = restore.check(old, df, expected)
        if msgs:
            raise RuntimeError(f"{old}: the archive's rebuild differs from warehouse/output: {'; '.join(msgs)}; "
                               "family left unconsolidated")
        with open(os.path.join(work, old + ".csv"), "w", encoding="utf-8", newline="") as f:
            write_header(f, header)
            df.to_csv(f, index=False, lineterminator="\n")
        log(f"  {old}: {len(df):,} rows rebuilt from the archive (the run recorded {expected:,}), equal to warehouse/output")
        del df
    return build_family(new, members, src=work)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW consolidated tables (session 29)")
    ap.add_argument("command", choices=["build", "split", "check", "migrate"])
    ap.add_argument("--work", default=os.path.join(ROOT, "runs", "consolidation"),
                    help="migrate: where the members rebuilt from the archive are written")
    ap.add_argument("--family", action="append", metavar="NEW_TABLE", help="only these consolidated tables")
    args = ap.parse_args(argv)
    fams = read_map()
    names = args.family or list(fams)
    unknown = [n for n in names if n not in fams]
    if unknown:
        ap.error(f"not a consolidated table: {unknown}; see {os.path.relpath(MAP, ROOT)}")
    failed = []
    for new in names:
        try:
            if args.command == "build":
                build_family(new, fams[new])
            elif args.command == "split":
                split_family(new, fams[new])
            elif args.command == "migrate":
                migrate_family(new, fams[new], os.path.join(args.work, new))
            elif check_family(new, fams[new]):
                failed.append(new)
        except Exception as exc:
            failed.append(new)
            log(f"FAILED {args.command} {new}: {type(exc).__name__}: {exc}")
    log(f"consolidate {args.command}: {len(names) - len(failed)} of {len(names)} families"
        + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
