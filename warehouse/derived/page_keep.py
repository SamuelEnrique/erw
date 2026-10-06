#!/usr/bin/env python3
"""A scheduled refresh never makes a page worse (landing step of 6 October 2026, before session 135).

Energy Research Warehouse (ERW). The price board (/board) and Supply and trade (/supply) read files this repository
holds: site/data/board.json with site/public/board/, and site/data/supply.json. Their builders (board_page.py,
supply_page.py) rebuild those files whole from the tables in warehouse/output. On a data machine every table is
there. On the scheduled runner many are not: the long histories are never restored, and the hourly generation
workbooks live only on a data machine. Run there as they stand, the builders would write a board with shorter
histories and a supply page whose fuel burn reads "working on it".

This script runs a builder into a temporary folder and then takes the new build ROW BY ROW:

  1. A row the new build gives with a value is taken when its newest date is not earlier than the held row's and
     its history is not shorter (the board: the points of the row's series file, where a build with fewer than 98
     percent of the held points is shorter, since a rolling table gains and loses a day; supply: the points of the
     row's trend).
  2. Otherwise the held row is kept exactly as it was, with its own date on it, and counted as "kept".
  3. A row the new build blanks as "paused" or "licensed" is always taken: a pause is never undone by a kept row.
  4. A row only the held file has is kept; a row only the new build has is taken.
  5. The board's hourly files follow the same rule: taken when they reach at least as far back and as far forward.

Nothing is filled, joined or averaged: every row on the page is one build's row, whole. The counts are printed and
logged. Exit 0 when the files were written (even if every row was kept), 1 when the builder failed or nothing could
be read, in which case no file under site/ is touched. --replace writes the new build whole (a person's command, on
a data machine, after a change that removes rows on purpose).

    python warehouse/derived/page_keep.py board
    python warehouse/derived/page_keep.py supply [--no-burn]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE = os.path.join(ROOT, "site")
BLANKED_ON_PURPOSE = {"paused", "licensed"}
SHORTER = 0.98


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(body, f, separators=(",", ":"))
        f.write("\n")


def named(body):
    """The rows with their source written out, so rows of two builds can sit in one list."""
    sources = body.get("sources", [])
    return [dict(r, source=sources[r["source"]]) if isinstance(r.get("source"), int) else dict(r) for r in body["rows"]]


def newest(row):
    return (row.get("last") or {}).get("t") or ""


def choose(old, new, n_old, n_new):
    """Which build's row to show: 'new' or 'old', and why. n_*: the number of points in the row's history, or None."""
    if new is None:
        return "old", "only the held file has it"
    if old is None or old.get("status") != "ok":
        return "new", ""
    if new.get("status") in BLANKED_ON_PURPOSE:
        return "new", ""
    if new.get("status") != "ok":
        return "old", f"the new build has no value ({new.get('status')})"
    if newest(new) < newest(old):
        return "old", f"the new build ends earlier ({newest(new)} against {newest(old)})"
    if n_old and (not n_new or n_new < SHORTER * n_old):
        return "old", f"the new build's history is shorter ({n_new or 0} points against {n_old})"
    return "new", ""


def merge_rows(old_body, new_body, points_old, points_new, log):
    old_rows, new_rows = named(old_body), named(new_body)
    old_by = {r["id"]: r for r in old_rows}
    new_by = {r["id"]: r for r in new_rows}
    order = {g["id"]: i for i, g in enumerate(new_body["groups"])}
    out, kept, taken = [], [], []
    for r in new_rows:
        which, why = choose(old_by.get(r["id"]), r, points_old(r["id"]), points_new(r["id"]))
        if which == "new":
            out.append(r); taken.append(r["id"])
        else:
            out.append(old_by[r["id"]]); kept.append((r["id"], why))
    for r in old_rows:
        if r["id"] not in new_by and r.get("group") in order:
            out.append(r); kept.append((r["id"], "only the held file has it"))
    out.sort(key=lambda r: order[r["group"]])                      # stable: rows keep their order inside a group
    sources = sorted({r["source"] for r in out if isinstance(r.get("source"), str)})
    rows = [dict(r, source=sources.index(r["source"])) if isinstance(r.get("source"), str) else r for r in out]
    for rid, why in kept[:40]:
        log(f"  kept {rid}: {why}")
    if len(kept) > 40:
        log(f"  and {len(kept) - 40} more kept")
    return rows, sources, kept, taken


def run_builder(script, tmp, extra):
    cmd = [sys.executable, os.path.join(HERE, script), "--site-dir", tmp] + extra
    r = subprocess.run(cmd, cwd=ROOT)
    return r.returncode


def series_points(folder, rid):
    p = os.path.join(folder, rid + ".json")
    if not os.path.exists(p):
        return None
    try:
        return len(load(p).get("v") or [])
    except (OSError, ValueError):
        return None


def board(args, log):
    held_path = os.path.join(SITE, "data", "board.json")
    with tempfile.TemporaryDirectory(prefix="erw_board_") as tmp:
        if run_builder("board_page.py", tmp, []) != 0:
            log("the builder failed: site/ is untouched")
            return 1
        new_body = load(os.path.join(tmp, "data", "board.json"))
        s_new, h_new = os.path.join(tmp, "public", "board", "s"), os.path.join(tmp, "public", "board", "h")
        s_old, h_old = os.path.join(SITE, "public", "board", "s"), os.path.join(SITE, "public", "board", "h")
        if args.replace or not os.path.exists(held_path):
            old_body = dict(new_body, rows=[], sources=[])
        else:
            old_body = load(held_path)
        rows, sources, kept, taken = merge_rows(old_body, new_body, lambda i: series_points(s_old, i), lambda i: series_points(s_new, i), log)
        kept_ids = {i for i, _ in kept}
        for d in (s_old, h_old):
            os.makedirs(d, exist_ok=True)
        for rid in taken:                                              # a taken row brings its series file
            src = os.path.join(s_new, rid + ".json")
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(s_old, rid + ".json"))
            elif os.path.exists(os.path.join(s_old, rid + ".json")):
                os.remove(os.path.join(s_old, rid + ".json"))
        if args.replace:
            for old in os.listdir(s_old):
                if old.endswith(".json") and old[:-5] not in set(taken):
                    os.remove(os.path.join(s_old, old))
        hourly_kept = 0
        for name in sorted(f for f in os.listdir(h_new) if f.endswith(".json")):
            src, dst = os.path.join(h_new, name), os.path.join(h_old, name)
            if not args.replace and os.path.exists(dst):
                a, b = load(dst), load(src)
                if b.get("t0", 0) > a.get("t0", 0) or b.get("t0", 0) + b.get("n", 0) < a.get("t0", 0) + a.get("n", 0):
                    hourly_kept += 1
                    continue
            shutil.copyfile(src, dst)
        week = new_body.get("week") or old_body.get("week") or []
        spikes = new_body.get("spikes") or old_body.get("spikes") or []
        dump(held_path, dict(new_body, sources=sources, rows=rows, week=week, spikes=spikes))
        held = sum(1 for r in rows if r["status"] == "ok")
        line = f"board: {len(rows)} rows ({held} with values): {len(taken)} from this build, {len(kept_ids)} kept as they were; hourly files kept: {hourly_kept}"
        print(line); log(line)
    return 0


def supply(args, log):
    held_path = os.path.join(SITE, "data", "supply.json")
    with tempfile.TemporaryDirectory(prefix="erw_supply_") as tmp:
        if run_builder("supply_page.py", tmp, ["--no-burn"] if args.no_burn else []) != 0:
            log("the builder failed: site/ is untouched")
            return 1
        new_body = load(os.path.join(tmp, "data", "supply.json"))
        if args.replace or not os.path.exists(held_path):
            old_body = dict(new_body, rows=[], sources=[])
        else:
            old_body = load(held_path)

        def points(body):
            by = {r["id"]: r for r in body["rows"]}
            def f(rid):
                t = ((by.get(rid) or {}).get("spark") or {}).get("t")
                return (len(t) if isinstance(t, list) and t else None)
            return f
        rows, sources, kept, taken = merge_rows(old_body, new_body, points(old_body), points(new_body), log)
        dump(held_path, dict(new_body, sources=sources, rows=rows))
        held = sum(1 for r in rows if r["status"] == "ok")
        line = f"supply: {len(rows)} rows ({held} with values): {len(taken)} from this build, {len(kept)} kept as they were"
        print(line); log(line)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="run a page's builder and take its rows only where they are no worse than the held ones")
    ap.add_argument("page", choices=["board", "supply"])
    ap.add_argument("--no-burn", action="store_true", help="supply: this machine has no hourly generation workbooks")
    ap.add_argument("--replace", action="store_true", help="write the new build whole (a person's command)")
    args = ap.parse_args(argv)
    lines = []

    def log(s):
        lines.append(s)
        print(s, file=sys.stderr)
    rc = board(args, log) if args.page == "board" else supply(args, log)
    return rc


if __name__ == "__main__":
    sys.exit(main())
